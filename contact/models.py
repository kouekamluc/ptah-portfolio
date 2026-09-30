from django.db import models


class ContactMessage(models.Model):
    """
    Submissions from the professional contact form.
    Stores inquiries safely in Django Admin with honeypot spam protection.
    """
    name = models.CharField(max_length=150)
    email = models.EmailField()
    organization = models.CharField(
        max_length=150,
        blank=True,
        help_text="Company, university, or lab affiliation (optional)"
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} from {self.name} ({self.email})"
