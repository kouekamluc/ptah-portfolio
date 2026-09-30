from django.contrib import admin
from django.utils.html import format_html
from .models import NoteCategory, Note


@admin.register(NoteCategory)
class NoteCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "display_order", "note_count")
    list_editable = ("display_order",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def note_count(self, obj):
        return obj.notes.count()
    note_count.short_description = "Notes"


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "reading_time_minutes",
        "is_published",
        "is_featured",
        "published_at",
        "preview_cover",
    )
    list_filter = ("category", "is_published", "is_featured", "published_at")
    list_editable = ("is_published", "is_featured")
    search_fields = ("title", "excerpt", "content_markdown", "tags")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("content_html", "reading_time_minutes", "created_at", "updated_at")

    fieldsets = (
        ("Meta & Categorization", {
            "fields": (
                "title",
                "slug",
                "category",
                "tags",
                "is_published",
                "is_featured",
                "published_at",
            )
        }),
        ("Abstract & Cover", {
            "fields": (
                "excerpt",
                "seo_description",
                "cover_image",
            )
        }),
        ("Content (Markdown)", {
            "fields": (
                "content_markdown",
                "reading_time_minutes",
                "content_html",
            )
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    def preview_cover(self, obj):
        if obj.cover_image:
            try:
                return format_html('<img src="{}" style="height: 36px; border-radius: 4px;" />', obj.cover_image.url)
            except ValueError:
                return "-"
        return "-"
    preview_cover.short_description = "Cover"
