from django.urls import path
from . import views

urlpatterns = [
    path("rates/", views.ExchangeRateListView.as_view(), name="rates"),
    path("international/estimate/", views.EstimateInternationalTransferView.as_view(), name="intl-estimate"),
    path("international/", views.InternationalTransferListView.as_view(), name="intl-list"),
    path("connectors/", views.PaymentConnectorListView.as_view(), name="connectors"),
    path("mobile-money/info/", views.MobileMoneyInfoView.as_view(), name="mm-info"),
]
