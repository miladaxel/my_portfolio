SUPPORTED_SITE_LANGUAGES = {"en", "fa"}
DEFAULT_SITE_LANGUAGE = "en"
SITE_LANGUAGE_SESSION_KEY = "site_language"


def get_site_language(request):
    """Return the visitor's saved site language, falling back safely to English."""
    language = request.session.get(
        SITE_LANGUAGE_SESSION_KEY,
        DEFAULT_SITE_LANGUAGE,
    )
    if language not in SUPPORTED_SITE_LANGUAGES:
        return DEFAULT_SITE_LANGUAGE
    return language
