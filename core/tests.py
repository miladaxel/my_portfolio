from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from accounts.models import Profile, User

from .models import ContactMessage, Project, ProjectFeature, Skill


class StorageConfigurationTests(SimpleTestCase):
    def test_default_storage_matches_environment(self):
        expected_backend = (
            "cloudinary_storage.storage.MediaCloudinaryStorage"
            if settings.IS_PRODUCTION
            else "django.core.files.storage.FileSystemStorage"
        )

        self.assertEqual(
            settings.STORAGES["default"]["BACKEND"],
            expected_backend,
        )

    def test_static_files_do_not_use_cloudinary(self):
        self.assertNotIn(
            "cloudinary",
            settings.STORAGES["staticfiles"]["BACKEND"].lower(),
        )

    def test_resume_storage_matches_environment(self):
        expected_backend = (
            "cloudinary_storage.storage.RawMediaCloudinaryStorage"
            if settings.IS_PRODUCTION
            else "django.core.files.storage.FileSystemStorage"
        )

        self.assertEqual(
            settings.STORAGES["raw_media"]["BACKEND"],
            expected_backend,
        )


class ProjectDetailViewTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Portfolio platform",
            fa_title="پلتفرم پورتفولیو",
            slug="portfolio-platform",
            short_description="A focused project summary.",
            fa_short_description="خلاصهٔ فارسی پروژه.",
            description="A complete project overview.",
            fa_description="معرفی کامل فارسی پروژه.",
            status=Project.Status.COMPLETED,
            is_featured=True,
            github_link="https://github.com/example/portfolio-platform",
            linkedin_link="https://www.linkedin.com/posts/example-project",
        )
        skill = Skill.objects.create(title="Django", category="Backend")
        self.project.skills.add(skill)
        ProjectFeature.objects.create(
            project=self.project,
            title="Dynamic project pages",
            slug="dynamic-project-pages",
            description="Each case study is rendered from the database.",
        )

    def test_project_detail_renders_model_content(self):
        response = self.client.get(
            reverse("core:project_detail", kwargs={"slug": self.project.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)
        self.assertContains(response, "Django")
        self.assertContains(response, "Dynamic project pages")
        self.assertContains(response, "GitHub")
        self.assertContains(response, "Source code and repository")

    def test_unknown_project_returns_404(self):
        response = self.client.get(
            reverse("core:project_detail", kwargs={"slug": "missing-project"})
        )

        self.assertEqual(response.status_code, 404)

    def test_project_detail_uses_persian_model_fields_in_farsi(self):
        session = self.client.session
        session["site_language"] = "fa"
        session.save()

        response = self.client.get(
            reverse("core:project_detail", kwargs={"slug": self.project.slug})
        )

        self.assertContains(response, self.project.fa_title)
        self.assertContains(response, self.project.fa_short_description)
        self.assertContains(response, self.project.fa_description)
        self.assertContains(response, 'lang="fa"')
        self.assertContains(response, 'dir="rtl"')


class SiteLanguageViewTests(TestCase):
    def test_language_choice_is_saved_and_redirects_back(self):
        response = self.client.post(
            reverse("core:set_site_language"),
            {"language": "fa", "next": reverse("core:home") + "#work"},
        )

        self.assertRedirects(response, reverse("core:home") + "#work")
        self.assertEqual(self.client.session["site_language"], "fa")

        page = self.client.get(reverse("core:home"))
        self.assertContains(page, 'lang="fa"')
        self.assertContains(page, 'dir="rtl"')

    def test_invalid_language_falls_back_to_english(self):
        self.client.post(
            reverse("core:set_site_language"),
            {"language": "unknown", "next": reverse("core:home")},
        )

        self.assertEqual(self.client.session["site_language"], "en")

    def test_external_redirect_is_rejected(self):
        response = self.client.post(
            reverse("core:set_site_language"),
            {"language": "fa", "next": "https://example.com/phishing"},
        )

        self.assertRedirects(response, reverse("core:home"))


class HomeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="portfolio-owner",
            email="owner@example.com",
            password="test-password",
            is_superuser=True,
            is_staff=True,
        )
        self.project = Project.objects.create(
            title="Featured build",
            fa_title="پروژهٔ منتخب",
            slug="featured-build",
            short_description="A featured portfolio project.",
            fa_short_description="یک پروژهٔ منتخب برای پورتفولیو.",
            is_featured=True,
        )
        self.skill = Skill.objects.create(title="Python", category="Backend")
        self.project.skills.add(self.skill)

    def test_home_renders_dynamic_portfolio_content(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Featured build")
        self.assertContains(response, "Python")
        self.assertContains(response, 'id="skills"')
        self.assertContains(response, "Backend")
        self.assertNotContains(response, "Stack &amp; tools")
        self.assertContains(response, 'href="#contact"')
        self.assertContains(response, "owner@example.com")

    def test_home_groups_skills_by_category_and_renders_icons(self):
        Skill.objects.create(
            title="PostgreSQL",
            category="Database",
            icon="icons/postgresql.png",
        )

        response = self.client.get(reverse("core:home"))
        content = response.content.decode()

        self.assertContains(response, "Database")
        self.assertContains(response, "PostgreSQL")
        self.assertContains(response, 'src="/media/icons/postgresql.png"')
        self.assertLess(
            content.index(">Backend</h3>"),
            content.index(">Database</h3>"),
        )

    def test_home_uses_profile_content_when_available(self):
        Profile.objects.create(
            user=self.user,
            short_bio="Short profile introduction.",
            bio="Long profile biography.",
            github_url="https://github.com/example",
        )

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "Short profile introduction.")
        self.assertContains(response, "Long profile biography.")
        self.assertContains(response, "https://github.com/example")

    def test_home_uses_persian_profile_fields_in_farsi(self):
        profile = Profile.objects.create(
            user=self.user,
            fa_name="میلاد سلطان‌محمدی",
            fa_short_bio="معرفی کوتاه فارسی پروفایل.",
            fa_bio="زندگی‌نامهٔ کامل فارسی پروفایل.",
        )
        session = self.client.session
        session["site_language"] = "fa"
        session.save()

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, profile.fa_name)
        self.assertContains(response, profile.fa_short_bio)
        self.assertContains(response, profile.fa_bio)
        self.assertContains(response, f"سلام، من <span class=\"text-accent\">{profile.fa_name}</span> هستم")

    def test_home_contact_form_posts_to_contact_message_api(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(
            response,
            f'action="{reverse("core:contact_message_create")}"',
        )
        for field_name in (
            "name",
            "email",
            "telegram_id",
            "phone",
            "subject",
            "message",
        ):
            with self.subTest(field_name=field_name):
                self.assertContains(response, f'name="{field_name}"')

    def test_home_uses_persian_project_fields_in_farsi(self):
        session = self.client.session
        session["site_language"] = "fa"
        session.save()

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, self.project.fa_title)
        self.assertContains(response, self.project.fa_short_description)
        self.assertContains(response, "پروژه‌های منتخب")
        self.assertContains(response, "مشاهده پروژه")
