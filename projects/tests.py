import datetime
from django.test import TestCase, Client
from django.urls import reverse
from core.models import Technology, TechnologyCategory
from .models import Project, ProjectCategory, ProjectMetric


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
