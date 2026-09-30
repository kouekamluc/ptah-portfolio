from django.urls import path
from .views import ProjectListView, ProjectDetailView, engineering_view

app_name = "projects"

urlpatterns = [
    path("", ProjectListView.as_view(), name="list"),
    path("engineering/", engineering_view, name="engineering"),
    path("<slug:slug>/", ProjectDetailView.as_view(), name="detail"),
]
