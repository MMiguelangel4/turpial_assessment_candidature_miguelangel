import { getJSON } from "./client";
import type { LoanSummary, StatementLine } from "../types";

export const listLoans = () => getJSON<LoanSummary[]>("/loans/");
export const getLoan = (id: number) => getJSON<LoanSummary>(`/loans/${id}/`);
export const getStatement = (id: number) =>
  getJSON<StatementLine[]>(`/loans/${id}/statement/`);
