from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import SiteSettings, TechnologyCategory, Technology, Education, TimelineItem, SocialLink
from projects.models import Project, ProjectCategory


class CoreModelTests(TestCase):
    def test_site_settings_singleton(self):
        settings = SiteSettings.get_settings()
        self.assertEqual(settings.full_name, "Ptah Kouekam Kamgou Luc Kevin")

        # Attempting to create a second instance should raise ValidationError
        second_settings = SiteSettings(full_name="Duplicate")
        with self.assertRaises(ValidationError):
            second_settings.clean()

    def test_site_settings_property_aliases(self):
        settings = SiteSettings.get_settings()
        self.assertEqual(settings.profile_image, settings.profile_photo)
        self.assertEqual(settings.default_social_image, settings.opengraph_image)
        self.assertEqual(settings.resume, settings.resume_file)

    def test_site_settings_default_meta_description(self):
        settings = SiteSettings.get_settings()
        settings.default_meta_description = "Engineered systems and mechatronics portfolio."
        settings.save()
        fresh = SiteSettings.get_settings()
        self.assertEqual(fresh.default_meta_description, "Engineered systems and mechatronics portfolio.")

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

    def test_global_context_processor_availability(self):
        response = self.client.get(reverse("core:home"))
        self.assertIn("site_settings", response.context)
        self.assertIn("global_socials", response.context)
        self.assertIn("global_hero_socials", response.context)
        self.assertIn("global_nav_socials", response.context)
        self.assertIn("global_footer_socials", response.context)
        self.assertIn("global_currently_building", response.context)
        self.assertIn("current_year", response.context)

    def test_home_page(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ptah Kouekam")
        self.assertContains(response, "Engineer. Developer. Builder.")

    def test_home_page_with_meta_description(self):
        self.settings.default_meta_description = "Unique engineer portfolio meta description test"
        self.settings.save()
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unique engineer portfolio meta description test")

    def test_home_page_when_optional_fields_missing(self):
        self.settings.public_email = ""
        self.settings.location = ""
        self.settings.short_bio = ""
        self.settings.long_bio = ""
        self.settings.availability_status = ""
        self.settings.default_meta_description = ""
        self.settings.profile_photo = None
        self.settings.resume_file = None
        self.settings.save()
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        # Check that page still renders gracefully
        self.assertContains(response, "Ptah Kouekam")

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

    def test_hero_renders_identity(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.settings.full_name)
        self.assertContains(response, "Engineer. Developer. Builder.")
        self.assertContains(response, "View Projects")
        self.assertContains(response, "Contact")

    def test_hero_without_profile_image(self):
        self.settings.profile_photo = None
        self.settings.save()
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        # Should render intentional monogram, not a broken image tag
        self.assertContains(response, "PK")

    def test_hero_without_cv(self):
        self.settings.resume_file = None
        self.settings.save()
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Download CV")

    def test_hero_with_cv(self):
        cv = SimpleUploadedFile("test_resume.pdf", b"%PDF-1.4 sample cv content", content_type="application/pdf")
        self.settings.resume_file = cv
        self.settings.save()
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Download CV")

    def test_hero_without_social_links(self):
        SocialLink.objects.all().delete()
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        # When no social links exist, empty state renders nothing
        self.assertNotContains(response, "Profiles:")

    def test_social_links_active_and_ordering_and_featured(self):
        SocialLink.objects.all().delete()
        s1 = SocialLink.objects.create(
            platform="github",
            display_name="GitHub Ptah",
            url="https://github.com/kouekamluc",
            display_order=2,
            is_active=True,
            show_in_hero=True,
            featured=False
        )
        s2 = SocialLink.objects.create(
            platform="linkedin",
            display_name="LinkedIn Ptah",
            url="https://linkedin.com/in/ptahkouekam",
            display_order=1,
            is_active=True,
            show_in_hero=True,
            featured=True
        )
        s3 = SocialLink.objects.create(
            platform="x",
            display_name="Inactive Link",
            url="https://x.com/inactive",
            display_order=0,
            is_active=False,
            show_in_hero=True
        )

        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GitHub Ptah")
        self.assertContains(response, "LinkedIn Ptah")
        self.assertNotContains(response, "Inactive Link")
        self.assertContains(response, "featured")
        
        # Test property alias and auto icon population
        self.assertTrue(s1.active)
        self.assertFalse(s3.active)
        self.assertEqual(s1.icon_identifier, "github")
        self.assertEqual(s2.icon_identifier, "linkedin")

    def test_featured_projects_homepage_section(self):
        import datetime
        cat = ProjectCategory.objects.create(name="Mechatronics Section")
        p_feat = Project.objects.create(
            title="Featured Quadruped",
            tagline="Legged locomotion rig",
            project_type="mechatronics",
            category=cat,
            status="prototype",
            start_date=datetime.date(2024, 1, 1),
            is_featured=True,
            is_published=True,
            overview="Featured robot rig"
        )
        p_non_feat = Project.objects.create(
            title="Hidden Sensor Module",
            tagline="Low priority bench sensor",
            project_type="electronics",
            category=cat,
            status="completed",
            start_date=datetime.date(2023, 1, 1),
            is_featured=False,
            is_published=True,
            overview="Non-featured bench sensor"
        )
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Featured Quadruped")
        self.assertContains(response, "Featured Engineering & Systems")
        # In featured section, non-featured project should not appear
        featured_list = response.context["featured_projects"]
        self.assertIn(p_feat, featured_list)
        self.assertNotIn(p_non_feat, featured_list)

    def test_featured_projects_empty_state_hidden(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="featured-projects"')

    def test_currently_building_homepage_section(self):
        import datetime
        cat = ProjectCategory.objects.create(name="Lab Builds")
        active_p = Project.objects.create(
            title="Active IMU Rig",
            tagline="Kalman filter calibration bench",
            project_type="mechatronics",
            category=cat,
            status="in_development",
            next_milestone="Bench calibration test",
            start_date=datetime.date(2025, 1, 1),
            is_published=True,
            overview="Active development rig"
        )
        completed_p = Project.objects.create(
            title="Old Completed Motor Driver",
            tagline="Finished stepper driver",
            project_type="electronics",
            category=cat,
            status="completed",
            start_date=datetime.date(2022, 1, 1),
            is_published=True,
            overview="Completed driver"
        )
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active IMU Rig")
        self.assertContains(response, "Bench calibration test")
        cb_list = list(response.context["currently_building"])
        self.assertIn(active_p, cb_list)
        self.assertNotIn(completed_p, cb_list)

    def test_currently_building_empty_state_hidden(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="currently-building"')

    def test_custom_404_view(self):
        response = self.client.get("/non-existent-endpoint-404-check/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "ERROR 404 // SIGNAL LOST", status_code=404)

    def test_sitemap_xml(self):
        response = self.client.get(reverse("django.contrib.sitemaps.views.sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<urlset")
        self.assertContains(response, "<loc>")

    def test_organization_and_timeline_models(self):
        import datetime
        from .models import Organization
        org = Organization.objects.create(name="KKEVO Tech", role="Founder")
        self.assertEqual(str(org), "KKEVO Tech (Founder)")

        edu = Education.objects.create(
            degree="B.Sc. Mechatronics",
            institution="Polytechnic in Italy",
            start_date=datetime.date(2023, 10, 1)
        )
        self.assertEqual(str(edu), "B.Sc. Mechatronics - Polytechnic in Italy")

        tl = TimelineItem.objects.create(
            title="Firmware Milestone",
            organization="Lab",
            start_date=datetime.date(2024, 3, 1)
        )
        self.assertEqual(str(tl), "Firmware Milestone @ Lab")
