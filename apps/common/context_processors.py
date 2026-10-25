from django.conf import settings
from django.core.cache import cache

from apps.common.permissions import is_editor

NAV = [
    ("persons", "Doanh nhân", "public:person_list"),
    ("stories", "Story", "public:story_list"),
    ("events", "Sự kiện", "public:event_list"),
    ("podcasts", "Podcast", "public:podcast_list"),
    ("videos", "Video", "public:video_list"),
    ("associations", "Hiệp hội", "public:association_list"),
]
SECTION_BY_PREFIX = [
    ("/doanh-nhan/", "persons"), ("/story/", "stories"),
    ("/su-kien/", "events"), ("/podcast/", "podcasts"),
    ("/postcast/", "podcasts"), ("/postcard/", "postcards"),
    ("/video/", "videos"), ("/hiep-hoi/", "associations"),
    ("/doanh-nghiep/", "companies"), ("/nganh-nghe/", "sectors"),
    ("/donate/", "donate"),
]


def _staff_counts():
    data = cache.get("staff_counts")
    if data is None:
        from apps.accounts.models import AccountApplication
        from apps.moderation.models import ProfileClaim, Revision
        from apps.sitecontent.models import InterviewRequest

        data = {
            "revisions": Revision.objects.filter(state="pending").count(),
            "accounts": AccountApplication.objects.filter(status="pending").count(),
            "claims": ProfileClaim.objects.filter(state="pending").count(),
            "interviews": InterviewRequest.objects.filter(state="new").count(),
        }
        cache.set("staff_counts", data, 30)
    return data


def site(request):
    from apps.sitecontent.models import SiteSettings

    path = request.path
    section = next((key for prefix, key in SECTION_BY_PREFIX if path.startswith(prefix)), "")
    ctx = {
        "NAV": NAV,
        "nav_section": section,
        "SITE": SiteSettings.load(),
        "SITE_URL": settings.SITE_URL,
        "GOOGLE_ENABLED": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
    }
    user = getattr(request, "user", None)
    if user is not None and is_editor(user):
        ctx["staff_counts"] = _staff_counts()
    return ctx
