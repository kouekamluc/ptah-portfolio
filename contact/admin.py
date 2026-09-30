from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "organization", "subject", "is_read", "is_archived", "created_at")
    list_filter = ("is_read", "is_archived", "created_at")
    list_editable = ("is_read", "is_archived")
    search_fields = ("name", "email", "organization", "subject", "message")
    readonly_fields = ("name", "email", "organization", "subject", "message", "ip_address", "created_at")

    fieldsets = (
        ("Inquiry Details", {
            "fields": (
                "name",
                "email",
                "organization",
                "subject",
                "message",
            )
        }),
        ("Status & Meta", {
            "fields": (
                "is_read",
                "is_archived",
                "ip_address",
                "created_at",
            )
        }),
    )

    def has_add_permission(self, request):
        return False
