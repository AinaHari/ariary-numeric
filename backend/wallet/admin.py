from django.contrib import admin
from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "currency", "balance", "is_demo", "updated_at")
    search_fields = ("user__email",)
    list_filter = ("currency", "is_demo")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("reference", "sender", "recipient", "amount", "fee", "currency", "kind", "status", "created_at")
    search_fields = ("reference", "sender__email", "recipient__email", "description")
    list_filter = ("kind", "status", "currency", "created_at")
    readonly_fields = ("reference", "created_at", "completed_at")
    ordering = ("-created_at",)