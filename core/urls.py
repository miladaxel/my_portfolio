from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
]
