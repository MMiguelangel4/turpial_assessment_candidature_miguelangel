"""Seed a small, runnable demo world.

Creates a cash account, a couple of loans, disburses them, and books some
historical repayments so the statement view has something to reconcile.

    python manage.py seed
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction as db_transaction

from bank.models import Account, AccountKind, Loan, Posting
from bank.money import allocate_waterfall
from bank.services.disbursement import disburse
from bank.services.transactions import record_transaction


class Command(BaseCommand):
    help = "Seed demo loans, disbursements, and a few repayments."

    @db_transaction.atomic
    def handle(self, *args, **options):
        if Loan.objects.exists():
            self.stdout.write(self.style.WARNING("Data already present; skipping seed."))
            return

        Account.objects.get_or_create(loan=None, kind=AccountKind.CASH)

        loan_a = Loan.objects.create(
            borrower="Rosa Delgado",
            principal=Decimal("10000.00"),
            annual_rate=Decimal("0.1200"),
            fees=Decimal("150.00"),
            limit=Decimal("15000.00"),
            opened_on=date(2026, 1, 5),
        )
        loan_b = Loan.objects.create(
            borrower="Kwame Mensah",
            principal=Decimal("4000.00"),
            annual_rate=Decimal("0.0900"),
            fees=Decimal("0.00"),
            limit=Decimal("6000.00"),
            opened_on=date(2026, 2, 12),
        )

        disburse(loan_a)
        disburse(loan_b)

        # A couple of historical repayments on loan A, booked through the shared
        # record_transaction helper (as any repayment would be).
        self._book_repayment(loan_a, Decimal("500.00"), date(2026, 2, 5),
                             fees_due=Decimal("150.00"), interest_due=Decimal("100.00"))
        self._book_repayment(loan_a, Decimal("300.00"), date(2026, 3, 5),
                             fees_due=Decimal("0.00"), interest_due=Decimal("98.63"))

        self.stdout.write(self.style.SUCCESS("Seeded 2 loans with history."))

    def _book_repayment(self, loan, amount, on, *, fees_due, interest_due):
        alloc = allocate_waterfall(
            amount, fees_due=fees_due, interest_due=interest_due,
            principal_due=Decimal("999999.00"),
        )
        cash = Account.objects.get(loan=None, kind=AccountKind.CASH)
        fees = Account.objects.get(loan=loan, kind=AccountKind.FEES_RECEIVABLE)
        interest = Account.objects.get(loan=loan, kind=AccountKind.INTEREST_RECEIVABLE)
        principal = Account.objects.get(loan=loan, kind=AccountKind.PRINCIPAL_RECEIVABLE)

        postings = [
            Posting(account=cash, amount=amount),
            Posting(account=fees, amount=-alloc.fees),
            Posting(account=interest, amount=-alloc.interest),
            Posting(account=principal, amount=-alloc.principal),
        ]
        record_transaction(
            memo=f"Repayment on loan #{loan.pk}", effective_on=on,
            postings=postings, loan=loan,
        )
