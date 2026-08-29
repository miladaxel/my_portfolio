"""Django settings shared by local development and production deployments."""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Local values live in .env. Hosting providers should inject environment
# variables directly; override=False ensures their values always win.
load_dotenv(BASE_DIR / ".env", override=False)


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ImproperlyConfigured(
        f"{name} must be one of: true, false, 1, 0, yes, no, on, off."
    )


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


ENVIRONMENT = os.getenv("DJANGO_ENV", "development").strip().lower()
if ENVIRONMENT not in {"development", "production"}:
    raise ImproperlyConfigured(
        "DJANGO_ENV must be either 'development' or 'production'."
    )

IS_PRODUCTION = ENVIRONMENT == "production"
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip()
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").strip()

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if IS_PRODUCTION and not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY is required in production.")
if not SECRET_KEY:
    # This fallback is deliberately limited to local development.
    SECRET_KEY = "django-insecure-development-only-change-me"

# Production can never accidentally expose Django's debug pages.
DEBUG = False if IS_PRODUCTION else env_bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    default=(
        RENDER_EXTERNAL_HOSTNAME
        if IS_PRODUCTION
        else "localhost,127.0.0.1,[::1]"
    ),
)
if IS_PRODUCTION and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS is required outside Render production, or "
        "RENDER_EXTERNAL_HOSTNAME must be provided automatically by Render."
    )

CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=RENDER_EXTERNAL_URL if IS_PRODUCTION else "",
)


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary_storage",
    "cloudinary",

    "core.apps.CoreConfig",
    "accounts.apps.AccountsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "my_portfolio.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_language",
            ],
        },
    },
]

WSGI_APPLICATION = "my_portfolio.wsgi.application"
ASGI_APPLICATION = "my_portfolio.asgi.application"


DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if IS_PRODUCTION and not DATABASE_URL:
    raise ImproperlyConfigured("DATABASE_URL is required in production.")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL or f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=60 if IS_PRODUCTION else 0,
        conn_health_checks=IS_PRODUCTION,
    )
}

if IS_PRODUCTION and DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
    raise ImproperlyConfigured(
        "DATABASE_URL must point to PostgreSQL in production."
    )


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "accounts.User"


LANGUAGE_CODE = os.getenv("DJANGO_LANGUAGE_CODE", "en-us")
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "Asia/Tehran")
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

CLOUDINARY_CREDENTIALS = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME", "").strip(),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY", "").strip(),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET", "").strip(),
}

if IS_PRODUCTION:
    missing_cloudinary_credentials = [
        name for name, value in CLOUDINARY_CREDENTIALS.items() if not value
    ]
    if missing_cloudinary_credentials:
        missing_names = ", ".join(
            f"CLOUDINARY_{name}" for name in missing_cloudinary_credentials
        )
        raise ImproperlyConfigured(
            f"The following Cloudinary environment variables are required in "
            f"production: {missing_names}."
        )

CLOUDINARY_STORAGE = CLOUDINARY_CREDENTIALS

STORAGES = {
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage.MediaCloudinaryStorage"
            if IS_PRODUCTION
            else "django.core.files.storage.FileSystemStorage"
        ),
    },
    "raw_media": {
        "BACKEND": (
            "cloudinary_storage.storage.RawMediaCloudinaryStorage"
            if IS_PRODUCTION
            else "django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if IS_PRODUCTION
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.getenv("DJANGO_MEDIA_ROOT", str(BASE_DIR / "media")))


# HTTPS and cookie hardening are automatic in production. These assume the
# reverse proxy sends X-Forwarded-Proto, which is standard on managed hosts.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = IS_PRODUCTION and env_bool(
    "DJANGO_SECURE_SSL_REDIRECT", default=True
)
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "3600")) if IS_PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION and env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False
)
SECURE_HSTS_PRELOAD = IS_PRODUCTION and env_bool(
    "DJANGO_SECURE_HSTS_PRELOAD", default=False
)


EMAIL_BACKEND = os.getenv(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {
        "handlers": ["console"],
        "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
