from django.contrib import admin
from .models import CustomsCase, DocumentRequirement, CustomsDocument, CustomsEvent


@admin.register(CustomsCase)
class CustomsCaseAdmin(admin.ModelAdmin):
    list_display = ("reference", "owner", "description", "origin_country", "destination_country", "mode", "status", "created_at", "updated_at")
    search_fields = ("reference", "description", "origin_country", "destination_country", "owner__email")
    list_filter = ("status", "mode", "created_at")
    readonly_fields = ("reference", "created_at", "updated_at")


@admin.register(DocumentRequirement)
class DocumentRequirementAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "name", "is_required", "provided")
    search_fields = ("name", "case__reference")
    list_filter = ("is_required", "provided")


@admin.register(CustomsDocument)
class CustomsDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "name", "uploaded_by", "created_at")
    search_fields = ("name", "case__reference")
    list_filter = ("created_at",)


@admin.register(CustomsEvent)
class CustomsEventAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "status", "created_at")
    search_fields = ("case__reference", "description")
    list_filter = ("status", "created_at")