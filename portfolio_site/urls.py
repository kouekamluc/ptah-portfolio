from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from core.sitemaps import StaticViewSitemap, ProjectSitemap, NoteSitemap
from core.views import health_check

sitemaps = {
    "static": StaticViewSitemap,
    "projects": ProjectSitemap,
    "notes": NoteSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health_check"),
    path("", include("core.urls", namespace="core")),
    path("projects/", include("projects.urls", namespace="projects")),
    path("engineering/", include("projects.urls_engineering")),
    path("notes/", include("notes.urls", namespace="notes")),
    path("contact/", include("contact.urls", namespace="contact")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]

# Serve media and static files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Custom error handlers
handler404 = "core.views_error.custom_404"
handler500 = "core.views_error.custom_500"
handler403 = "core.views_error.custom_403"
