from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import SiteSettings, TechnologyCategory, Technology, Education, TimelineItem


class CoreModelTests(TestCase):
    def test_site_settings_singleton(self):
        settings = SiteSettings.get_settings()
        self.assertEqual(settings.full_name, "Ptah Kouekam Kamgou Luc Kevin")

        # Attempting to create a second instance should raise ValidationError
        second_settings = SiteSettings(full_name="Duplicate")
        with self.assertRaises(ValidationError):
            second_settings.clean()

    def test_technology_and_category(self):
        cat = TechnologyCategory.objects.create(name="Embedded Hardware", display_order=1)
        tech = Technology.objects.create(
            category=cat,
            name="ESP32",
            proficiency="strong",
            highlighted=True
        )
        self.assertEqual(str(tech), "ESP32 (Embedded Hardware)")
        self.assertEqual(tech.slug, "esp32")


class CoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.settings = SiteSettings.get_settings()
        self.cat = TechnologyCategory.objects.create(name="Software", display_order=1)
        self.tech = Technology.objects.create(category=self.cat, name="Django", highlighted=True)

    def test_home_page(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ptah Kouekam")
        self.assertContains(response, "Engineer. Developer. Builder.")

    def test_about_page(self):
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Academic Engineering Studies")

    def test_stack_page(self):
        response = self.client.get(reverse("core:stack"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Technologies & Engineering Stack")
        self.assertContains(response, "Django")

    def test_search_view_regular(self):
        response = self.client.get(reverse("core:search"), {"q": "Django"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django")

    def test_search_view_htmx(self):
        response = self.client.get(reverse("core:search"), {"q": "Django"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/partials/search_results.html")

    def test_robots_txt(self):
        response = self.client.get(reverse("core:robots_txt"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User-agent: *")
        self.assertContains(response, "Sitemap:")

    def test_health_check(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "healthy")
        self.assertEqual(response.json().get("database"), "connected")

    def test_cv_download_fallback(self):
        # By default no CV file is uploaded in test DB
        response = self.client.get(reverse("core:cv_download"))
        # Should redirect to contact page with a message
        self.assertRedirects(response, reverse("contact:index"))

    def test_cv_button_fallback_on_home(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        # Should display 'Request CV' instead of broken download link
        self.assertContains(response, "Request CV")
