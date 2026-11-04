from django.contrib import admin
from .models import Shipment, ShipmentEvent, ShipmentDocument


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("reference", "owner", "name", "origin", "destination", "mode", "status", "estimated_departure", "estimated_arrival", "created_at")
    search_fields = ("reference", "name", "origin", "destination", "carrier", "tracking_number", "owner__email")
    list_filter = ("mode", "status", "created_at")
    readonly_fields = ("reference", "created_at", "updated_at")


@admin.register(ShipmentEvent)
class ShipmentEventAdmin(admin.ModelAdmin):
    list_display = ("id", "shipment", "status", "location", "source", "created_at")
    search_fields = ("shipment__reference", "location", "description")
    list_filter = ("status", "source", "created_at")


@admin.register(ShipmentDocument)
class ShipmentDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "shipment", "name", "uploaded_by", "created_at")
    search_fields = ("name", "shipment__reference")
    list_filter = ("created_at",)