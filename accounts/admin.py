from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Profile, User


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 1
    max_num = 1
    can_delete = False
    fields = (
        "short_bio",
        "bio",
        "avatar",
        "github_url",
        "linkedin_url",
        "resume",
        "updated_at",
    )
    readonly_fields = ("updated_at",)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "profile_status",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)

    @admin.display(description="پروفایل", boolean=True)
    def profile_status(self, obj):
        return hasattr(obj, "profile")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "github_url", "linkedin_url", "updated_at")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "bio",
    )
    list_select_related = ("user",)
    readonly_fields = ("avatar_preview", "updated_at")
    fieldsets = (
        ("کاربر", {"fields": ("user",)}),
        ("معرفی", {"fields": ("short_bio", "bio", "avatar", "avatar_preview")}),
        ("ارتباطات و رزومه", {"fields": ("github_url", "linkedin_url", "resume")}),
        ("زمان‌ها", {"fields": ("updated_at",), "classes": ("collapse",)}),
    )

    @admin.display(description="نام")
    def full_name(self, obj):
        return obj.user.get_full_name() or "—"

    @admin.display(description="پیش‌نمایش آواتار")
    def avatar_preview(self, obj):
        if not obj.avatar:
            return "—"
        return format_html(
            '<img src="{}" width="96" height="96" '
            'style="object-fit:cover;border-radius:50%;" alt="" />',
            obj.avatar.url,
        )
