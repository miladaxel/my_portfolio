import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts.models import Profile, User

from .forms import ContactMessageForm
from .language import (
    DEFAULT_SITE_LANGUAGE,
    SITE_LANGUAGE_SESSION_KEY,
    SUPPORTED_SITE_LANGUAGES,
    get_site_language,
)
from .models import Project, Skill


@require_POST
def set_site_language(request):
    language = request.POST.get("language", DEFAULT_SITE_LANGUAGE)
    if language not in SUPPORTED_SITE_LANGUAGES:
        language = DEFAULT_SITE_LANGUAGE

    request.session[SITE_LANGUAGE_SESSION_KEY] = language

    next_url = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse("core:home")

    return redirect(next_url)


def home(request):
    profile = Profile.objects.select_related("user").first()
    owner = profile.user if profile else User.objects.filter(is_superuser=True).order_by("id").first()
    is_farsi = get_site_language(request) == "fa"

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

    display_name = "پورتفولیو" if is_farsi else "Portfolio"
    if is_farsi and profile and profile.fa_name:
        display_name = profile.fa_name.strip()
    elif owner:
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
            "skills": Skill.objects.order_by("display_order", "category", 'title'),
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
    is_farsi = get_site_language(request) == "fa"
    if request.method != "POST":
        response = JsonResponse(
            {
                "success": False,
                "error": (
                    "فقط درخواست POST مجاز است."
                    if is_farsi
                    else "Only POST requests are allowed."
                ),
            },
            status=405,
        )
        response["Allow"] = "POST"
        return response

    if request.content_type == "application/json":
        try:
            data = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {
                    "success": False,
                    "error": (
                        "بدنهٔ درخواست JSON معتبر نیست."
                        if is_farsi
                        else "The request body is not valid JSON."
                    ),
                },
                status=400,
            )
        if not isinstance(data, dict):
            return JsonResponse(
                {
                    "success": False,
                    "error": (
                        "بدنهٔ JSON باید یک شیء باشد."
                        if is_farsi
                        else "The JSON body must be an object."
                    ),
                },
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
            "message": (
                "پیام شما دریافت شد."
                if is_farsi
                else "Your message has been received."
            ),
            "id": contact_message.pk,
        },
        status=201,
    )
