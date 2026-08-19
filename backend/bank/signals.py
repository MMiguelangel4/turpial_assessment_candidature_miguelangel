"""Keep ``Account.balance`` in step with its postings.

Note this is a convenience cache for quick dashboard reads. The authoritative
balance is always ``selectors.get_balance()``.
"""
from __future__ import annotations

from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Account, Posting


@receiver(post_save, sender=Posting)
def _bump_cached_balance(sender, instance: Posting, created: bool, **kwargs) -> None:
    if created:
        Account.objects.filter(pk=instance.account_id).update(
            balance=F("balance") + instance.amount
        )
