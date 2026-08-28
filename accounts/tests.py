from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse


class AccountsAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_user_change_page_contains_profile_inline(self):
        response = self.client.get(
            reverse("admin:accounts_user_change", args=(self.admin_user.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "profile-TOTAL_FORMS")

    def test_profile_admin_page_is_available(self):
        response = self.client.get(reverse("admin:accounts_profile_changelist"))

        self.assertEqual(response.status_code, 200)


class EnsureSuperuserCommandTests(TestCase):
    environment = {
        "DJANGO_SUPERUSER_USERNAME": "render-admin",
        "DJANGO_SUPERUSER_EMAIL": "render-admin@example.com",
        "DJANGO_SUPERUSER_PASSWORD": "A-strong-render-password-4829!",
    }

    @patch.dict("os.environ", environment, clear=False)
    def test_command_creates_superuser(self):
        call_command("ensure_superuser")

        user = get_user_model().objects.get(username="render-admin")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.email, "render-admin@example.com")
        self.assertTrue(user.check_password(self.environment["DJANGO_SUPERUSER_PASSWORD"]))

    @patch.dict("os.environ", environment, clear=False)
    def test_command_is_idempotent_and_does_not_reset_existing_password(self):
        User = get_user_model()
        User.objects.create_superuser(
            username="render-admin",
            email="old@example.com",
            password="A-different-existing-password-9317!",
        )

        call_command("ensure_superuser")

        user = User.objects.get(username="render-admin")
        self.assertEqual(User.objects.filter(username="render-admin").count(), 1)
        self.assertEqual(user.email, "render-admin@example.com")
        self.assertTrue(user.check_password("A-different-existing-password-9317!"))

    @patch.dict(
        "os.environ",
        {
            "DJANGO_SUPERUSER_USERNAME": "",
            "DJANGO_SUPERUSER_EMAIL": "",
            "DJANGO_SUPERUSER_PASSWORD": "",
        },
        clear=False,
    )
    def test_command_rejects_missing_environment_variables(self):
        with self.assertRaises(CommandError):
            call_command("ensure_superuser")
