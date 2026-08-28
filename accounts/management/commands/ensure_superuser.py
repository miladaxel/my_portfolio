import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Create the environment-configured superuser if it does not exist."

    @transaction.atomic
    def handle(self, *args, **options):
        variable_names = (
            "DJANGO_SUPERUSER_USERNAME",
            "DJANGO_SUPERUSER_EMAIL",
            "DJANGO_SUPERUSER_PASSWORD",
        )
        values = {
            name: os.getenv(name, "").strip()
            for name in variable_names
        }
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise CommandError(
                "Missing required environment variables: " + ", ".join(missing)
            )

        username = values["DJANGO_SUPERUSER_USERNAME"]
        email = values["DJANGO_SUPERUSER_EMAIL"]
        password = values["DJANGO_SUPERUSER_PASSWORD"]
        User = get_user_model()

        try:
            user = User._default_manager.get(username=username)
        except User.DoesNotExist:
            candidate = User(username=username, email=email)
            try:
                validate_password(password, user=candidate)
            except ValidationError as exc:
                raise CommandError(
                    "Invalid superuser password: " + " ".join(exc.messages)
                ) from exc

            User._default_manager.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Created superuser '{username}'.")
            )
            return

        fields_to_update = []
        was_superuser = user.is_superuser

        if not user.is_staff:
            user.is_staff = True
            fields_to_update.append("is_staff")
        if not user.is_superuser:
            user.is_superuser = True
            fields_to_update.append("is_superuser")
        if user.email != email:
            user.email = email
            fields_to_update.append("email")

        if not was_superuser:
            try:
                validate_password(password, user=user)
            except ValidationError as exc:
                raise CommandError(
                    "Invalid superuser password: " + " ".join(exc.messages)
                ) from exc
            user.set_password(password)
            fields_to_update.append("password")

        if fields_to_update:
            user.save(update_fields=fields_to_update)
            self.stdout.write(
                self.style.SUCCESS(f"Updated superuser '{username}'.")
            )
        else:
            self.stdout.write(f"Superuser '{username}' already exists.")