from django.urls import reverse

from .models import Project


class CoreAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )
        cls.project = Project.objects.create(title="Portfolio", slug="portfolio")

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_core_admin_pages_are_available(self):
        urls = (
            reverse("admin:index"),
            reverse("admin:core_project_changelist"),
            reverse("admin:core_skill_changelist"),
            reverse("admin:core_projectfeature_changelist"),
            reverse("admin:core_projectimage_changelist"),
            reverse("admin:core_contactmessage_changelist"),
        )

        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_project_change_page_contains_related_inlines(self):
        response = self.client.get(
            reverse("admin:core_project_change", args=(self.project.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "features-TOTAL_FORMS")
        self.assertContains(response, "images-TOTAL_FORMS")
        self.assertContains(response, 'name="fa_title"')
        self.assertContains(response, 'name="fa_short_description"')
        self.assertContains(response, 'name="fa_description"')


class ContactMessageApiTests(TestCase):
    def setUp(self):
        self.url = reverse("core:contact_message_create")

    def test_json_message_is_saved(self):
        response = self.client.post(
            self.url,
            data={
                "name": "Sara Ahmadi",
                "email": "sara@example.com",
                "telegram_id": "@sara_dev",
                "phone": "",
                "subject": "New project",
                "message": "I would like to discuss a Django project.",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["success"])
        saved_message = ContactMessage.objects.get()
        self.assertEqual(saved_message.name, "Sara Ahmadi")
        self.assertEqual(saved_message.email, "sara@example.com")
        self.assertFalse(saved_message.is_read)

    def test_form_encoded_message_is_saved(self):
        response = self.client.post(
            self.url,
            data={
                "name": "Ali",
                "phone": "+98 912 123 4567",
                "subject": "Hello",
                "message": "Please contact me.",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactMessage.objects.get().phone, "+98 912 123 4567")

    def test_at_least_one_contact_method_is_required(self):
        response = self.client.post(
            self.url,
            data={
                "name": "No Contact",
                "subject": "Hello",
                "message": "There is no way to reply to me.",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("__all__", response.json()["errors"])
        self.assertEqual(len(response.json()["errors"]["__all__"]), 1)
        self.assertFalse(ContactMessage.objects.exists())

    def test_invalid_contact_values_are_rejected(self):
        response = self.client.post(
            self.url,
            data={
                "name": "Invalid Contact",
                "email": "not-an-email",
                "telegram_id": "bad id",
                "subject": "Hello",
                "message": "Invalid contact fields.",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json()["errors"])
        self.assertIn("telegram_id", response.json()["errors"])

    def test_invalid_json_is_rejected(self):
        response = self.client.post(
            self.url,
            data="{not-json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_get_is_not_allowed(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.headers["Allow"], "POST")
