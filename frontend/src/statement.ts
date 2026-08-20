/**
 * Reconcile a loan statement from raw ledger transactions.
 *
 * Outstanding for the borrower = sum of receivable postings (not cash).
 * See GLOSSARY.md: balance is derived; debit +, credit −.
 */
import type { Posting, StatementLine } from "./types";

const RECEIVABLE_KINDS = new Set([
  "principal_receivable",
  "interest_receivable",
  "fees_receivable",
]);

export interface StatementRow {
  id: number;
  memo: string;
  effective_on: string;
  /** Net change to what the borrower owes (receivables only). */
  delta: string;
  /** Running outstanding after this line. */
  balance: string;
  /** True when this transaction's postings sum to zero. */
  balanced: boolean;
  postings: Posting[];
}

export interface ReconciledStatement {
  rows: StatementRow[];
  /** Final outstanding derived from the statement. */
  derivedOutstanding: string;
  /** True if every transaction's postings sum to zero. */
  allBalanced: boolean;
}

function roundCents(n: number): number {
  return Math.round(n * 100) / 100;
}

function toMoney(n: number): string {
  return roundCents(n).toFixed(2);
}

/** Sum of signed posting amounts (double-entry check: must be 0). */
export function postingSum(postings: Posting[]): number {
  return roundCents(
    postings.reduce((acc, p) => acc + Number(p.amount), 0),
  );
}

/** Change to borrower outstanding from one transaction. */
export function receivableDelta(postings: Posting[]): number {
  return roundCents(
    postings
      .filter((p) => RECEIVABLE_KINDS.has(p.account_kind))
      .reduce((acc, p) => acc + Number(p.amount), 0),
  );
}

export function reconcileStatement(lines: StatementLine[]): ReconciledStatement {
  let running = 0;
  let allBalanced = true;
  const rows: StatementRow[] = [];

  for (const line of lines) {
    const delta = receivableDelta(line.postings);
    const balanced = postingSum(line.postings) === 0;
    if (!balanced) allBalanced = false;
    running = roundCents(running + delta);
    rows.push({
      id: line.id,
      memo: line.memo,
      effective_on: line.effective_on,
      delta: toMoney(delta),
      balance: toMoney(running),
      balanced,
      postings: line.postings,
    });
  }

  return {
    rows,
    derivedOutstanding: toMoney(running),
    allBalanced,
  };
}

/** Compare two money strings to the cent. */
export function moneyEquals(a: string, b: string): boolean {
  return toMoney(Number(a)) === toMoney(Number(b));
}
