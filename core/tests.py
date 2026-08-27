from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile, User

from .models import Project, ProjectFeature, Skill


class ProjectDetailViewTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Portfolio platform",
            slug="portfolio-platform",
            short_description="A focused project summary.",
            description="A complete project overview.",
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
            slug="featured-build",
            short_description="A featured portfolio project.",
            is_featured=True,
        )
        self.skill = Skill.objects.create(title="Python", category="Backend")
        self.project.skills.add(self.skill)

    def test_home_renders_dynamic_portfolio_content(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Featured build")
        self.assertContains(response, "Python")
        self.assertContains(response, "owner@example.com")

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
