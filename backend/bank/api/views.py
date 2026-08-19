from __future__ import annotations

from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from ..models import Loan, Transaction
from .serializers import LoanSummarySerializer, StatementLineSerializer


class StatementPagination(PageNumberPagination):
    """Statements on long-running loans get big, so page them.

    Callers can override with ?page_size=, up to 100.
    """

    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 100


class LoanListView(generics.ListAPIView):
    """All loans, with a quick `outstanding` from the cached balances."""

    queryset = Loan.objects.prefetch_related("accounts").all()
    serializer_class = LoanSummarySerializer
    permission_classes = [AllowAny]


class LoanDetailView(generics.RetrieveAPIView):
    queryset = Loan.objects.prefetch_related("accounts").all()
    serializer_class = LoanSummarySerializer
    permission_classes = [AllowAny]


class LoanStatementView(generics.ListAPIView):
    """The raw transaction/posting history for a loan.

    The client reconciles these into a running balance. This is the honest,
    derived view of the loan — as opposed to the `outstanding` summary field,
    which reads the cached balances.
    """

    serializer_class = StatementLineSerializer
    permission_classes = [AllowAny]
    pagination_class = StatementPagination

    def get_queryset(self):
        return (
            Transaction.objects.filter(loan_id=self.kwargs["pk"])
            .prefetch_related("postings", "postings__account")
            .order_by("effective_on", "id")
        )
