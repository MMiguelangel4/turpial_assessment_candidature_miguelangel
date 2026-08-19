"""Ledger invariants and the existing disbursement feature."""
from datetime import date
from decimal import Decimal

import pytest

from bank.models import Account, AccountKind, Loan
from bank.selectors import available_credit, get_balance
from bank.services.disbursement import disburse

pytestmark = pytest.mark.django_db


def _loan(**kw):
    defaults = dict(
        borrower="Test Borrower",
        principal=Decimal("10000.00"),
        annual_rate=Decimal("0.1200"),
        fees=Decimal("150.00"),
        limit=Decimal("15000.00"),
        opened_on=date(2026, 1, 5),
    )
    defaults.update(kw)
    return Loan.objects.create(**defaults)


def test_disbursement_balances_to_zero():
    loan = _loan()
    txn = disburse(loan)
    total = sum(p.amount for p in txn.postings.all())
    assert total == Decimal("0.00")


def test_derived_balance_matches_disbursement():
    loan = _loan()
    disburse(loan)
    principal = Account.objects.get(loan=loan, kind=AccountKind.PRINCIPAL_RECEIVABLE)
    fees = Account.objects.get(loan=loan, kind=AccountKind.FEES_RECEIVABLE)
    assert get_balance(principal) == Decimal("10000.00")
    assert get_balance(fees) == Decimal("150.00")


def test_available_credit_subtracts_holds():
    from bank.models import Hold, HoldStatus

    loan = _loan(limit=Decimal("15000.00"))
    Hold.objects.create(loan=loan, amount=Decimal("2000.00"),
                        status=HoldStatus.PENDING, placed_on=date(2026, 1, 6))
    Hold.objects.create(loan=loan, amount=Decimal("1000.00"),
                        status=HoldStatus.SETTLED, placed_on=date(2026, 1, 6))
    # 15000 - 1000 settled - 2000 pending = 12000
    assert available_credit(loan) == Decimal("12000.00")
