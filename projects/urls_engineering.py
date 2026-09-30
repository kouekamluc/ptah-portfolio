from django.urls import path
from .views import engineering_view

urlpatterns = [
    path("", engineering_view, name="engineering_index"),
]
