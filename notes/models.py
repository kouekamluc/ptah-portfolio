import re
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
import markdown
import bleach


class NoteCategory(models.Model):
    """Topic grouping for engineering notes and technical articles."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Note Category"
        verbose_name_plural = "Note Categories"
        ordering = ["display_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Note(models.Model):
    """
    Technical notes, engineering lab logs, and development tutorials.
    Rendered safely from Markdown to HTML with Bleach sanitization.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.TextField(
        help_text="Concise abstract or preview shown on note cards and SEO meta tags"
    )
    content_markdown = models.TextField(
        help_text="Technical content written in GitHub-flavored Markdown"
    )
    content_html = models.TextField(
        blank=True,
        editable=False,
        help_text="Compiled, sanitized HTML for safe and rapid rendering"
    )
    cover_image = models.ImageField(
        upload_to="notes/covers/",
        blank=True,
        null=True,
        help_text="Optional banner or schematic diagram"
    )
    category = models.ForeignKey(
        NoteCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="notes"
    )
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated tags (e.g. 'Control Systems, Arduino, Circuit Design')"
    )
    reading_time_minutes = models.PositiveIntegerField(
        default=5,
        help_text="Estimated reading duration in minutes"
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Toggle public availability"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature on homepage latest notes section"
    )
    published_at = models.DateTimeField(
        default=timezone.now,
        help_text="Publication timestamp"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Engineering Note"
        verbose_name_plural = "Engineering Notes"
        ordering = ["-published_at", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Calculate estimated reading time (approx. 200 words per minute)
        word_count = len(re.findall(r"\w+", self.content_markdown))
        self.reading_time_minutes = max(1, round(word_count / 200))

        # Compile Markdown to HTML
        raw_html = markdown.markdown(
            self.content_markdown,
            extensions=[
                "markdown.extensions.fenced_code",
                "markdown.extensions.tables",
                "markdown.extensions.nl2br",
                "markdown.extensions.toc",
                "markdown.extensions.codehilite",
            ]
        )

        # Sanitize HTML via bleach to prevent XSS while allowing technical formatting
        allowed_tags = bleach.sanitizer.ALLOWED_TAGS.union({
            "p", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "code", "table", "thead",
            "tbody", "tr", "th", "td", "blockquote", "hr", "br", "img", "span", "div"
        })
        allowed_attrs = {
            "*": ["class", "id"],
            "a": ["href", "title", "target", "rel"],
            "img": ["src", "alt", "title", "width", "height", "loading"],
            "code": ["class"],
        }
        self.content_html = bleach.clean(
            raw_html,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("notes:detail", kwargs={"slug": self.slug})

    @property
    def tag_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(",") if t.strip()]
        return []

    def __str__(self):
        return self.title
