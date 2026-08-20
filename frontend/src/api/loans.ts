import { getJSON } from "./client";
import type { LoanSummary, Paginated, StatementLine } from "../types";

export const listLoans = () => getJSON<LoanSummary[]>("/loans/");
export const getLoan = (id: number) => getJSON<LoanSummary>(`/loans/${id}/`);

/**
 * Full statement for a loan.
 *
 * The API paginates (default page_size=2). We request a large page and follow
 * `next` so the running balance is built from the complete history.
 */
export async function getStatement(id: number): Promise<StatementLine[]> {
  const lines: StatementLine[] = [];
  let path: string | null = `/loans/${id}/statement/?page_size=100`;

  while (path) {
    const page = await getJSON<Paginated<StatementLine>>(path);
    lines.push(...page.results);
    path = page.next ? apiPathFromNext(page.next) : null;
  }

  return lines;
}

/** Turn a DRF `next` URL into a path for getJSON (`/loans/...`). */
function apiPathFromNext(next: string): string {
  const url = new URL(next, "http://localhost");
  return url.pathname.replace(/^\/api/, "") + url.search;
}