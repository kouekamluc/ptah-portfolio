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

    def test_unpublished_note_visibility(self):
        draft_note = Note.objects.create(
            title="Draft Engineering Hypothesis",
            excerpt="Unpublished laboratory measurements",
            content_markdown="## Confidential\n\nData pending validation.",
            category=self.category,
            tags="Confidential, Draft",
            is_published=False
        )
        # Anonymous visitor should get 404
        res = self.client.get(reverse("notes:detail", kwargs={"slug": draft_note.slug}))
        self.assertEqual(res.status_code, 404)

        # Staff user can preview draft
        from django.contrib.auth import get_user_model
        User = get_user_model()
        staff = User.objects.create_user(username="lab_staff", password="pass1234password", is_staff=True)
        self.client.login(username="lab_staff", password="pass1234password")
        res_staff = self.client.get(reverse("notes:detail", kwargs={"slug": draft_note.slug}))
        self.assertEqual(res_staff.status_code, 200)
        self.assertContains(res_staff, "Draft Engineering Hypothesis")

    def test_note_category_filtering(self):
        res = self.client.get(reverse("notes:list"), {"category": self.category.slug})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Discrete PID Implementation")
