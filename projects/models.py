from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class ProjectCategory(models.Model):
    """Categorization for projects across multidisciplinary engineering & software domains."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Project Category"
        verbose_name_plural = "Project Categories"
        ordering = ["display_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Project(models.Model):
    """
    Comprehensive Project model supporting both software systems and physical engineering systems
    (Mechatronics, Arduino, ESP32, analogue/digital circuits, control loops, and CAD).
    """
    TYPE_CHOICES = [
        ("mechatronics", "Mechatronics & Robotics"),
        ("software", "Software & Web Systems"),
        ("embedded", "Embedded & IoT Systems"),
        ("electronics", "Analogue & Digital Electronics"),
        ("control", "Control Systems & Automation"),
        ("research", "Research & Scientific Computing"),
        ("experimental", "Hardware Experiments"),
        ("university", "University Engineering Coursework"),
        ("other", "Other Technology Project"),
    ]

    STATUS_CHOICES = [
        ("concept", "Concept & Planning"),
        ("in_development", "In Development"),
        ("prototype", "Prototype Built"),
        ("testing", "Testing & Verification"),
        ("completed", "Completed"),
        ("maintained", "Actively Maintained"),
        ("archived", "Archived"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    tagline = models.CharField(
        max_length=255,
        help_text="Concise one-line summary displayed on project cards"
    )
    project_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="software")
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="projects"
    )
    technologies = models.ManyToManyField(
        "core.Technology",
        blank=True,
        related_name="projects",
        help_text="Technologies, sensors, languages, or tools utilized"
    )
    thumbnail = models.ImageField(
        upload_to="projects/thumbnails/",
        blank=True,
        null=True,
        help_text="Card preview image (16:9 or 4:3 recommended)"
    )
    hero_image = models.ImageField(
        upload_to="projects/hero/",
        blank=True,
        null=True,
        help_text="Wide header visual or banner"
    )
    start_date = models.DateField(help_text="Project initiation date")
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Completion date (leave empty if ongoing or maintained)"
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="in_development")
    is_featured = models.BooleanField(
        default=False,
        help_text="If checked, prioritized in the homepage showcase"
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Toggle public visibility"
    )

    # Repository & Demonstration Links
    github_url = models.URLField(blank=True, help_text="Repository URL (e.g. GitHub/GitLab)")
    live_url = models.URLField(blank=True, help_text="Live web deployment or interactive demonstration")
    documentation_url = models.URLField(blank=True, help_text="Technical manual, Sphinx/MkDocs, or datasheet")
    video_url = models.URLField(blank=True, help_text="YouTube/Vimeo demonstration or prototype recording")

    # In-Depth Case Study Sections (Omissible when not applicable)
    overview = models.TextField(help_text="High-level engineering problem and system purpose")
    problem = models.TextField(blank=True, help_text="Underlying technical difficulty or motivation")
    objectives = models.TextField(blank=True, help_text="Target performance, specs, or requirements")
    system_architecture = models.TextField(
        blank=True,
        help_text="Hardware blocks, communication protocols (SPI, I2C, UART), or software diagrams"
    )
    hardware_specs = models.TextField(
        blank=True,
        help_text="Microcontrollers, sensors, operational amplifiers, actuators, power stages"
    )
    software_stack_details = models.TextField(
        blank=True,
        help_text="Firmware algorithms, Django architecture, API endpoints, or database structures"
    )
    engineering_process = models.TextField(
        blank=True,
        help_text="Iteration chronology: modeling -> circuit prototyping -> PCB -> firmware -> testing"
    )
    challenges = models.TextField(blank=True, help_text="Unforeseen obstacles, noise issues, bugs, or physical limits")
    solution = models.TextField(blank=True, help_text="Decisions made to achieve target performance")
    quantitative_results = models.TextField(
        blank=True,
        help_text="Measured data, error bounds, frequency response, efficiency, or benchmarks"
    )
    lessons_learned = models.TextField(blank=True, help_text="Key takeaways and engineering insights")
    future_improvements = models.TextField(blank=True, help_text="Next revisions, PCB spins, or feature additions")

    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["display_order", "-start_date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"slug": self.slug})

    @property
    def year_display(self):
        if self.start_date:
            if self.end_date and self.end_date.year != self.start_date.year:
                return f"{self.start_date.year} - {self.end_date.year}"
            elif not self.end_date:
                return f"{self.start_date.year} - Present"
            return str(self.start_date.year)
        return ""

    @property
    def is_hardware_project(self):
        return self.project_type in ["mechatronics", "embedded", "electronics", "control", "experimental"]

    def __str__(self):
        return self.title


class ProjectMetric(models.Model):
    """
    Quantitative engineering specifications and measurements (e.g. '1 kHz Loop Rate', '0.2% Linearity').
    Supports engineering rigour without pseudo-percentages.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="metrics")
    label = models.CharField(max_length=100, help_text="e.g. Sampling Rate, Operating Voltage, Latency, Bandwidth")
    value = models.CharField(max_length=100, help_text="e.g. 500 Hz, 3.3V / 5V DC, < 2.5 ms, 99.4%")
    description = models.CharField(max_length=255, blank=True, help_text="Context or measurement conditions")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Project Metric"
        verbose_name_plural = "Project Metrics"
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.label}: {self.value}"


class ProjectImage(models.Model):
    """Visual engineering documentation: CAD renderings, schematics, test waveforms, prototypes."""
    IMAGE_TYPE_CHOICES = [
        ("photo", "Hardware Prototype / Rig"),
        ("schematic", "Circuit Schematic"),
        ("cad", "CAD / Mechanical Assembly"),
        ("diagram", "System Block Diagram"),
        ("screenshot", "Software Interface"),
        ("plot", "Measurement / Oscilloscope Plot"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=255, blank=True)
    image_type = models.CharField(max_length=30, choices=IMAGE_TYPE_CHOICES, default="photo")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Project Image"
        verbose_name_plural = "Project Images"
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"Image for {self.project.title} - {self.get_image_type_display()}"


class ProjectFile(models.Model):
    """Downloadable engineering assets: BOMs, technical reports, datasheets, or schematics."""
    FILE_TYPE_CHOICES = [
        ("bom", "Bill of Materials (BOM)"),
        ("schematic", "Circuit Schematic / PCB"),
        ("report", "Technical / Experimental Report"),
        ("datasheet", "Datasheet / Component Spec"),
        ("code", "Firmware / Source Archive"),
        ("other", "Other Asset"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="files")
    title = models.CharField(max_length=200, help_text="e.g. System Bill of Materials v1.2")
    file = models.FileField(upload_to="projects/files/")
    file_type = models.CharField(max_length=30, choices=FILE_TYPE_CHOICES, default="report")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Project File"
        verbose_name_plural = "Project Files"
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.title} ({self.project.title})"
