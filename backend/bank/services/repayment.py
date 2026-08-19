"""Recording a repayment against a loan.

    ┌─────────────────────────────────────────────────────────────────────┐
    │  THIS IS YOUR TASK (back-end Feature Slice).                         │
    │                                                                     │
    │  A repayment arrives against a loan. Accept it, allocate it across   │
    │  the loan's balances in the order the domain requires, and record   │
    │  the result so the loan's accounting stays consistent.              │
    │                                                                     │
    │  What's already here for you:                                       │
    │    • the amounts owed, per bucket, via selectors + accrual          │
    │    • the waterfall allocation itself, in money.allocate_waterfall   │
    │    • the way this codebase writes balanced postings, in             │
    │      services.transactions.record_transaction                       │
    │                                                                     │
    │  You decide what "consistent" has to mean, and what happens at the  │
    │  edges. Read GLOSSARY.md first.                                      │
    │                                                                     │
    │  Scope: this service function is the task. You do NOT need to add   │
    │  an HTTP endpoint — exposing it over the API is out of scope.       │
    └─────────────────────────────────────────────────────────────────────┘
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from ..models import Loan, Transaction


def record_repayment(*, loan: Loan, amount: Decimal, effective_on: date) -> Transaction:
    """Record a borrower's repayment against ``loan``.

    Returns the Transaction that was written.

    TODO(candidate): implement this. The allocation order, the postings, and the
    edges (overpayment, an already-settled loan, an awkward amount) are yours to
    decide and defend.
    """
    raise NotImplementedError("record_repayment is the Feature Slice — implement me")
