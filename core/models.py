from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


class Skill(models.Model):
    title = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='icons/', blank=True, null=True)



    def __str__(self):
        return self.title

class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        IN_PROGRESS = 'in progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'


    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    short_description = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='projects/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    display_order = models.PositiveIntegerField(default=0)
    github_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)
    skills = models.ManyToManyField('Skill', related_name='projects', blank=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)



class ProjectFeature(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProjectImage(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    caption = models.TextField(blank=True, null=True, max_length=200)
    def __str__(self):
        return f"image for {self.project.title}"


class ContactMessage(models.Model):
    telegram_validator = RegexValidator(
        regex=r"^@?[A-Za-z0-9_]{5,32}$",
        message="Enter a valid Telegram username (for example, @username).",
    )
    phone_validator = RegexValidator(
        regex=r"^\+?[0-9][0-9\s().-]{6,24}$",
        message="Enter a valid phone number.",
    )

    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    telegram_id = models.CharField(
        max_length=33,
        blank=True,
        validators=[telegram_validator],
    )
    phone = models.CharField(
        max_length=26,
        blank=True,
        validators=[phone_validator],
    )
    subject = models.CharField(max_length=200)
    message = models.TextField(max_length=5000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = (
            models.CheckConstraint(
                condition=~Q(email="") | ~Q(telegram_id="") | ~Q(phone=""),
                name="contact_message_has_contact_method",
                violation_error_message=(
                    "At least one contact method is required: email, Telegram ID, or phone."
                ),
            ),
        )

    def __str__(self):
        return f"{self.name}: {self.subject}"
