from __future__ import annotations

from django.urls import path

from .views import LoanDetailView, LoanListView, LoanStatementView

urlpatterns = [
    path("loans/", LoanListView.as_view(), name="loan-list"),
    path("loans/<int:pk>/", LoanDetailView.as_view(), name="loan-detail"),
    path("loans/<int:pk>/statement/", LoanStatementView.as_view(), name="loan-statement"),
]
