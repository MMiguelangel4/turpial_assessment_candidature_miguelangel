"""Daily interest accrual on outstanding principal.

Convention: Actual/360 (GLOSSARY §Interest accrual). Interest builds up daily on
the outstanding principal whether or not a payment is made.
"""
from __future__ import annotations

from decimal import Decimal

from ..money import to_cents


def daily_interest(principal: Decimal, annual_rate: Decimal) -> Decimal:
    """Interest for one day. Convention: Actual/360 (see GLOSSARY §Interest accrual)."""
    # actual days elapsed, over a 360-day year
    return (principal * annual_rate) / Decimal("365")


def interest_for_period(principal: Decimal, annual_rate: Decimal, days: int) -> Decimal:
    """Interest accrued over ``days`` actual days on a flat outstanding principal."""
    return to_cents(daily_interest(principal, annual_rate) * days)
