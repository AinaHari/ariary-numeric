from django.urls import path
from . import views

urlpatterns = [
    path("wallet/", views.WalletDetailView.as_view(), name="wallet-detail"),
    path("transactions/", views.TransactionListView.as_view(), name="transaction-list"),
    path("transactions/<uuid:reference>/", views.TransactionDetailView.as_view(), name="transaction-detail"),
    path("transfer/", views.TransferView.as_view(), name="transfer"),
    path("topup-demo/", views.TopupDemoView.as_view(), name="topup-demo"),
]
