from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_TRANSFER_RECEIVED = "transfer_received"
    TYPE_TRANSFER_SENT = "transfer_sent"
    TYPE_SHIPMENT = "shipment"
    TYPE_CUSTOMS = "customs"
    TYPE_PAYMENT_ERROR = "payment_error"
    TYPE_INFO = "info"
    TYPE_CHOICES = [
        (TYPE_TRANSFER_RECEIVED, "Transfert reçu"),
        (TYPE_TRANSFER_SENT, "Transfert envoyé"),
        (TYPE_SHIPMENT, "Expédition"),
        (TYPE_CUSTOMS, "Douane"),
        (TYPE_PAYMENT_ERROR, "Erreur de paiement"),
        (TYPE_INFO, "Information"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    ntype = models.CharField(max_length=40, choices=TYPE_CHOICES, default=TYPE_INFO)
    title = models.CharField(max_length=120)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email}: {self.title}"
