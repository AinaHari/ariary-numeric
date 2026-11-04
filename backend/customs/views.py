from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomsCase, DocumentRequirement, CustomsEvent, CustomsDocument
from .serializers import CustomsCaseSerializer, CustomsCaseCreateSerializer


class CustomsCaseListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return CustomsCase.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CustomsCaseCreateSerializer
        return CustomsCaseSerializer

    def perform_create(self, serializer):
        case = serializer.save(owner=self.request.user)
        # default configurable checklist (not legal universal list)
        defaults = ["Facture commerciale", "Connaissement (BL) / Lettre de transport", "Packing list", "Certificat d'origine"]
        for d in defaults:
            DocumentRequirement.objects.create(case=case, name=d)
        CustomsEvent.objects.create(case=case, status=case.status, description="Dossier créé")


class CustomsCaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CustomsCaseSerializer
    lookup_field = "reference"

    def get_queryset(self):
        return CustomsCase.objects.filter(owner=self.request.user)


class CustomsEventCreateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, reference):
        try:
            case = CustomsCase.objects.get(reference=reference, owner=request.user)
        except CustomsCase.DoesNotExist:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        status_val = request.data.get("status")
        desc = request.data.get("description", "")
        if status_val not in [c[0] for c in CustomsCase.STATUS_CHOICES]:
            return Response({"detail": "Statut invalide."}, status=status.HTTP_400_BAD_REQUEST)
        case.status = status_val
        case.save(update_fields=["status", "updated_at"])
        ev = CustomsEvent.objects.create(case=case, status=status_val, description=desc)
        from notifications.models import Notification
        Notification.objects.create(user=request.user, ntype="customs", title="Mise à jour douane", message=f"{case.reference}: {status_val}")
        return Response({"id": ev.id, "status": ev.status}, status=status.HTTP_201_CREATED)


class CustomsDocUploadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, reference):
        try:
            case = CustomsCase.objects.get(reference=reference, owner=request.user)
        except CustomsCase.DoesNotExist:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        f = request.FILES.get("file")
        if not f:
            return Response({"detail": "Fichier requis."}, status=status.HTTP_400_BAD_REQUEST)
        import os
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx"]:
            return Response({"detail": "Type non autorisé."}, status=status.HTTP_400_BAD_REQUEST)
        if f.size > 5 * 1024 * 1024:
            return Response({"detail": "Fichier trop volumineux."}, status=status.HTTP_400_BAD_REQUEST)
        doc = CustomsDocument.objects.create(case=case, name=request.data.get("name", f.name), file=f, uploaded_by=request.user)
        return Response({"id": doc.id, "name": doc.name}, status=status.HTTP_201_CREATED)


class CustomsDocumentDownloadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, reference, doc_id):
        try:
            case = CustomsCase.objects.get(reference=reference, owner=request.user)
            doc = CustomsDocument.objects.get(id=doc_id, case=case)
        except (CustomsCase.DoesNotExist, CustomsDocument.DoesNotExist):
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        import mimetypes, os
        content_type, _ = mimetypes.guess_type(doc.file.name)
        from django.http import FileResponse
        resp = FileResponse(doc.file.open("rb"), content_type=content_type or "application/octet-stream")
        resp["Content-Disposition"] = f'inline; filename="{os.path.basename(doc.file.name)}"'
        return resp


class RequirementToggleView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, reference, req_id):
        try:
            case = CustomsCase.objects.get(reference=reference, owner=request.user)
            req = DocumentRequirement.objects.get(id=req_id, case=case)
        except Exception:
            return Response({"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND)
        req.provided = not req.provided
        req.save(update_fields=["provided"])
        return Response({"id": req.id, "provided": req.provided})
