from django.test import TestCase, Client
from django.urls import reverse
from .models import Note, NoteCategory


class NoteModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = NoteCategory.objects.create(name="Control Theory")
        self.note = Note.objects.create(
            title="Discrete PID Implementation",
            excerpt="Euler backward difference method",
            content_markdown="## Heading\n\n```cpp\nfloat err = setpoint - val;\n```",
            category=self.category,
            tags="PID, Arduino, Control",
            is_published=True
        )

    def test_markdown_sanitization_and_html_generation(self):
        # Verify content_html was automatically generated and contains safe tags
        self.assertIn("Heading</h2>", self.note.content_html)
        self.assertIn("<code>", self.note.content_html)
        self.assertEqual(self.note.reading_time_minutes, 1)

    def test_note_list_view(self):
        response = self.client.get(reverse("notes:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Discrete PID Implementation")

    def test_note_detail_view(self):
        response = self.client.get(reverse("notes:detail", kwargs={"slug": self.note.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Discrete PID Implementation")
        self.assertContains(response, "Heading")
