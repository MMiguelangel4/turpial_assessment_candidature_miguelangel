"""Read-side queries over the ledger.

The balance of an account is *derived* — the sum of its postings — not the cached
``Account.balance`` column. When the two disagree, this is the source of truth.
"""
from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum

from .models import Account, Hold, HoldStatus, Loan


def get_balance(account: Account) -> Decimal:
    """The authoritative balance of an account: the sum of its postings."""
    total = account.postings.aggregate(s=Sum("amount"))["s"]
    if total is None:
        return Decimal("0.00")
    # SQLite can hand back a float for a DecimalField Sum; keep money in Decimal.
    return Decimal(str(total)).quantize(Decimal("0.01"))


def loan_outstanding(loan: Loan) -> dict[str, Decimal]:
    """What the borrower still owes on a loan, per receivable, derived from postings."""
    out: dict[str, Decimal] = {}
    for account in loan.accounts.all():
        if account.kind == "cash":
            continue
        out[account.kind] = get_balance(account)
    return out


def available_credit(loan: Loan) -> Decimal:
    """available_credit = limit - settled - holds  (GLOSSARY §Credit and holds)."""
    settled = (
        loan.holds.filter(status=HoldStatus.SETTLED).aggregate(s=Sum("amount"))["s"]
        or Decimal("0.00")
    )
    holds = (
        loan.holds.filter(status=HoldStatus.PENDING).aggregate(s=Sum("amount"))["s"]
        or Decimal("0.00")
    )
    return loan.limit - settled - holds
