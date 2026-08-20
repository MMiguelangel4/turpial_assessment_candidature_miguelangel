export interface LoanSummary {
  id: number;
  borrower: string;
  principal: string;
  annual_rate: string;
  fees: string;
  opened_on: string;
  outstanding: string; // NOTE: served from cached balances (see the API)
}

export interface Posting {
  id: number;
  account_kind: string;
  amount: string; // signed; credit is negative
}

export interface StatementLine {
  id: number;
  memo: string;
  effective_on: string;
  postings: Posting[];
}

/** DRF page envelope used by GET /api/loans/:id/statement/. */
export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
