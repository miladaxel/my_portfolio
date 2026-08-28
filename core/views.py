import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from accounts.models import Profile, User

from .forms import ContactMessageForm
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


def create_contact_message(request):
    if request.method != "POST":
        response = JsonResponse(
            {"success": False, "error": "Only POST requests are allowed."},
            status=405,
        )
        response["Allow"] = "POST"
        return response

    if request.content_type == "application/json":
        try:
            data = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {"success": False, "error": "The request body is not valid JSON."},
                status=400,
            )
        if not isinstance(data, dict):
            return JsonResponse(
                {"success": False, "error": "The JSON body must be an object."},
                status=400,
            )
    else:
        data = request.POST

    form = ContactMessageForm(data)
    if not form.is_valid():
        return JsonResponse(
            {
                "success": False,
                "errors": {
                    field: [error["message"] for error in errors]
                    for field, errors in form.errors.get_json_data().items()
                },
            },
            status=400,
        )

    contact_message = form.save()
    return JsonResponse(
        {
            "success": True,
            "message": "Your message has been received.",
            "id": contact_message.pk,
        },
        status=201,
    )
