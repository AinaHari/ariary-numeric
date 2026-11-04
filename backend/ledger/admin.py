from django.contrib import admin
from .models import LedgerEntry


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "transaction", "wallet", "entry_type", "amount", "balance_after", "created_at")
    search_fields = ("transaction__reference", "wallet__user__email")
    list_filter = ("entry_type", "created_at")
    readonly_fields = ("transaction", "wallet", "entry_type", "amount", "balance_after", "created_at")