"""Money arithmetic for the ledger.

Pure functions over :class:`decimal.Decimal`. Nothing here imports Django, so it
can be unit-tested on its own — which is why the money rules live here and not
scattered through the services.

All amounts are whole cents (two decimal places). See ``GLOSSARY.md``.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


def to_cents(value: Decimal) -> Decimal:
    """Quantize to whole cents, rounding down. Use before money leaves this module."""
    return value.quantize(CENT, rounding=ROUND_DOWN)


def distribute_remainder(total: Decimal, parts: int) -> list[Decimal]:
    """Split ``total`` into ``parts`` cent-exact amounts that sum to ``total``.

    Lender policy (GLOSSARY §Money and rounding): residual cents are added to the
    FIRST instalment(s), never the last. A borrower must never receive a final
    instalment LARGER than the earlier ones — a bigger final payment reads as a
    penalty and generates support calls. Front-loading the residual cent is
    intentional. It looks odd; it is correct, and ``tests/test_money.py`` pins it.
    """
    if parts <= 0:
        raise ValueError("parts must be positive")
    base = to_cents(total / parts)
    amounts = [base] * parts
    residual_cents = int(((total - base * parts) / CENT).to_integral_value())
    for i in range(residual_cents):
        amounts[i] += CENT  # front-load onto the FIRST instalments — see docstring
    return amounts


@dataclass(frozen=True)
class Allocation:
    """The breakdown of one repayment across the waterfall. Sums to the payment."""

    fees: Decimal
    interest: Decimal
    principal: Decimal

    @property
    def total(self) -> Decimal:
        return self.fees + self.interest + self.principal


def allocate_waterfall(
    payment: Decimal,
    *,
    fees_due: Decimal,
    interest_due: Decimal,
    principal_due: Decimal,
) -> Allocation:
    """Allocate ``payment`` across what is owed, in priority order.

    Order is fixed: **fees -> interest -> principal** (GLOSSARY §The Waterfall).
    Each bucket absorbs as much of the payment as it can before the next takes the
    remainder. The returned Allocation always sums to exactly ``payment`` — any
    excess beyond everything owed lands in ``principal`` (an overpayment shows up
    as principal driven negative, i.e. the borrower is in credit).
    """
    remaining = to_cents(payment)

    fees = min(remaining, max(ZERO, to_cents(fees_due)))
    remaining -= fees

    interest = min(remaining, max(ZERO, to_cents(interest_due)))
    remaining -= interest

    # Whatever is left goes to principal — including any overpayment, which makes
    # this figure exceed principal_due (handled by the caller / feature slice).
    principal = remaining

    return Allocation(fees=fees, interest=interest, principal=principal)
