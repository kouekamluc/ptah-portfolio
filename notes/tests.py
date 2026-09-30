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

    def test_note_tag_and_featured_filtering(self):
        featured_note = Note.objects.create(
            title="State Space Estimation",
            excerpt="Observer design in modern control",
            content_markdown="State space matrices A, B, C, D.",
            category=self.category,
            tags="Estimation, Kalman",
            is_published=True,
            is_featured=True
        )
        # Filter by tag
        res_tag = self.client.get(reverse("notes:list"), {"tag": "Kalman"})
        self.assertEqual(res_tag.status_code, 200)
        self.assertContains(res_tag, "State Space Estimation")
        self.assertNotContains(res_tag, "Discrete PID Implementation")

        # Filter by featured
        res_feat = self.client.get(reverse("notes:list"), {"featured": "1"})
        self.assertEqual(res_feat.status_code, 200)
        self.assertContains(res_feat, "State Space Estimation")
        self.assertNotContains(res_feat, "Discrete PID Implementation")

    def test_note_xss_sanitization(self):
        xss_note = Note.objects.create(
            title="XSS Test Note",
            excerpt="Security test",
            content_markdown="Safe text <script>alert('xss')</script> and <iframe src='malicious.com'></iframe>",
            category=self.category,
            is_published=True
        )
        self.assertNotIn("<script>", xss_note.content_html)
        self.assertNotIn("</script>", xss_note.content_html)
        self.assertNotIn("<iframe", xss_note.content_html)

    def test_note_detail_404_for_nonexistent_slug(self):
        res = self.client.get(reverse("notes:detail", kwargs={"slug": "non-existent-note-slug"}))
        self.assertEqual(res.status_code, 404)

    def test_note_model_aliases_and_seo(self):
        note = self.note
        note.seo_description = "Engineered PID discrete controller derivation and C++ embedded loop."
        note.save()
        self.assertEqual(note.meta_description, "Engineered PID discrete controller derivation and C++ embedded loop.")
        self.assertEqual(note.content, note.content_markdown)
        self.assertEqual(note.published, note.is_published)
        self.assertEqual(note.featured, note.is_featured)

    def test_note_empty_state(self):
        Note.objects.all().delete()
        res = self.client.get(reverse("notes:list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "No notes found matching your criteria.")
