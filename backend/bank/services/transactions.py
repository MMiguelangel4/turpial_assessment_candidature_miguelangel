"""Recording balanced transactions into the ledger."""
from __future__ import annotations

from decimal import Decimal

from django.db import transaction as db_transaction
from django.db.models import Sum

from ..models import Posting, Transaction


class ImbalancedTransaction(Exception):
    """Raised when a transaction's postings do not sum to exactly zero."""


@db_transaction.atomic
def record_transaction(
    *, memo: str, effective_on, postings: list[Posting], loan=None
) -> Transaction:
    """Persist a set of postings as one balanced Transaction.

    ``postings`` are unsaved ``Posting`` instances with ``account`` and ``amount``
    set; this attaches them to a fresh Transaction and writes them. Raises
    :class:`ImbalancedTransaction` if they do not sum to zero.
    """
    txn = Transaction.objects.create(memo=memo, effective_on=effective_on, loan=loan)
    for p in postings:
        p.transaction = txn
    # bulk_create for efficiency — one round trip.
    Posting.objects.bulk_create(postings)
    _assert_balanced(txn)
    return txn


def _assert_balanced(txn: Transaction) -> None:
    raw = txn.postings.aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    # SQLite can return a float for a DecimalField Sum; coerce before comparing.
    total = Decimal(str(raw)).quantize(Decimal("0.01"))
    if total != Decimal("0.00"):
        raise ImbalancedTransaction(
            f"Transaction #{txn.pk} postings sum to {total}, not zero"
        )
