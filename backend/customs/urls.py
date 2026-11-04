from django.urls import path
from . import views

urlpatterns = [
    path("cases/", views.CustomsCaseListCreateView.as_view(), name="customs-list"),
    path("cases/<str:reference>/", views.CustomsCaseDetailView.as_view(), name="customs-detail"),
    path("cases/<str:reference>/events/", views.CustomsEventCreateView.as_view(), name="customs-event"),
    path("cases/<str:reference>/documents/", views.CustomsDocUploadView.as_view(), name="customs-doc"),
    path("cases/<str:reference>/documents/<int:doc_id>/download/", views.CustomsDocumentDownloadView.as_view(), name="customs-doc-download"),
    path("cases/<str:reference>/requirements/<int:req_id>/toggle/", views.RequirementToggleView.as_view(), name="customs-req-toggle"),
]
