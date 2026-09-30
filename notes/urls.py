from django.urls import path
from .views import NoteListView, NoteDetailView

app_name = "notes"

urlpatterns = [
    path("", NoteListView.as_view(), name="list"),
    path("<slug:slug>/", NoteDetailView.as_view(), name="detail"),
]
