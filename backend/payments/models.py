from django.conf import settings
from django.db import models


class ExchangeRate(models.Model):
    base = models.CharField(max_length=10)
    target = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=18, decimal_places=6)
    source = models.CharField(max_length=80, default="démonstration")
    is_demo = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("base", "target")
        ordering = ["base", "target"]

    def __str__(self):
        return f"{self.base}/{self.target} = {self.rate}"


class InternationalTransfer(models.Model):
    STATUS_DRAFT = "brouillon"
    STATUS_ESTIMATED = "estime"
    STATUS_DISABLED = "desactive"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Brouillon"),
        (STATUS_ESTIMATED, "Estimé"),
        (STATUS_DISABLED, "Désactivé (partenaire requis)"),
    ]

    reference = models.CharField(max_length=40, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="intl_transfers")
    origin_country = models.CharField(max_length=80)
    destination_country = models.CharField(max_length=80)
    origin_currency = models.CharField(max_length=10)
    destination_currency = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    rate = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    estimated_fee = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    estimated_receive = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_ESTIMATED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class PaymentConnector(models.Model):
    name = models.CharField(max_length=80)
    kind = models.CharField(max_length=40)  # mobile_money, bank, fx
    config = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.kind}) active={self.is_active}"
