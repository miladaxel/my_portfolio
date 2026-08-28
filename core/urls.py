from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "api/contact/messages/",
        views.create_contact_message,
        name="contact_message_create",
    ),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
]
