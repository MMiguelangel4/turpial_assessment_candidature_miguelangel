import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import LoanStatement from "../components/LoanStatement.vue";

vi.mock("../api/loans", () => ({
  getLoan: vi.fn(async () => ({
    id: 1,
    borrower: "Rosa Delgado",
    principal: "10000.00",
    annual_rate: "0.1200",
    fees: "150.00",
    opened_on: "2026-01-05",
    outstanding: "9650.00",
  })),
  getStatement: vi.fn(async () => [
    {
      id: 1,
      memo: "Disbursement of loan #1",
      effective_on: "2026-01-05",
      postings: [
        { id: 1, account_kind: "principal_receivable", amount: "10000.00" },
        { id: 2, account_kind: "fees_receivable", amount: "150.00" },
        { id: 3, account_kind: "cash", amount: "-10150.00" },
      ],
    },
    {
      id: 2,
      memo: "Repayment on loan #1",
      effective_on: "2026-02-05",
      postings: [
        { id: 4, account_kind: "cash", amount: "500.00" },
        { id: 5, account_kind: "fees_receivable", amount: "-150.00" },
        { id: 6, account_kind: "interest_receivable", amount: "-100.00" },
        { id: 7, account_kind: "principal_receivable", amount: "-250.00" },
      ],
    },
  ]),
}));

const stubs = { RouterLink: { template: "<a><slot /></a>" } };

afterEach(() => vi.clearAllMocks());

describe("LoanStatement", () => {
  it("renders running balances from the statement", async () => {
    const wrapper = mount(LoanStatement, {
      props: { id: "1" },
      global: { stubs },
    });
    await flushPromises();

    expect(wrapper.text()).toContain("Rosa Delgado");
    expect(wrapper.text()).toContain("Disbursement of loan #1");
    expect(wrapper.text()).toContain("10,150.00");
    expect(wrapper.text()).toContain("9,650.00");
    expect(wrapper.findAll("tbody tr")).toHaveLength(2);
  });
});
