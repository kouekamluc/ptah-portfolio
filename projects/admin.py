from django.contrib import admin
from django.utils.html import format_html
from .models import ProjectCategory, Project, ProjectMetric, ProjectImage, ProjectFile


class ProjectMetricInline(admin.TabularInline):
    model = ProjectMetric
    extra = 1
    fields = ("label", "value", "description", "display_order")


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "alt_text", "caption", "image_type", "display_order", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 40px; border-radius: 4px;" />', obj.image.url)
        return "-"
    preview.short_description = "Preview"


class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 1
    fields = ("title", "file", "file_type", "display_order")


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "display_order", "project_count")
    list_editable = ("display_order",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")

    def project_count(self, obj):
        return obj.projects.count()
    project_count.short_description = "Projects"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project_type",
        "category",
        "status",
        "is_featured",
        "is_published",
        "start_date",
        "display_order",
        "thumbnail_preview",
    )
    list_filter = ("project_type", "category", "status", "is_featured", "is_published")
    list_editable = ("status", "is_featured", "is_published", "display_order")
    search_fields = ("title", "tagline", "overview", "hardware_specs", "software_stack_details")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("technologies",)
    inlines = [ProjectMetricInline, ProjectImageInline, ProjectFileInline]

    fieldsets = (
        ("Basic Overview & Identity", {
            "fields": (
                "title",
                "slug",
                "tagline",
                "project_type",
                "category",
                "status",
                "technologies",
                "display_order",
                "is_featured",
                "is_published",
            )
        }),
        ("Dates & Visual Assets", {
            "fields": (
                "start_date",
                "end_date",
                "thumbnail",
                "hero_image",
            )
        }),
        ("Links & Repositories", {
            "fields": (
                "github_url",
                "live_url",
                "documentation_url",
                "video_url",
            )
        }),
        ("Case Study: Core Definition", {
            "fields": (
                "overview",
                "problem",
                "objectives",
            )
        }),
        ("Case Study: Technical Architecture & Specs", {
            "fields": (
                "system_architecture",
                "hardware_specs",
                "software_stack_details",
            )
        }),
        ("Case Study: Execution & Results", {
            "fields": (
                "engineering_process",
                "challenges",
                "solution",
                "quantitative_results",
                "lessons_learned",
                "future_improvements",
            )
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="height: 36px; border-radius: 4px;" />', obj.thumbnail.url)
        return "-"
    thumbnail_preview.short_description = "Thumbnail"
