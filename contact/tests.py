from django.test import TestCase, Client
from django.urls import reverse
from .models import ContactMessage


class ContactViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_contact_get(self):
        response = self.client.get(reverse("contact:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Get in Touch")

    def test_contact_post_valid_standard(self):
        data = {
            "name": "Alex Vance",
            "email": "alex@example.com",
            "organization": "Black Mesa Lab",
            "subject": "Mechatronics Research",
            "message": "Interested in discussing your sensor rig.",
            "website": "",  # Empty honeypot
        }
        response = self.client.post(reverse("contact:index"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContactMessage.objects.filter(email="alex@example.com").exists())

    def test_contact_post_valid_htmx(self):
        data = {
            "name": "Elena Rostova",
            "email": "elena@example.com",
            "organization": "Robotics Institute",
            "subject": "Firmware Collaboration",
            "message": "Let us collaborate on the ESP32 project.",
            "website": "",  # Empty honeypot
        }
        response = self.client.post(reverse("contact:index"), data, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact/partials/form_status.html")
        self.assertContains(response, "Inquiry Received")
        self.assertTrue(ContactMessage.objects.filter(email="elena@example.com").exists())

    def test_contact_honeypot_spam_trap(self):
        data = {
            "name": "Spam Bot",
            "email": "bot@spam.com",
            "subject": "Buy crypto",
            "message": "Check our links",
            "website": "http://spamsite.xyz",  # Honeypot filled by bot!
        }
        response = self.client.post(reverse("contact:index"), data)
        # Should fail validation and not create ContactMessage
        self.assertFalse(ContactMessage.objects.filter(email="bot@spam.com").exists())

    def test_contact_rate_limiting(self):
        # We allow up to 3 submissions in 5 minutes
        for i in range(3):
            data = {
                "name": f"Tester {i}",
                "email": f"test{i}@example.com",
                "subject": f"Inquiry {i}",
                "message": f"Message body {i}",
                "website": "",
            }
            res = self.client.post(reverse("contact:index"), data, follow=True)
            self.assertEqual(res.status_code, 200)

        self.assertEqual(ContactMessage.objects.count(), 3)

        # 4th submission within the same session should be rate limited
        rate_limited_data = {
            "name": "Spammer",
            "email": "spammer@example.com",
            "subject": "Spam inquiry",
            "message": "Too many requests",
            "website": "",
        }
        res_4 = self.client.post(reverse("contact:index"), rate_limited_data, follow=True)
        # Should not create 4th message
        self.assertEqual(ContactMessage.objects.count(), 3)
        self.assertContains(res_4, "Rate limit reached")

    def test_contact_post_invalid_email(self):
        data = {
            "name": "Invalid Email User",
            "email": "not-an-email",
            "subject": "Question",
            "message": "Hello world",
            "website": "",
        }
        res = self.client.post(reverse("contact:index"), data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(ContactMessage.objects.filter(name="Invalid Email User").exists())

    def test_contact_post_missing_field(self):
        data = {
            "name": "Missing Message User",
            "email": "user@example.com",
            "subject": "Question",
            "message": "",  # missing required message
            "website": "",
        }
        res = self.client.post(reverse("contact:index"), data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(ContactMessage.objects.filter(name="Missing Message User").exists())
