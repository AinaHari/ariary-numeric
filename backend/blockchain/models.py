from django.db import models


class BlockchainRecord(models.Model):
    STATUS_UNCONFIGURED = "non_configure"
    STATUS_PENDING = "en_attente"
    STATUS_CONFIRMED = "confirme"
    STATUS_FAILED = "echoue"
    STATUS_CHOICES = [
        (STATUS_UNCONFIGURED, "Blockchain de test non configurée"),
        (STATUS_PENDING, "En attente"),
        (STATUS_CONFIRMED, "Confirmé"),
        (STATUS_FAILED, "Échoué"),
    ]

    record_type = models.CharField(max_length=60)
    data_hash = models.CharField(max_length=128)
    network = models.CharField(max_length=60, default="sepolia")
    tx_hash = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_UNCONFIGURED)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.record_type} {self.data_hash[:12]} ({self.status})"
