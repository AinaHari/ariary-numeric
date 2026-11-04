from django.urls import path
from . import views

urlpatterns = [
    path("info/", views.BlockchainInfoView.as_view(), name="blockchain-info"),
    path("records/", views.BlockchainRecordListCreateView.as_view(), name="blockchain-records"),
    path("records/<int:pk>/", views.BlockchainRecordDetailView.as_view(), name="blockchain-record-detail"),
    path("verify/", views.BlockchainVerifyView.as_view(), name="blockchain-verify"),
]
