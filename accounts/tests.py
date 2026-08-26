from django.contrib.auth import get_user_model
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
