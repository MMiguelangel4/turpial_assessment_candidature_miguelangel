"""Money arithmetic tests. Pure — no database."""
from decimal import Decimal

from bank.money import allocate_waterfall, distribute_remainder


def test_residual_cent_goes_to_first_instalment():
    # $100.00 over 3 -> 33.34, 33.33, 33.33 (not 33.33, 33.33, 33.34).
    # Lender policy: the borrower never gets a LARGER final instalment.
    assert distribute_remainder(Decimal("100.00"), 3) == [
        Decimal("33.34"),
        Decimal("33.33"),
        Decimal("33.33"),
    ]


def test_distribute_remainder_sums_to_total():
    parts = distribute_remainder(Decimal("10.00"), 7)
    assert sum(parts) == Decimal("10.00")


def test_waterfall_orders_fees_interest_principal():
    alloc = allocate_waterfall(
        Decimal("150.00"),
        fees_due=Decimal("5.00"),
        interest_due=Decimal("12.50"),
        principal_due=Decimal("2000.00"),
    )
    assert alloc.fees == Decimal("5.00")
    assert alloc.interest == Decimal("12.50")
    assert alloc.principal == Decimal("132.50")
    assert alloc.total == Decimal("150.00")


def test_waterfall_partial_payment_stops_at_interest():
    alloc = allocate_waterfall(
        Decimal("6.00"),
        fees_due=Decimal("5.00"),
        interest_due=Decimal("12.50"),
        principal_due=Decimal("2000.00"),
    )
    assert alloc.fees == Decimal("5.00")
    assert alloc.interest == Decimal("1.00")
    assert alloc.principal == Decimal("0.00")
