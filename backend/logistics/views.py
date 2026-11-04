from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Shipment, ShipmentEvent, ShipmentDocument
from .serializers import ShipmentSerializer, ShipmentCreateSerializer, ShipmentEventSerializer


class ShipmentListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Shipment.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ShipmentCreateSerializer
        return ShipmentSerializer

    def perform_create(self, serializer):
        shipment = serializer.save(owner=self.request.user)
        ShipmentEvent.objects.create(shipment=shipment, status=shipment.status, description="Expédition créée (données manuelles)", source="manuel")


class ShipmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ShipmentSerializer
    lookup_field = "reference"

    def get_queryset(self):
        return Shipment.objects.filter(owner=self.request.user)


class ShipmentEventCreateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, reference):
        try:
            shipment = Shipment.objects.get(reference=reference, owner=request.user)
        except Shipment.DoesNotExist:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ShipmentEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save(shipment=shipment)
        # update shipment status
        shipment.status = event.status
        shipment.save(update_fields=["status", "updated_at"])
        return Response(ShipmentEventSerializer(event).data, status=status.HTTP_201_CREATED)


class ShipmentDocumentUploadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, reference):
        try:
            shipment = Shipment.objects.get(reference=reference, owner=request.user)
        except Shipment.DoesNotExist:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        f = request.FILES.get("file")
        if not f:
            return Response({"detail": "Fichier requis."}, status=status.HTTP_400_BAD_REQUEST)
        allowed = [".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx"]
        import os
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in allowed:
            return Response({"detail": "Type de fichier non autorisé."}, status=status.HTTP_400_BAD_REQUEST)
        if f.size > 5 * 1024 * 1024:
            return Response({"detail": "Fichier trop volumineux."}, status=status.HTTP_400_BAD_REQUEST)
        doc = ShipmentDocument.objects.create(shipment=shipment, name=request.data.get("name", f.name), file=f, uploaded_by=request.user)
        from notifications.models import Notification
        Notification.objects.create(user=request.user, ntype="shipment", title="Document ajouté", message=f"Document ajouté à {shipment.reference}")
        return Response({"id": doc.id, "name": doc.name}, status=status.HTTP_201_CREATED)


class ShipmentDocumentDownloadView(APIView):
    """Téléchargement authentifié d'un document d'expédition (pas d'accès public)."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, reference, doc_id):
        try:
            shipment = Shipment.objects.get(reference=reference, owner=request.user)
            doc = ShipmentDocument.objects.get(id=doc_id, shipment=shipment)
        except (Shipment.DoesNotExist, ShipmentDocument.DoesNotExist):
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        import mimetypes, os
        content_type, _ = mimetypes.guess_type(doc.file.name)
        from django.http import FileResponse
        resp = FileResponse(doc.file.open("rb"), content_type=content_type or "application/octet-stream")
        resp["Content-Disposition"] = f'inline; filename="{os.path.basename(doc.file.name)}"'
        return resp
