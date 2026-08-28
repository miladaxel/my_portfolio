from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import storages


def resume_storage():
    return storages["raw_media"]


class User(AbstractUser):
    # Add any additional fields you want for your custom user model
    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    short_bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    resume = models.FileField(
        upload_to='resume/',
        blank=True,
        null=True,
        storage=resume_storage,
    )
    updated_at = models.DateTimeField(auto_now=True)
