from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class SiteSettings(models.Model):
    """
    Singleton model holding global personal identity, SEO defaults, and site settings.
    Ensures zero hardcoding of titles, bio, and credentials across templates.
    """
    full_name = models.CharField(
        max_length=200,
        default="Ptah Kouekam Kamgou Luc Kevin",
        help_text="Full legal/professional name"
    )
    professional_title = models.CharField(
        max_length=200,
        default="Engineer. Developer. Builder.",
        help_text="Concise professional positioning (e.g. 'Engineer. Developer. Builder.')"
    )
    short_bio = models.TextField(
        default=(
            "Engineering student studying Mechatronics Engineering and Engineering Science in Italy. "
            "Building at the intersection of embedded electronics, mechanical systems, and robust software."
        ),
        help_text="Displayed in the hero section and SEO meta descriptions"
    )
    long_bio = models.TextField(
        blank=True,
        help_text="Detailed personal narrative used on the About page"
    )
    location = models.CharField(
        max_length=150,
        default="Italy",
        help_text="General location (country/city)"
    )
    public_email = models.EmailField(
        blank=True,
        help_text="Public contact email displayed if configured"
    )
    
    STATUS_CHOICES = [
        ("available", "Open to opportunities"),
        ("collab", "Open to collaboration"),
        ("research", "Focused on studies & research"),
        ("busy", "Currently unavailable"),
    ]
    availability_status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="collab",
        help_text="Current professional availability indicator"
    )
    
    profile_photo = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True,
        help_text="High-resolution professional photo"
    )
    hero_image = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True,
        help_text="Engineering workshop, CAD, or secondary hero visual"
    )
    resume_file = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True,
        help_text="Active CV/Resume document (PDF format recommended)"
    )
    resume_version = models.CharField(
        max_length=50,
        default="2026.1",
        blank=True,
        help_text="Version identifier for the active CV"
    )
    footer_text = models.CharField(
        max_length=255,
        default="Designed & engineered with precision using Django, HTMX, and Tailwind CSS.",
        help_text="Brief technical or philosophical note in footer"
    )
    seo_meta_keywords = models.CharField(
        max_length=300,
        default="Mechatronics, Engineering, Embedded Systems, Django, Arduino, ESP32, Python, Electronics, Control Systems",
        help_text="Comma-separated keywords for meta tags"
    )
    opengraph_image = models.ImageField(
        upload_to="seo/",
        blank=True,
        null=True,
        help_text="Social preview image (1200x630px recommended)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def clean(self):
        # Enforce singleton pattern: only one instance can exist
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError("There can only be one SiteSettings instance.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Fetch singleton instance, creating a default one if none exists."""
        settings, _ = cls.objects.get_or_create(id=1)
        return settings

    def __str__(self):
        return f"Site Settings ({self.full_name})"


class TechnologyCategory(models.Model):
    """Broad classification for technical skills and stack components."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Technology Category"
        verbose_name_plural = "Technology Categories"
        ordering = ["display_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Technology(models.Model):
    """Individual tools, programming languages, CAD software, and hardware frameworks."""
    PROFICIENCY_CHOICES = [
        ("learning", "Learning"),
        ("working", "Working knowledge"),
        ("comfortable", "Comfortable"),
        ("strong", "Strong"),
        ("advanced", "Advanced"),
    ]

    category = models.ForeignKey(
        TechnologyCategory,
        on_delete=models.CASCADE,
        related_name="technologies"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon_svg = models.TextField(
        blank=True,
        help_text="Inline SVG markup or SVG path for crisp rendering without third-party CDN fonts"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief note on how and where this technology is used"
    )
    proficiency = models.CharField(
        max_length=20,
        choices=PROFICIENCY_CHOICES,
        blank=True,
        null=True,
        help_text="Optional proficiency assessment"
    )
    years_used = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        help_text="Optional years of active exposure"
    )
    highlighted = models.BooleanField(
        default=False,
        help_text="If checked, displayed in the homepage skills snapshot"
    )
    url = models.URLField(
        blank=True,
        help_text="Official documentation or project URL"
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Technology"
        verbose_name_plural = "Technologies"
        ordering = ["category__display_order", "display_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class CurrentlyBuilding(models.Model):
    """Real-time active engineering prototypes, software builds, or research projects."""
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Brief technical summary of current state")
    status = models.CharField(
        max_length=100,
        default="In Active Prototyping",
        help_text="e.g. 'Fabricating test rig', 'Writing firmware', 'Drafting control loop'"
    )
    progress = models.PositiveIntegerField(
        default=50,
        help_text="Estimated progress percentage (0 - 100)"
    )
    category = models.CharField(
        max_length=100,
        default="Mechatronics & Embedded",
        help_text="e.g. Embedded Systems, Django Web, Robotics"
    )
    link = models.URLField(blank=True, help_text="Optional link to repository or issue tracker")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Currently Building Item"
        verbose_name_plural = "Currently Building Items"
        ordering = ["display_order", "-updated_at"]

    def __str__(self):
        return f"{self.title} [{self.status}]"


class TimelineItem(models.Model):
    """Unified chronological record: Education, Experience, Milestones, Certifications."""
    TYPE_CHOICES = [
        ("education", "Education"),
        ("experience", "Experience / Roles"),
        ("milestone", "Milestone"),
        ("achievement", "Achievement / Award"),
        ("certification", "Certification"),
        ("initiative", "Organization / Project"),
    ]

    title = models.CharField(max_length=200, help_text="Degree, role, or milestone title")
    organization = models.CharField(max_length=200, help_text="University, lab, company, or organization")
    location = models.CharField(max_length=150, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True, help_text="Leave blank if currently ongoing")
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="experience")
    url = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Timeline Item"
        verbose_name_plural = "Timeline Items"
        ordering = ["-is_current", "-start_date", "display_order"]

    def __str__(self):
        return f"{self.title} @ {self.organization}"


class Education(models.Model):
    """Dedicated academic background record ensuring precise, transparent representation."""
    institution = models.CharField(max_length=250, default="University in Italy")
    degree = models.CharField(
        max_length=250,
        default="Bachelor of Science in Mechatronics Engineering / Engineering Science"
    )
    location = models.CharField(max_length=150, default="Italy")
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True, help_text="Expected graduation date or completion")
    is_current = models.BooleanField(default=True)
    description = models.TextField(
        blank=True,
        help_text="Context regarding specialization, methodology, and academic rigor"
    )
    coursework = models.TextField(
        blank=True,
        help_text="Key subjects (e.g. Analogue & Digital Electronics; Control Systems; Mechanics; Machine Design; Mathematics; Physics)"
    )
    research_areas = models.TextField(
        blank=True,
        help_text="Key academic and practical areas of interest"
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Education Record"
        verbose_name_plural = "Education Records"
        ordering = ["display_order", "-start_date"]

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class SocialLink(models.Model):
    """Configurable social media profiles, repositories, and developer platforms."""
    PLATFORM_CHOICES = [
        ("github", "GitHub"),
        ("linkedin", "LinkedIn"),
        ("youtube", "YouTube"),
        ("x", "X / Twitter"),
        ("instagram", "Instagram"),
        ("facebook", "Facebook"),
        ("tiktok", "TikTok"),
        ("email", "Email"),
        ("website", "Personal / Other Site"),
    ]

    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES)
    display_name = models.CharField(max_length=100)
    url = models.URLField(help_text="Complete URL with https://")
    username = models.CharField(max_length=100, blank=True, help_text="e.g. @username")
    icon_svg = models.TextField(
        blank=True,
        help_text="Inline SVG path/markup for precise rendering"
    )
    is_active = models.BooleanField(default=True)
    show_in_hero = models.BooleanField(default=True)
    show_in_nav = models.BooleanField(default=False)
    show_in_footer = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"
        ordering = ["display_order", "display_name"]

    def __str__(self):
        return f"{self.display_name} ({self.get_platform_display()})"


class Organization(models.Model):
    """External initiatives, technology brands, student ventures, or research labs."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    role = models.CharField(max_length=150, help_text="e.g. Founder, Technical Lead, Contributor")
    description = models.TextField()
    logo = models.ImageField(upload_to="organizations/", blank=True, null=True)
    website = models.URLField(blank=True)
    period = models.CharField(max_length=100, default="2024 - Present")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Organization / Initiative"
        verbose_name_plural = "Organizations & Initiatives"
        ordering = ["display_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.role})"
