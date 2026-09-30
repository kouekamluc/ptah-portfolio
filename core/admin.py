from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SiteSettings,
    TechnologyCategory,
    Technology,
    CurrentlyBuilding,
    TimelineItem,
    Education,
    SocialLink,
    Organization,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Personal Identity", {
            "fields": (
                "full_name",
                "professional_title",
                "short_bio",
                "long_bio",
                "location",
                "public_email",
                "availability_status",
            )
        }),
        ("Visual & Media Assets", {
            "fields": (
                "profile_photo",
                "hero_image",
                "opengraph_image",
            )
        }),
        ("Curriculum Vitae / Resume", {
            "fields": (
                "resume_file",
                "resume_version",
            )
        }),
        ("SEO & Footer", {
            "fields": (
                "seo_meta_keywords",
                "footer_text",
            )
        }),
    )

    def has_add_permission(self, request):
        # Enforce singleton in admin: disable Add button if an instance already exists
        if SiteSettings.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TechnologyCategory)
class TechnologyCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "display_order", "tech_count")
    list_editable = ("display_order",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")

    def tech_count(self, obj):
        return obj.technologies.count()
    tech_count.short_description = "Technologies"


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "proficiency", "highlighted", "display_order", "years_used")
    list_filter = ("category", "proficiency", "highlighted")
    list_editable = ("highlighted", "display_order", "proficiency")
    search_fields = ("name", "description", "category__name")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CurrentlyBuilding)
class CurrentlyBuildingAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "category", "progress_bar", "is_active", "display_order", "updated_at")
    list_filter = ("is_active", "category")
    list_editable = ("is_active", "display_order")
    search_fields = ("title", "description", "status")

    def progress_bar(self, obj):
        return format_html(
            """
            <div style="width: 100px; background-color: #e5e7eb; border-radius: 4px; overflow: hidden; height: 12px; display: inline-block; vertical-align: middle;">
                <div style="width: {}%; background-color: #10b981; height: 100%;"></div>
            </div>
            <span style="font-size: 11px; margin-left: 6px;">{}%</span>
            """,
            obj.progress,
            obj.progress,
        )
    progress_bar.short_description = "Progress"


@admin.register(TimelineItem)
class TimelineItemAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "item_type", "start_date", "end_date", "is_current", "display_order")
    list_filter = ("item_type", "is_current")
    list_editable = ("display_order", "is_current")
    search_fields = ("title", "organization", "description")


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("degree", "institution", "location", "start_date", "end_date", "is_current", "display_order")
    list_filter = ("is_current",)
    list_editable = ("display_order", "is_current")
    search_fields = ("degree", "institution", "coursework", "description")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("display_name", "platform", "username", "url", "is_active", "show_in_hero", "show_in_footer", "display_order")
    list_filter = ("platform", "is_active", "show_in_hero", "show_in_footer")
    list_editable = ("is_active", "show_in_hero", "show_in_footer", "display_order")
    search_fields = ("display_name", "username", "url")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "period", "is_active", "display_order")
    list_filter = ("is_active",)
    list_editable = ("is_active", "display_order")
    search_fields = ("name", "role", "description")
    prepopulated_fields = {"slug": ("name",)}
