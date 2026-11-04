from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "actor", "action", "target_type", "target_id", "ip_address", "created_at")
    search_fields = ("action", "target_type", "target_id", "actor__email")
    list_filter = ("action", "target_type", "created_at")
    readonly_fields = ("actor", "action", "target_type", "target_id", "metadata", "ip_address", "created_at")
    ordering = ("-created_at",)