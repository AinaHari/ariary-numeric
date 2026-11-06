import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Wallet(models.Model):
    CURRENCY_MGA = "MGA"
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    currency = models.CharField(max_length=10, default=CURRENCY_MGA)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    is_demo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet({self.user.email}, {self.balance} {self.currency})"


class Transaction(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_COMPLETED, "Terminée"),
        (STATUS_FAILED, "Échouée"),
    ]
    KIND_TRANSFER = "transfer"
    KIND_TOPUP = "topup"
    KIND_PAYMENT = "payment"
    KIND_CHOICES = [
        (KIND_TRANSFER, "Transfert"),
        (KIND_TOPUP, "Rechargement démo"),
        (KIND_PAYMENT, "Paiement"),
    ]

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sent_transactions", null=True, blank=True)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="received_transactions", null=True, blank=True)
    sender_wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="outgoing", null=True, blank=True)
    recipient_wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="incoming", null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    fee = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=10, default="MGA")
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=KIND_TRANSFER)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    description = models.CharField(max_length=255, blank=True)
    idempotency_key = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "idempotency_key"],
                condition=models.Q(idempotency_key__isnull=False) & ~models.Q(idempotency_key=""),
                name="unique_idempotency_per_sender",
            ),
        ]

    def __str__(self):
        return f"{self.reference} {self.amount} {self.currency} ({self.status})"