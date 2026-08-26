from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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

    def test_unknown_project_returns_404(self):
        response = self.client.get(
            reverse("core:project_detail", kwargs={"slug": "missing-project"})
        )

        self.assertEqual(response.status_code, 404)
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
