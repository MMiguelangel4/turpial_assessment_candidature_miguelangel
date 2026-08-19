"""The bank's data model: a double-entry ledger and the loans it services.

Read ``GLOSSARY.md`` before this file. Sign convention: a debit is positive, a
credit is negative, and every Transaction's Postings sum to zero.
"""
from __future__ import annotations

from decimal import Decimal

from django.db import models


class AccountKind(models.TextChoices):
    CASH = "cash", "Cash"
    PRINCIPAL_RECEIVABLE = "principal_receivable", "Principal receivable"
    INTEREST_RECEIVABLE = "interest_receivable", "Interest receivable"
    FEES_RECEIVABLE = "fees_receivable", "Fees receivable"


class Account(models.Model):
    """A bucket money is tracked against.

    ``cash`` is global (one row, ``loan`` null). The three receivable kinds are
    per-loan — the borrower owes *this loan's* principal/interest/fees.
    """

    kind = models.CharField(max_length=32, choices=AccountKind.choices)
    loan = models.ForeignKey(
        "Loan", null=True, blank=True, on_delete=models.CASCADE, related_name="accounts"
    )

    # Cached running balance, kept in step by a post_save signal on Posting.
    # The authoritative balance is derived — see selectors.get_balance().
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["kind", "loan"],
                name="one_account_per_kind_per_loan",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.kind}" + (f"#{self.loan_id}" if self.loan_id else "")


class Loan(models.Model):
    """A fixed-term advance to a borrower."""

    borrower = models.CharField(max_length=200)
    principal = models.DecimalField(max_digits=18, decimal_places=2)
    annual_rate = models.DecimalField(max_digits=6, decimal_places=4)  # e.g. 0.1200 = 12%
    fees = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    limit = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    opened_on = models.DateField()

    def __str__(self) -> str:
        return f"Loan #{self.pk} — {self.borrower}"


class Transaction(models.Model):
    """One financial event, made of two or more Postings that balance to zero."""

    memo = models.CharField(max_length=300, blank=True)
    loan = models.ForeignKey(
        Loan, null=True, blank=True, on_delete=models.CASCADE, related_name="transactions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    effective_on = models.DateField()

    def __str__(self) -> str:
        return f"Txn #{self.pk} — {self.memo}"


class Posting(models.Model):
    """A single signed entry against one Account, belonging to one Transaction."""

    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="postings"
    )
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="postings")
    amount = models.DecimalField(max_digits=18, decimal_places=2)  # signed; credit is negative

    class Meta:
        constraints = [
            # A disbursement touches each account at most once, so this keeps
            # duplicate postings out. (Added with the disbursement feature.)
            models.UniqueConstraint(
                fields=["transaction", "account"],
                name="one_posting_per_account_per_txn",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.account} {self.amount:+}"


class HoldStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SETTLED = "settled", "Settled"
    RELEASED = "released", "Released"


class Hold(models.Model):
    """An amount reserved against a loan's limit but not yet settled."""

    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="holds")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(
        max_length=16, choices=HoldStatus.choices, default=HoldStatus.PENDING
    )
    placed_on = models.DateField()

    def __str__(self) -> str:
        return f"Hold {self.amount} ({self.status}) on loan #{self.loan_id}"
