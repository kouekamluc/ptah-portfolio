from django.urls import path
from .views import HomeView, AboutView, StackView, SearchView, robots_txt, cv_download_view

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("stack/", StackView.as_view(), name="stack"),
    path("search/", SearchView.as_view(), name="search"),
    path("cv/", cv_download_view, name="cv_download"),
    path("robots.txt", robots_txt, name="robots_txt"),
]

