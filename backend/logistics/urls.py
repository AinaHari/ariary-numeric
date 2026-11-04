from django.urls import path
from . import views

urlpatterns = [
    path("shipments/", views.ShipmentListCreateView.as_view(), name="shipment-list"),
    path("shipments/<str:reference>/", views.ShipmentDetailView.as_view(), name="shipment-detail"),
    path("shipments/<str:reference>/events/", views.ShipmentEventCreateView.as_view(), name="shipment-event"),
    path("shipments/<str:reference>/documents/", views.ShipmentDocumentUploadView.as_view(), name="shipment-doc"),
    path("shipments/<str:reference>/documents/<int:doc_id>/download/", views.ShipmentDocumentDownloadView.as_view(), name="shipment-doc-download"),
]
