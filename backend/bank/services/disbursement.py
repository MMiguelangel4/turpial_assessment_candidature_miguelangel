"""Disbursing a loan: move principal (and book fees) onto the ledger.

This is existing, working code — the Candidate is not asked to change it. It is
the reference for how a transaction gets written in this codebase, though note it
predates ``services.transactions.record_transaction`` and still writes postings
one at a time.
"""
from __future__ import annotations

from decimal import Decimal

from django.db import transaction as db_transaction

from ..models import Account, AccountKind, Loan, Posting, Transaction


def _account(loan: Loan, kind: str) -> Account:
    account, _ = Account.objects.get_or_create(loan=loan, kind=kind)
    return account


def _cash_account() -> Account:
    account, _ = Account.objects.get_or_create(loan=None, kind=AccountKind.CASH)
    return account


@db_transaction.atomic
def disburse(loan: Loan) -> Transaction:
    """Book a loan's opening balances.

    Debits principal_receivable (and fees_receivable, if any); credits cash.
    Postings are saved individually.
    """
    txn = Transaction.objects.create(
        memo=f"Disbursement of loan #{loan.pk}",
        effective_on=loan.opened_on,
        loan=loan,
    )

    cash = _cash_account()
    principal_recv = _account(loan, AccountKind.PRINCIPAL_RECEIVABLE)
    fees_recv = _account(loan, AccountKind.FEES_RECEIVABLE)
    # ensure the interest receivable account exists for later accrual/repayment
    _account(loan, AccountKind.INTEREST_RECEIVABLE)

    booked = loan.principal + loan.fees

    Posting(transaction=txn, account=principal_recv, amount=loan.principal).save()
    if loan.fees > Decimal("0.00"):
        Posting(transaction=txn, account=fees_recv, amount=loan.fees).save()
    Posting(transaction=txn, account=cash, amount=-booked).save()

    return txn
