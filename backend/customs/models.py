import uuid
from django.conf import settings
from django.db import models


def _customs_ref():
    import uuid
    return f"DOU-{uuid.uuid4().hex[:8].upper()}"

class CustomsCase(models.Model):
    STATUS_CREATED = "cree"
    STATUS_DOCS = "documents_a_fournir"
    STATUS_VERIFY = "verification"
    STATUS_FORMALITIES = "formalites"
    STATUS_DONE = "formalites_terminees"
    STATUS_CLOSED = "clos"
    STATUS_CHOICES = [
        (STATUS_CREATED, "Dossier créé"),
        (STATUS_DOCS, "Documents à fournir"),
        (STATUS_VERIFY, "Documents en vérification"),
        (STATUS_FORMALITIES, "En attente de formalités"),
        (STATUS_DONE, "Formalités terminées"),
        (STATUS_CLOSED, "Dossier clôturé"),
    ]

    reference = models.CharField(max_length=40, unique=True, default=_customs_ref)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customs_cases")
    description = models.CharField(max_length=255)
    origin_country = models.CharField(max_length=80)
    destination_country = models.CharField(max_length=80)
    mode = models.CharField(max_length=20, default="maritime")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_CREATED)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.reference


class DocumentRequirement(models.Model):
    case = models.ForeignKey(CustomsCase, on_delete=models.CASCADE, related_name="requirements")
    name = models.CharField(max_length=120)
    is_required = models.BooleanField(default=True)
    provided = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.case.reference}: {self.name}"


class CustomsDocument(models.Model):
    case = models.ForeignKey(CustomsCase, on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(max_length=120)
    file = models.FileField(upload_to="customs/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CustomsEvent(models.Model):
    case = models.ForeignKey(CustomsCase, on_delete=models.CASCADE, related_name="events")
    status = models.CharField(max_length=30, choices=CustomsCase.STATUS_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
