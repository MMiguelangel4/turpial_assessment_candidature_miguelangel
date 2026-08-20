import { describe, expect, it } from "vitest";
import {
  moneyEquals,
  postingSum,
  receivableDelta,
  reconcileStatement,
} from "../statement";
import type { StatementLine } from "../types";

const disbursement: StatementLine = {
  id: 1,
  memo: "Disbursement of loan #1",
  effective_on: "2026-01-05",
  postings: [
    { id: 1, account_kind: "principal_receivable", amount: "10000.00" },
    { id: 2, account_kind: "fees_receivable", amount: "150.00" },
    { id: 3, account_kind: "cash", amount: "-10150.00" },
  ],
};

const repayment: StatementLine = {
  id: 2,
  memo: "Repayment on loan #1",
  effective_on: "2026-02-05",
  postings: [
    { id: 4, account_kind: "cash", amount: "500.00" },
    { id: 5, account_kind: "fees_receivable", amount: "-150.00" },
    { id: 6, account_kind: "interest_receivable", amount: "-100.00" },
    { id: 7, account_kind: "principal_receivable", amount: "-250.00" },
  ],
};

describe("postingSum", () => {
  it("is zero for a balanced transaction", () => {
    expect(postingSum(disbursement.postings)).toBe(0);
  });
});

describe("receivableDelta", () => {
  it("ignores cash and sums receivables", () => {
    expect(receivableDelta(disbursement.postings)).toBe(10150);
    expect(receivableDelta(repayment.postings)).toBe(-500);
  });
});

describe("reconcileStatement", () => {
  it("builds a running outstanding from receivable deltas", () => {
    const result = reconcileStatement([disbursement, repayment]);
    expect(result.rows).toHaveLength(2);
    expect(result.rows[0].balance).toBe("10150.00");
    expect(result.rows[1].delta).toBe("-500.00");
    expect(result.rows[1].balance).toBe("9650.00");
    expect(result.derivedOutstanding).toBe("9650.00");
    expect(result.allBalanced).toBe(true);
  });

  it("flags a transaction whose postings do not sum to zero", () => {
    const broken: StatementLine = {
      id: 9,
      memo: "Broken",
      effective_on: "2026-01-01",
      postings: [
        { id: 1, account_kind: "principal_receivable", amount: "100.00" },
        { id: 2, account_kind: "cash", amount: "-99.00" },
      ],
    };
    const result = reconcileStatement([broken]);
    expect(result.rows[0].balanced).toBe(false);
    expect(result.allBalanced).toBe(false);
  });
});

describe("moneyEquals", () => {
  it("compares to the cent", () => {
    expect(moneyEquals("9650", "9650.00")).toBe(true);
    expect(moneyEquals("9650.00", "9650.01")).toBe(false);
  });
});
