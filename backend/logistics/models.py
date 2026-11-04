import uuid
from django.conf import settings
from django.db import models


def _shipment_ref():
    import uuid
    return f"EXP-{uuid.uuid4().hex[:8].upper()}"

class Shipment(models.Model):
    MODE_MARITIME = "maritime"
    MODE_AERIEN = "aerien"
    MODE_TERRESTRE = "terrestre"
    MODE_CHOICES = [(MODE_MARITIME, "Maritime"), (MODE_AERIEN, "Aérien"), (MODE_TERRESTRE, "Terrestre")]

    STATUS_PREPARATION = "preparation"
    STATUS_ATTENTE = "attente_depart"
    STATUS_TRANSIT = "transit"
    STATUS_ARRIVE = "arrive_port"
    STATUS_DEDOUANEMENT = "dedouanement"
    STATUS_LIBERE = "libere"
    STATUS_LIVRAISON = "livraison"
    STATUS_LIVRE = "livre"
    STATUS_RETARDE = "retarde"
    STATUS_ANNULE = "annule"
    STATUS_CHOICES = [
        (STATUS_PREPARATION, "Préparation"),
        (STATUS_ATTENTE, "En attente de départ"),
        (STATUS_TRANSIT, "En transit"),
        (STATUS_ARRIVE, "Arrivé au port/aéroport"),
        (STATUS_DEDOUANEMENT, "En cours de dédouanement"),
        (STATUS_LIBERE, "Libéré par la douane"),
        (STATUS_LIVRAISON, "En livraison"),
        (STATUS_LIVRE, "Livré"),
        (STATUS_RETARDE, "Retardé"),
        (STATUS_ANNULE, "Annulé"),
    ]

    reference = models.CharField(max_length=40, unique=True, default=_shipment_ref)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shipments")
    name = models.CharField(max_length=120)
    origin = models.CharField(max_length=120)
    destination = models.CharField(max_length=120)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default=MODE_MARITIME)
    carrier = models.CharField(max_length=120, blank=True)
    tracking_number = models.CharField(max_length=120, blank=True)
    estimated_departure = models.DateField(null=True, blank=True)
    estimated_arrival = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PREPARATION)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} {self.name}"


class ShipmentEvent(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="events")
    status = models.CharField(max_length=30, choices=Shipment.STATUS_CHOICES)
    location = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=40, default="manuel")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.shipment.reference}: {self.status}"


class ShipmentDocument(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(max_length=120)
    file = models.FileField(upload_to="shipments/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
