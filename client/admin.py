# apps/accounts/admin.py
from django.contrib import admin
from .models import ClientProfile

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "gender", "skin_tone", "body_shape", "face_shape", "created_at")
    list_filter = ("gender", "skin_tone", "body_shape", "face_shape")
    search_fields = ("user__username", "user__email", "user__phone")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
