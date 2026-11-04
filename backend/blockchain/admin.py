from django.contrib import admin
from .models import BlockchainRecord


@admin.register(BlockchainRecord)
class BlockchainRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "record_type", "data_hash", "network", "status", "created_at")
    search_fields = ("record_type", "data_hash", "tx_hash")
    list_filter = ("status", "network", "record_type", "created_at")
    readonly_fields = ("data_hash", "created_at", "confirmed_at")