from django.db import models
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