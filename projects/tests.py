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
