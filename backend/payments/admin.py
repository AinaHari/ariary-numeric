from django.contrib import admin
from .models import ExchangeRate, InternationalTransfer, PaymentConnector


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("base", "target", "rate", "source", "updated_at")
    search_fields = ("base", "target", "source")
    list_filter = ("source",)


@admin.register(InternationalTransfer)
class InternationalTransferAdmin(admin.ModelAdmin):
    list_display = ("reference", "owner", "origin_country", "destination_country", "origin_currency", "destination_currency", "amount", "rate", "estimated_fee", "estimated_receive", "status", "created_at")
    search_fields = ("reference", "user__email", "origin_country", "destination_country")
    list_filter = ("status", "origin_currency", "destination_currency", "created_at")
    readonly_fields = ("reference", "created_at")


@admin.register(PaymentConnector)
class PaymentConnectorAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "is_active", "created_at")
    search_fields = ("name", "kind")
    list_filter = ("is_active", "kind")