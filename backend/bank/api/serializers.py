from __future__ import annotations

from rest_framework import serializers

from ..models import Loan, Posting, Transaction


class LoanSummarySerializer(serializers.ModelSerializer):
    outstanding = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ["id", "borrower", "principal", "annual_rate", "fees", "opened_on", "outstanding"]

    def get_outstanding(self, loan: Loan):
        # Fast path for the dashboard: sum the cached balances of the loan's
        # receivable accounts. (Avoids re-summing every posting on list views.)
        total = sum(
            (a.balance for a in loan.accounts.all() if a.kind != "cash"),
            start=__import__("decimal").Decimal("0.00"),
        )
        return total


class PostingSerializer(serializers.ModelSerializer):
    account_kind = serializers.CharField(source="account.kind")

    class Meta:
        model = Posting
        fields = ["id", "account_kind", "amount"]


class StatementLineSerializer(serializers.ModelSerializer):
    postings = PostingSerializer(many=True)

    class Meta:
        model = Transaction
        fields = ["id", "memo", "effective_on", "postings"]
