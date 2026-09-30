from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from core.models import Technology
from .models import Project, ProjectCategory


class ProjectListView(ListView):
    model = Project
    paginate_by = 9
    context_object_name = "projects"

    def get_template_names(self):
        if self.request.headers.get("HX-Request") == "true":
            return ["projects/partials/project_grid.html"]
        return ["projects/list.html"]

    def get_queryset(self):
        qs = Project.objects.filter(is_published=True).select_related("category").prefetch_related("technologies", "metrics")
        
        # Search query
        query = self.request.GET.get("q", "").strip()
        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(tagline__icontains=query) |
                Q(overview__icontains=query) |
                Q(technologies__name__icontains=query)
            ).distinct()

        # Category filter (?category=embedded)
        cat_slug = self.request.GET.get("category", "").strip()
        if cat_slug:
            qs = qs.filter(category__slug=cat_slug)

        # Status filter (?status=completed)
        status_val = self.request.GET.get("status", "").strip()
        if status_val:
            qs = qs.filter(status=status_val)

        # Project Type filter
        p_type = self.request.GET.get("type", "").strip()
        if p_type:
            qs = qs.filter(project_type=p_type)

        # Technology filter (?technology=django or ?tech=django)
        tech_val = (self.request.GET.get("technology", "") or self.request.GET.get("tech", "")).strip()
        if tech_val:
            qs = qs.filter(Q(technologies__slug=tech_val) | Q(technologies__name__iexact=tech_val)).distinct()

        # Featured first, then deliberate display_order, then most recent start date
        return qs.order_by("-is_featured", "display_order", "-start_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = ProjectCategory.objects.all().order_by("display_order")
        context["technologies"] = Technology.objects.filter(projects__isnull=False).distinct().order_by("name")
        context["statuses"] = Project.STATUS_CHOICES
        context["current_category"] = self.request.GET.get("category", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_type"] = self.request.GET.get("type", "")
        context["current_tech"] = self.request.GET.get("technology", "") or self.request.GET.get("tech", "")
        context["search_query"] = self.request.GET.get("q", "")
        context["project_types"] = Project.TYPE_CHOICES
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_queryset(self):
        if self.request.user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        context["metrics"] = project.metrics.all()
        context["images"] = project.images.all()
        context["files"] = project.files.all()
        context["related_projects"] = (
            Project.objects.filter(is_published=True)
            .exclude(id=project.id)
            .filter(Q(category=project.category) | Q(technologies__in=project.technologies.all()))
            .select_related("category")
            .prefetch_related("technologies", "metrics")
            .distinct()[:3]
        )
        return context


def engineering_view(request):
    """Specialized showcase of mechatronics, embedded hardware, and circuit engineering."""
    from notes.models import Note

    hardware_types = ["mechatronics", "embedded", "electronics", "control", "experimental"]
    base_qs = (
        Project.objects.filter(is_published=True, project_type__in=hardware_types)
        .select_related("category")
        .prefetch_related("technologies", "metrics", "images")
    )

    category_slug = request.GET.get("category", "").strip()
    status_filter = request.GET.get("status", "").strip()

    projects = base_qs
    if category_slug:
        projects = projects.filter(category__slug=category_slug)
    if status_filter:
        projects = projects.filter(status=status_filter)

    projects = projects.order_by("-is_featured", "display_order", "-start_date")

    # Hardware categories that actually contain engineering projects
    categories = ProjectCategory.objects.filter(
        projects__in=base_qs
    ).distinct().order_by("display_order", "name")

    # Active hardware prototypes
    active_prototypes = base_qs.filter(
        status__in=["planning", "in_development", "prototype", "testing"]
    ).order_by("display_order", "-start_date")[:4]

    # Relevant hardware technologies
    relevant_technologies = Technology.objects.filter(
        is_active=True
    ).filter(
        Q(category__slug__in=["embedded", "embedded-systems", "hardware", "electronics", "engineering"]) |
        Q(category__name__icontains="embedded") |
        Q(category__name__icontains="electronics") |
        Q(category__name__icontains="hardware") |
        Q(category__name__icontains="engineering")
    ).select_related("category").order_by("display_order", "name")[:12]

    # Engineering notes
    engineering_notes = Note.objects.filter(
        is_published=True
    ).filter(
        Q(category__name__icontains="control") |
        Q(category__name__icontains="hardware") |
        Q(category__name__icontains="embedded") |
        Q(category__name__icontains="electronics") |
        Q(tags__icontains="Arduino") |
        Q(tags__icontains="ESP32") |
        Q(tags__icontains="Circuit") |
        Q(tags__icontains="PID")
    ).select_related("category").order_by("-published_at")[:3]

    return render(request, "projects/engineering.html", {
        "projects": projects,
        "categories": categories,
        "current_category": category_slug,
        "current_status": status_filter,
        "active_prototypes": active_prototypes,
        "relevant_technologies": relevant_technologies,
        "engineering_notes": engineering_notes,
        "section_title": "Mechatronics & Physical Engineering",
    })
