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

        # Category filter
        cat_slug = self.request.GET.get("category", "").strip()
        if cat_slug:
            qs = qs.filter(category__slug=cat_slug)

        # Project Type filter
        p_type = self.request.GET.get("type", "").strip()
        if p_type:
            qs = qs.filter(project_type=p_type)

        # Technology filter
        tech_slug = self.request.GET.get("tech", "").strip()
        if tech_slug:
            qs = qs.filter(technologies__slug=tech_slug)

        return qs.order_by("display_order", "-start_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = ProjectCategory.objects.all().order_by("display_order")
        context["technologies"] = Technology.objects.filter(projects__isnull=False).distinct().order_by("name")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_type"] = self.request.GET.get("type", "")
        context["current_tech"] = self.request.GET.get("tech", "")
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
            .distinct()[:3]
        )
        return context


def engineering_view(request):
    """Specialized showcase of mechatronics, embedded hardware, and circuit engineering."""
    hardware_types = ["mechatronics", "embedded", "electronics", "control", "experimental"]
    projects = (
        Project.objects.filter(is_published=True, project_type__in=hardware_types)
        .select_related("category")
        .prefetch_related("technologies", "metrics", "images")
        .order_by("display_order", "-start_date")
    )
    return render(request, "projects/engineering.html", {
        "projects": projects,
        "section_title": "Mechatronics & Physical Engineering",
    })
