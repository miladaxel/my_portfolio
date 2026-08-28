from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html, format_html_join

from .models import ContactMessage, Project, ProjectFeature, ProjectImage, Skill


def image_preview(image, *, width=72):
    if not image:
        return "—"
    return format_html(
        '<img src="{}" width="{}" style="height:auto;max-height:72px;object-fit:cover;'
        'border-radius:6px;" alt="" />',
        image.url,
        width,
    )


class ProjectFeatureInline(admin.TabularInline):
    model = ProjectFeature
    extra = 1
    fields = ("title", "slug", "description", "display_order")
    ordering = ("display_order", "id")
    prepopulated_fields = {"slug": ("title",)}
    show_change_link = True


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "image_preview", "caption")
    readonly_fields = ("image_preview",)
    show_change_link = True

    @admin.display(description="پیش‌نمایش")
    def image_preview(self, obj):
        return image_preview(obj.image)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "project_count", "icon_preview")
    list_filter = ("category",)
    search_fields = ("title", "category")
    ordering = ("category", "title")
    readonly_fields = ("icon_preview",)
    fields = ("title", "category",'display_order' ,"icon", "icon_preview")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_project_count=Count("projects", distinct=True))

    @admin.display(description="تعداد پروژه‌ها", ordering="_project_count")
    def project_count(self, obj):
        return obj._project_count

    @admin.display(description="پیش‌نمایش آیکن")
    def icon_preview(self, obj):
        return image_preview(obj.icon, width=48)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "is_featured",
        "display_order",
        "skill_count",
        "updated_at",
    )
    list_display_links = ("title",)
    list_editable = ("status", "is_featured", "display_order")
    list_filter = ("status", "is_featured", "skills", "created_at")
    search_fields = ("title", "short_description", "description", "skills__title")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("skills",)
    readonly_fields = ("thumbnail_preview", "created_at", "updated_at")
    date_hierarchy = "created_at"
    save_on_top = True
    inlines = (ProjectFeatureInline, ProjectImageInline)
    actions = ("mark_as_featured", "remove_from_featured", "mark_as_completed")
    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "title",
                    "slug",
                    "short_description",
                    "description",
                    "thumbnail",
                    "thumbnail_preview",
                )
            },
        ),
        (
            "وضعیت و نمایش",
            {"fields": ("status", "is_featured", "display_order", "skills")},
        ),
        ("لینک‌ها", {"fields": ("github_link", "linkedin_link")}),
        (
            "زمان‌ها",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_skill_count=Count("skills", distinct=True))

    @admin.display(description="تعداد مهارت‌ها", ordering="_skill_count")
    def skill_count(self, obj):
        return obj._skill_count

    @admin.display(description="پیش‌نمایش تصویر")
    def thumbnail_preview(self, obj):
        return image_preview(obj.thumbnail, width=160)

    @admin.action(description="نمایش پروژه‌های انتخاب‌شده در بخش ویژه")
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="حذف پروژه‌های انتخاب‌شده از بخش ویژه")
    def remove_from_featured(self, request, queryset):
        queryset.update(is_featured=False)

    @admin.action(description="تغییر وضعیت پروژه‌های انتخاب‌شده به تکمیل‌شده")
    def mark_as_completed(self, request, queryset):
        queryset.update(status=Project.Status.COMPLETED)


@admin.register(ProjectFeature)
class ProjectFeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "display_order")
    list_editable = ("display_order",)
    list_filter = ("project",)
    search_fields = ("title", "description", "project__title")
    prepopulated_fields = {"slug": ("title",)}
    list_select_related = ("project",)
    ordering = ("project", "display_order", "id")


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "short_caption", "image_preview")
    list_filter = ("project",)
    search_fields = ("caption", "project__title")
    list_select_related = ("project",)
    readonly_fields = ("image_preview",)
    fields = ("project", "image", "image_preview", "caption")

    @admin.display(description="عنوان تصویر")
    def short_caption(self, obj):
        if not obj.caption:
            return "—"
        return obj.caption[:60]

    @admin.display(description="پیش‌نمایش")
    def image_preview(self, obj):
        return image_preview(obj.image)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "contact_method", "created_at", "is_read")
    list_display_links = ("name", "subject")
    list_editable = ("is_read",)
    list_filter = ("is_read", "created_at")
    search_fields = (
        "name",
        "email",
        "telegram_id",
        "phone",
        "subject",
        "message",
    )
    readonly_fields = (
        "name",
        "email",
        "telegram_id",
        "phone",
        "subject",
        "message",
        "created_at",
    )
    fields = (
        "name",
        "email",
        "telegram_id",
        "phone",
        "subject",
        "message",
        "created_at",
        "is_read",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    actions = ("mark_as_read", "mark_as_unread")

    @admin.display(description="راه ارتباطی")
    def contact_method(self, obj):
        methods = (
            ("Email", obj.email),
            ("Telegram", obj.telegram_id),
            ("Phone", obj.phone),
        )
        available_methods = ((label, value) for label, value in methods if value)
        return format_html_join(", ", "<span>{}: {}</span>", available_methods) or "—"

    @admin.action(description="علامت‌گذاری پیام‌های انتخاب‌شده به‌عنوان خوانده‌شده")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="علامت‌گذاری پیام‌های انتخاب‌شده به‌عنوان خوانده‌نشده")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)


admin.site.site_header = "مدیریت پورتفولیو"
admin.site.site_title = "پنل پورتفولیو"
admin.site.index_title = "مدیریت محتوای سایت"
