from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "phone", "country", "preferred_language", "is_verified_email", "is_staff", "is_active", "created_at")
    search_fields = ("email", "first_name", "last_name", "phone")
    list_filter = ("is_staff", "is_active", "country", "preferred_language", "is_verified_email")
    ordering = ("-created_at",)