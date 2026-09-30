from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "organization", "subject", "is_read", "is_archived", "created_at")
    list_filter = ("is_read", "is_archived", "created_at")
    list_editable = ("is_read", "is_archived")
    search_fields = ("name", "email", "organization", "subject", "message")
    readonly_fields = ("name", "email", "organization", "subject", "message", "ip_address", "created_at")
    actions = ["mark_as_read", "mark_as_unread", "mark_as_archived", "mark_as_unarchived"]

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

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as Read"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as Unread (New)"

    def mark_as_archived(self, request, queryset):
        queryset.update(is_archived=True)
    mark_as_archived.short_description = "Mark selected messages as Archived"

    def mark_as_unarchived(self, request, queryset):
        queryset.update(is_archived=False)
    mark_as_unarchived.short_description = "Restore selected messages from Archive"

    def has_add_permission(self, request):
        return False
