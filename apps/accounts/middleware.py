"""Buộc người dùng đã đăng nhập đồng ý lại khi Điều khoản / Chính sách bắt buộc có phiên bản mới."""
from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import reverse

EXEMPT_PREFIXES = ("/static/", "/api/", "/media/", "/dong-y-dieu-khoan/", "/dang-xuat/", "/chinh-sach/", "/django-admin/",
                   "/hoan-tat-dang-ky/")


def required_versions():
    """[(document, version)] của các văn bản bắt buộc đang có hiệu lực. Cache 60 giây."""
    data = cache.get("required_policy_versions")
    if data is None:
        from apps.sitecontent.models import PolicyDocument

        data = []
        for doc in PolicyDocument.objects.filter(requires_acceptance=True):
            version = doc.current_version()
            if version:
                data.append((doc.pk, version.pk, version.require_reaccept))
        cache.set("required_policy_versions", data, 60)
    return data


def missing_acceptances(user):
    """Các phiên bản người dùng cần đồng ý: chưa từng đồng ý văn bản đó, hoặc phiên bản mới yêu cầu đồng ý lại."""
    from apps.sitecontent.models import PolicyAcceptance

    accepted = PolicyAcceptance.objects.filter(user=user).values_list("version_id", "version__document_id")
    accepted_versions = {v for v, _ in accepted}
    accepted_docs = {d for _, d in accepted}
    return [vid for doc_id, vid, reaccept in required_versions()
            if vid not in accepted_versions and (reaccept or doc_id not in accepted_docs)]


class PolicyAcceptanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (user is not None and user.is_authenticated and request.method == "GET"
                and not request.path.startswith(EXEMPT_PREFIXES)):
            key = tuple(v for _, v, _ in required_versions())
            if request.session.get("policy_ok") != list(key):
                if missing_acceptances(user):
                    return redirect(f"{reverse('accounts:accept_policies')}?next={request.get_full_path()}")
                request.session["policy_ok"] = list(key)
        return self.get_response(request)
