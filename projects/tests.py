import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from core.models import Technology, TechnologyCategory
from .models import Project, ProjectCategory, ProjectMetric, ProjectImage


class ProjectModelAndViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = ProjectCategory.objects.create(name="Mechatronics")
        self.tcat = TechnologyCategory.objects.create(name="Embedded")
        self.tech = Technology.objects.create(category=self.tcat, name="Arduino")
        
        self.project = Project.objects.create(
            title="Balancing Robot",
            tagline="Inverted pendulum closed loop balance",
            project_type="mechatronics",
            category=self.cat,
            status="prototype",
            start_date=datetime.date(2024, 1, 1),
            is_featured=True,
            is_published=True,
            overview="Closed-loop balance rig",
            challenges="IMU vibration noise",
            solution="Low-pass filter derivative term"
        )
        self.project.technologies.add(self.tech)
        self.metric = ProjectMetric.objects.create(
            project=self.project,
            label="Loop Rate",
            value="200 Hz"
        )

    def test_project_model(self):
        self.assertEqual(self.project.slug, "balancing-robot")
        self.assertTrue(self.project.is_hardware_project)
        self.assertEqual(self.project.year_display, "2024 - Present")
        # Test property aliases
        self.assertEqual(self.project.short_description, self.project.tagline)
        self.assertEqual(self.project.full_description, self.project.overview)
        self.assertEqual(self.project.featured, self.project.is_featured)
        self.assertEqual(self.project.results, self.project.quantitative_results)

    def test_project_date_validation(self):
        # End date earlier than start date must raise ValidationError
        invalid_project = Project(
            title="Invalid Date Project",
            tagline="Timing paradox",
            project_type="mechatronics",
            category=self.cat,
            status="planning",
            start_date=datetime.date(2025, 6, 1),
            end_date=datetime.date(2025, 1, 1),
            overview="Testing date validator"
        )
        with self.assertRaises(ValidationError):
            invalid_project.clean()

    def test_project_image_alt_text_fallback(self):
        img = ProjectImage(
            project=self.project,
            caption="Oscilloscope trace of closed-loop step response",
            image_type="plot"
        )
        img.save()
        self.assertEqual(img.alt_text, "Oscilloscope trace of closed-loop step response")

    def test_project_ordering_and_status(self):
        p1 = Project.objects.create(
            title="Alpha Project",
            tagline="Alpha",
            project_type="software",
            category=self.cat,
            status="planning",
            start_date=datetime.date(2023, 1, 1),
            display_order=10,
            overview="Alpha overview"
        )
        p2 = Project.objects.create(
            title="Beta Project",
            tagline="Beta",
            project_type="software",
            category=self.cat,
            status="completed",
            start_date=datetime.date(2024, 1, 1),
            display_order=1,
            overview="Beta overview"
        )
        projects = list(Project.objects.all())
        # Display order 0 (balancing robot) should come first, then display_order 1 (Beta), then 10 (Alpha)
        self.assertEqual(projects[0], self.project)
        self.assertEqual(projects[1], p2)
        self.assertEqual(projects[2], p1)

    def test_project_list_view(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Balancing Robot")
        self.assertTemplateUsed(response, "projects/list.html")

    def test_project_list_htmx(self):
        response = self.client.get(reverse("projects:list"), {"q": "balance"}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/partials/project_grid.html")
        self.assertContains(response, "Balancing Robot")

    def test_project_detail_view(self):
        response = self.client.get(reverse("projects:detail", kwargs={"slug": self.project.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Balancing Robot")
        self.assertContains(response, "200 Hz")
        self.assertContains(response, "Closed-loop balance rig")

    def test_engineering_view(self):
        response = self.client.get(reverse("projects:engineering"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mechatronics & Physical Engineering")
        self.assertContains(response, "Balancing Robot")

    def test_unpublished_project_visibility(self):
        unpublished = Project.objects.create(
            title="Secret Prototype",
            tagline="Internal experiment",
            project_type="experimental",
            category=self.cat,
            status="concept",
            start_date=datetime.date(2024, 1, 1),
            is_published=False,
            overview="Private research"
        )
        # Anonymous visitor should get 404
        response = self.client.get(reverse("projects:detail", kwargs={"slug": unpublished.slug}))
        self.assertEqual(response.status_code, 404)

        # Staff user should be able to view it
        from django.contrib.auth import get_user_model
        User = get_user_model()
        staff_user = User.objects.create_user(username="staff", password="password123", is_staff=True)
        self.client.login(username="staff", password="password123")
        response_staff = self.client.get(reverse("projects:detail", kwargs={"slug": unpublished.slug}))
        self.assertEqual(response_staff.status_code, 200)
        self.assertContains(response_staff, "Secret Prototype")

    def test_project_category_filtering(self):
        # Filtering by existing category
        response = self.client.get(reverse("projects:list"), {"category": self.cat.slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Balancing Robot")

        # Filtering by non-existent category
        response_empty = self.client.get(reverse("projects:list"), {"category": "non-existent-cat"})
        self.assertEqual(response_empty.status_code, 200)
        self.assertNotContains(response_empty, "Balancing Robot")

    def test_project_status_filtering(self):
        # self.project status is 'prototype'
        res_match = self.client.get(reverse("projects:list"), {"status": "prototype"})
        self.assertEqual(res_match.status_code, 200)
        self.assertContains(res_match, "Balancing Robot")

        res_nomatch = self.client.get(reverse("projects:list"), {"status": "completed"})
        self.assertEqual(res_nomatch.status_code, 200)
        self.assertNotContains(res_nomatch, "Balancing Robot")

    def test_project_technology_filtering(self):
        # self.project has tech "Arduino" (slug: "arduino")
        res_tech = self.client.get(reverse("projects:list"), {"technology": "arduino"})
        self.assertEqual(res_tech.status_code, 200)
        self.assertContains(res_tech, "Balancing Robot")

        res_tech_short = self.client.get(reverse("projects:list"), {"tech": "arduino"})
        self.assertEqual(res_tech_short.status_code, 200)
        self.assertContains(res_tech_short, "Balancing Robot")

    def test_project_pagination(self):
        # Create additional projects to exceed paginate_by = 9
        for i in range(12):
            Project.objects.create(
                title=f"Batch Project {i}",
                tagline=f"Tagline {i}",
                project_type="software",
                category=self.cat,
                status="completed",
                start_date=datetime.date(2024, 1, 1),
                overview="Overview"
            )
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["projects"]), 9)
        # Check page 2
        response_p2 = self.client.get(reverse("projects:list"), {"page": 2})
        self.assertEqual(response_p2.status_code, 200)
        self.assertEqual(len(response_p2.context["projects"]), 4)

    def test_project_list_ordering_featured_first(self):
        Project.objects.all().delete()
        p_normal = Project.objects.create(
            title="Normal Project",
            tagline="Normal",
            project_type="software",
            category=self.cat,
            status="completed",
            start_date=datetime.date(2025, 1, 1),
            is_featured=False,
            display_order=1,
            overview="Normal"
        )
        p_featured = Project.objects.create(
            title="Featured Project",
            tagline="Featured",
            project_type="software",
            category=self.cat,
            status="completed",
            start_date=datetime.date(2023, 1, 1),
            is_featured=True,
            display_order=5,
            overview="Featured"
        )
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)
        projects = list(response.context["projects"])
        self.assertEqual(projects[0], p_featured)
        self.assertEqual(projects[1], p_normal)
