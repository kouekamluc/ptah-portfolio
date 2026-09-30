from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from .models import Note, NoteCategory


class NoteListView(ListView):
    model = Note
    paginate_by = 10
    context_object_name = "notes"

    def get_template_names(self):
        if self.request.headers.get("HX-Request") == "true":
            return ["notes/partials/note_list_partial.html"]
        return ["notes/list.html"]

    def get_queryset(self):
        qs = Note.objects.filter(is_published=True).select_related("category")
        
        query = self.request.GET.get("q", "").strip()
        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(tags__icontains=query)
            )

        cat_slug = self.request.GET.get("category", "").strip()
        if cat_slug:
            qs = qs.filter(category__slug=cat_slug)

        tag = self.request.GET.get("tag", "").strip()
        if tag:
            qs = qs.filter(tags__icontains=tag)

        return qs.order_by("-published_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = NoteCategory.objects.all().order_by("display_order")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_tag"] = self.request.GET.get("tag", "")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class NoteDetailView(DetailView):
    model = Note
    template_name = "notes/detail.html"
    context_object_name = "note"

    def get_queryset(self):
        if self.request.user.is_staff:
            return Note.objects.all()
        return Note.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = self.object
        context["related_notes"] = (
            Note.objects.filter(is_published=True)
            .exclude(id=note.id)
            .filter(category=note.category)
            .select_related("category")[:3]
        )
        return context
