from .language import get_site_language


def site_language(request):
    language = get_site_language(request)
    return {
        "site_language": language,
        "is_farsi": language == "fa",
        "text_direction": "rtl" if language == "fa" else "ltr",
    }
