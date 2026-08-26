from django.shortcuts import get_object_or_404, render

from .models import Project


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
        },
    )
