from django.db import models

from wallet.models import Transaction, Wallet


class LedgerEntry(models.Model):
    ENTRY_DEBIT = "debit"
    ENTRY_CREDIT = "credit"
    ENTRY_CHOICES = [(ENTRY_DEBIT, "Débit"), (ENTRY_CREDIT, "Crédit")]

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="entries")
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="ledger_entries")
    entry_type = models.CharField(max_length=10, choices=ENTRY_CHOICES)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    balance_after = models.DecimalField(max_digits=18, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.wallet_id} {self.entry_type} {self.amount}"
