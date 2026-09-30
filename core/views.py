from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView
from projects.models import Project, ProjectCategory
from notes.models import Note
from .models import (
    SiteSettings,
    TechnologyCategory,
    Technology,
    CurrentlyBuilding,
    TimelineItem,
    Education,
    Organization,
)


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_projects"] = (
            Project.objects.filter(is_published=True, is_featured=True)
            .select_related("category")
            .prefetch_related("technologies", "metrics")
            .order_by("display_order", "-start_date")[:4]
        )
        active_statuses = ["planning", "in_development", "prototype", "testing", "concept"]
        context["currently_building"] = (
            Project.objects.filter(is_published=True, status__in=active_statuses)
            .select_related("category")
            .prefetch_related("technologies")
            .order_by("display_order", "-start_date")[:3]
        )
        context["tech_categories"] = (
            TechnologyCategory.objects.prefetch_related("technologies")
            .order_by("display_order")
        )
        context["highlighted_techs"] = (
            Technology.objects.filter(highlighted=True)
            .select_related("category")
            .order_by("category__display_order", "display_order")
        )
        context["latest_notes"] = (
            Note.objects.filter(is_published=True)
            .select_related("category")
            .order_by("-published_at")[:3]
        )
        context["project_categories"] = ProjectCategory.objects.all().order_by("display_order")
        context["organizations"] = Organization.objects.filter(is_active=True).order_by("display_order")
        return context


class AboutView(TemplateView):
    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["educations"] = Education.objects.all().order_by("display_order", "-start_date")
        context["timeline_items"] = TimelineItem.objects.all().order_by("display_order", "-start_date")
        context["organizations"] = Organization.objects.filter(is_active=True).order_by("display_order")
        return context


class StackView(TemplateView):
    template_name = "core/stack.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = (
            TechnologyCategory.objects.prefetch_related("technologies")
            .order_by("display_order")
        )
        return context


class SearchView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "").strip()
        is_htmx = request.headers.get("HX-Request") == "true"
        
        projects = []
        notes = []
        technologies = []

        if query:
            projects = Project.objects.filter(
                is_published=True
            ).filter(
                Q(title__icontains=query) |
                Q(tagline__icontains=query) |
                Q(overview__icontains=query) |
                Q(hardware_specs__icontains=query) |
                Q(software_stack_details__icontains=query)
            ).distinct()[:6]

            notes = Note.objects.filter(
                is_published=True
            ).filter(
                Q(title__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(tags__icontains=query)
            ).distinct()[:5]

            technologies = Technology.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            ).select_related("category")[:8]

        context = {
            "query": query,
            "projects": projects,
            "notes": notes,
            "technologies": technologies,
            "total_count": len(projects) + len(notes) + len(technologies),
        }

        if is_htmx:
            return render(request, "core/partials/search_results.html", context)
        return render(request, "core/search.html", context)


def robots_txt(request):
    """Dynamically serve robots.txt pointing to the XML sitemap."""
    host = request.get_host()
    scheme = "https" if request.is_secure() else "http"
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {scheme}://{host}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def health_check(request):
    """Lightweight health check endpoint for Railway, Docker, and PaaS liveness probes."""
    from django.http import JsonResponse
    from django.db import connection
    
    status_data = {
        "status": "healthy",
        "app": "ptah-portfolio",
    }
    try:
        connection.ensure_connection()
        status_data["database"] = "connected"
        return JsonResponse(status_data, status=200)
    except Exception as e:
        status_data["status"] = "degraded"
        status_data["database"] = str(e)
        return JsonResponse(status_data, status=503)


def cv_download_view(request):
    """
    Clean permalink for downloading the latest CV.
    Gracefully redirects to contact page if no resume has been uploaded yet.
    """
    from django.shortcuts import redirect
    from django.contrib import messages
    site_settings = SiteSettings.get_settings()
    if site_settings.resume_file:
        return redirect(site_settings.resume_file.url)
    messages.info(request, "Direct CV download is currently being updated. Please send an inquiry to request an updated resume.")
    return redirect("contact:index")


