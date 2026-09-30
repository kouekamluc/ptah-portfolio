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
            highlighted=True,
            url="https://espressif.com"
        )
        self.assertEqual(str(tech), "ESP32 (Embedded Hardware)")
        self.assertEqual(tech.slug, "esp32")
        self.assertTrue(tech.featured)
        self.assertEqual(tech.website_url, "https://espressif.com")
        self.assertTrue(tech.is_active)


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
        self.assertContains(response, "Ptah Kouekam")
        self.assertContains(response, "Who I Am")

    def test_stack_page(self):
        # Create an inactive technology
        hidden_tech = Technology.objects.create(
            category=self.cat,
            name="Deprecated Framework",
            is_active=False
        )
        # Create an empty category with 0 technologies
        empty_cat = TechnologyCategory.objects.create(name="Empty Category", display_order=99)

        response = self.client.get(reverse("core:stack"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Technologies & Engineering Stack")
        self.assertContains(response, "Django")
        self.assertNotContains(response, "Deprecated Framework")
        self.assertNotContains(response, "Empty Category")

    def test_search_view_regular(self):
        response = self.client.get(reverse("core:search"), {"q": "Django"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django")

    def test_search_view_htmx(self):
        response = self.client.get(reverse("core:search"), {"q": "Django"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/partials/search_results.html")

    def test_search_matching_project_note_technology_and_empty(self):
        import datetime
        from notes.models import Note, NoteCategory
        # Create Project
        cat = ProjectCategory.objects.create(name="Automation")
        p = Project.objects.create(
            title="Telemetry Micro-Rover",
            tagline="Sub-miniature autonomous rover",
            project_type="mechatronics",
            category=cat,
            status="prototype",
            start_date=datetime.date(2024, 1, 1),
            overview="Autonomous rover chassis and telemetry testbench.",
            is_published=True
        )
        # Create Note
        note_cat = NoteCategory.objects.create(name="Sensors")
        n = Note.objects.create(
            title="IMU Noise Filtering Guide",
            excerpt="Complementary filter practical derivation",
            content_markdown="Kalman vs complementary filters",
            category=note_cat,
            is_published=True
        )

        # 1. Matching project
        res_p = self.client.get(reverse("core:search"), {"q": "Rover"})
        self.assertEqual(res_p.status_code, 200)
        self.assertContains(res_p, "Telemetry Micro-Rover")

        # 2. Matching note
        res_n = self.client.get(reverse("core:search"), {"q": "Filtering"})
        self.assertEqual(res_n.status_code, 200)
        self.assertContains(res_n, "IMU Noise Filtering Guide")

        # 3. Matching technology
        res_t = self.client.get(reverse("core:search"), {"q": "Django"})
        self.assertEqual(res_t.status_code, 200)
        self.assertContains(res_t, "Django")

        # 4. No results
        res_none = self.client.get(reverse("core:search"), {"q": "xyznonexistentquery999"})
        self.assertEqual(res_none.status_code, 200)
        self.assertContains(res_none, "No items matched your search query")

        # 5. Empty query
        res_empty = self.client.get(reverse("core:search"), {"q": ""})
        self.assertEqual(res_empty.status_code, 200)
        self.assertContains(res_empty, "Type above to search")

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

    def test_resume_model_activation_and_uniqueness(self):
        from .models import Resume
        Resume.objects.all().delete()
        pdf_file1 = SimpleUploadedFile("resume_v1.pdf", b"%PDF-1.4 content1", content_type="application/pdf")
        pdf_file2 = SimpleUploadedFile("resume_v2.pdf", b"%PDF-1.4 content2", content_type="application/pdf")
        
        r1 = Resume.objects.create(title="CV 2024", version="1.0", file=pdf_file1, active=True)
        self.assertTrue(r1.active)

        # Activating r2 should deactivate r1
        r2 = Resume.objects.create(title="CV 2025", version="2.0", file=pdf_file2, active=True)
        r1.refresh_from_db()
        self.assertFalse(r1.active)
        self.assertTrue(r2.active)

        # Non-PDF validation
        bad_file = SimpleUploadedFile("malicious.exe", b"binary", content_type="application/x-msdownload")
        bad_resume = Resume(title="Bad CV", version="0.1", file=bad_file, active=False)
        with self.assertRaises(ValidationError):
            bad_resume.full_clean()

    def test_resume_active_download_and_visibility(self):
        from .models import Resume
        Resume.objects.all().delete()
        self.settings.resume_file = None
        self.settings.save()

        # No resume: verify hero, about, contact hide the button
        res_home = self.client.get(reverse("core:home"))
        self.assertNotContains(res_home, "Download CV")

        res_about = self.client.get(reverse("core:about"))
        self.assertNotContains(res_about, "Download Curriculum Vitae")

        res_contact = self.client.get(reverse("contact:index"))
        self.assertNotContains(res_contact, "Download Curriculum Vitae")

        # Inactive resume: still hidden
        pdf_file = SimpleUploadedFile("my_resume.pdf", b"%PDF-1.4 active cv test", content_type="application/pdf")
        res_obj = Resume.objects.create(title="Ptah CV", version="1.0", file=pdf_file, active=False)
        
        res_dl = self.client.get(reverse("core:cv_download"))
        self.assertRedirects(res_dl, reverse("contact:index"))

        # Active resume: visible on all 3 pages, and download redirects to file url
        res_obj.active = True
        res_obj.save()

        res_dl_active = self.client.get(reverse("core:cv_download"))
        self.assertEqual(res_dl_active.status_code, 302)
        self.assertIn("my_resume", res_dl_active.url)

        res_home_active = self.client.get(reverse("core:home"))
        self.assertContains(res_home_active, "Download CV")

        res_about_active = self.client.get(reverse("core:about"))
        self.assertContains(res_about_active, "Download Curriculum Vitae")

        res_contact_active = self.client.get(reverse("contact:index"))
        self.assertContains(res_contact_active, "Download Curriculum Vitae")

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

    def test_seo_metadata_and_structured_data(self):
        import datetime
        from notes.models import Note, NoteCategory
        from projects.models import Project, ProjectCategory

        # Test home page canonical and Person schema
        res_home = self.client.get(reverse("core:home"))
        self.assertEqual(res_home.status_code, 200)
        self.assertContains(res_home, '<link rel="canonical" href="http://testserver/">')
        self.assertContains(res_home, '"@type": "Person"')
        self.assertContains(res_home, self.settings.full_name)

        # Test note detail schema
        note_cat = NoteCategory.objects.create(name="Control Theory Testing")
        note = Note.objects.create(
            title="Kalman Filter Tuning",
            excerpt="Covariance matrix tuning",
            content_markdown="State estimation formulas.",
            category=note_cat,
            is_published=True
        )
        res_note = self.client.get(reverse("notes:detail", kwargs={"slug": note.slug}))
        self.assertEqual(res_note.status_code, 200)
        self.assertContains(res_note, '"@type": "TechArticle"')
        self.assertContains(res_note, "Kalman Filter Tuning")
        self.assertContains(res_note, '<link rel="canonical"')

        # Test project detail schema
        proj_cat = ProjectCategory.objects.create(name="Embedded Builds")
        proj = Project.objects.create(
            title="CAN Bus Telemetry Rig",
            tagline="Automotive CAN diagnostic unit",
            project_type="embedded",
            category=proj_cat,
            status="completed",
            start_date=datetime.date(2024, 1, 1),
            overview="CAN bus telemetry logger",
            is_published=True
        )
        res_proj = self.client.get(reverse("projects:detail", kwargs={"slug": proj.slug}))
        self.assertEqual(res_proj.status_code, 200)
        self.assertContains(res_proj, '"@type": "TechArticle"')
        self.assertContains(res_proj, "CAN Bus Telemetry Rig")
        self.assertContains(res_proj, '<link rel="canonical"')

    def test_organization_and_timeline_models(self):
        import datetime
        from .models import Organization
        org = Organization.objects.create(name="KKEVO Tech", role="Founder")
        self.assertEqual(str(org), "KKEVO Tech (Founder)")

        edu = Education.objects.create(
            degree="B.Sc. Mechatronics",
            institution="Polytechnic in Italy",
            start_date=datetime.date(2023, 10, 1),
            is_current=True,
            coursework="Dynamics, Control, Circuits"
        )
        self.assertEqual(str(edu), "B.Sc. Mechatronics - Polytechnic in Italy")
        self.assertEqual(edu.program, "B.Sc. Mechatronics")
        self.assertTrue(edu.currently_enrolled)
        self.assertEqual(edu.relevant_coursework, "Dynamics, Control, Circuits")

        tl = TimelineItem.objects.create(
            title="Firmware Milestone",
            organization="Lab",
            item_type="milestone",
            is_current=True,
            start_date=datetime.date(2024, 3, 1)
        )
        self.assertEqual(str(tl), "Firmware Milestone @ Lab")
        self.assertEqual(tl.type, "milestone")
        self.assertTrue(tl.current)

    def test_about_page_detailed(self):
        import datetime
        Education.objects.all().delete()
        TimelineItem.objects.all().delete()

        # Test empty state for optional sections
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Understand &rarr; Model &rarr; Build &rarr; Measure &rarr; Improve")
        self.assertNotContains(response, "Academic Engineering Studies")
        self.assertNotContains(response, "Milestone Chronology & Experience")

        # Now create an active education and completed timeline item
        edu = Education.objects.create(
            degree="B.Sc. Engineering Science",
            institution="Italian University",
            start_date=datetime.date(2023, 9, 1),
            is_current=True
        )
        tl = TimelineItem.objects.create(
            title="Embedded Robotics Project",
            organization="Independent Research",
            item_type="project",
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 6, 1),
            is_current=False
        )

        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Academic Engineering Studies")
        self.assertContains(response, "B.Sc. Engineering Science")
        self.assertContains(response, "Present")
        self.assertContains(response, "Milestone Chronology & Experience")
        self.assertContains(response, "Embedded Robotics Project")

    def test_organization_relationships_and_display(self):
        import datetime
        from .models import Organization
        from projects.models import Project, ProjectCategory

        Organization.objects.all().delete()

        cat = ProjectCategory.objects.create(name="Initiatives Category")
        proj = Project.objects.create(
            title="KKEVO Media Platform",
            tagline="Engineering media and tech publication",
            project_type="software",
            category=cat,
            status="in_development",
            start_date=datetime.date(2024, 1, 1),
            overview="Technical media brand",
            is_published=True
        )

        org_active = Organization.objects.create(
            name="KKEVO Technology Network",
            role="Creator & Technical Lead",
            description="Technical journalism and open engineering community.",
            start_date=datetime.date(2024, 2, 1),
            is_active=True,
            display_order=1
        )
        org_active.associated_projects.add(proj)
        self.assertEqual(org_active.period, "2024 - Present")
        self.assertTrue(org_active.active)
        self.assertIn(proj, org_active.associated_projects.all())

        org_inactive = Organization.objects.create(
            name="Archived Lab Initiative",
            role="Former Researcher",
            description="Inactive student project.",
            is_active=False
        )

        # Home page display
        res_home = self.client.get(reverse("core:home"))
        self.assertEqual(res_home.status_code, 200)
        self.assertContains(res_home, "KKEVO Technology Network")
        self.assertContains(res_home, "KKEVO Media Platform")
        self.assertNotContains(res_home, "Archived Lab Initiative")

        # About page display
        res_about = self.client.get(reverse("core:about"))
        self.assertEqual(res_about.status_code, 200)
        self.assertContains(res_about, "KKEVO Technology Network")
        self.assertContains(res_about, "KKEVO Media Platform")
        self.assertNotContains(res_about, "Archived Lab Initiative")

