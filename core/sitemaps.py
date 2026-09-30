from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from projects.models import Project
from notes.models import Note


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        return [
            "core:home",
            "core:about",
            "core:stack",
            "projects:list",
            "projects:engineering",
            "notes:list",
            "contact:index",
        ]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return Project.objects.filter(is_published=True).order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at


class NoteSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return Note.objects.filter(is_published=True).order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at
