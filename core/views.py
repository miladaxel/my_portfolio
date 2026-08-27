from django.shortcuts import get_object_or_404, render

from accounts.models import Profile, User

from .models import Project, Skill


def home(request):
    profile = Profile.objects.select_related("user").first()
    owner = profile.user if profile else User.objects.filter(is_superuser=True).order_by("id").first()

    featured_projects = list(
        Project.objects.filter(is_featured=True)
        .prefetch_related("skills")
        .order_by("display_order", "-created_at")[:3]
    )
    if not featured_projects:
        featured_projects = list(
            Project.objects.prefetch_related("skills")
            .order_by("display_order", "-created_at")[:3]
        )

    display_name = "Portfolio"
    if owner:
        display_name = owner.get_full_name().strip() or owner.username.replace("_", " ").title()

    return render(
        request,
        "core/home.html",
        {
            "profile": profile,
            "owner": owner,
            "display_name": display_name,
            "featured_projects": featured_projects,
            "latest_project": featured_projects[0] if featured_projects else None,
            "project_count": Project.objects.count(),
            "skills": Skill.objects.order_by("category", "title"),
            "skill_count": Skill.objects.count(),
        },
    )


def project_detail(request, slug):
    project = get_object_or_404(
        Project.objects.prefetch_related("skills", "features", "images"),
        slug=slug,
    )
    related_projects = (
        Project.objects.exclude(pk=project.pk)
        .prefetch_related("skills")
        .order_by("display_order", "-created_at")[:3]
    )

    return render(
        request,
        "core/project_detail.html",
        {
            "project": project,
            "related_projects": related_projects,
            "active_nav": "work",
        },
    )
