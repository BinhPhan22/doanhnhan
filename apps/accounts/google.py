"""Đăng nhập bằng Google (OAuth 2.0 / OpenID Connect). Chỉ bật khi có GOOGLE_CLIENT_ID và GOOGLE_CLIENT_SECRET."""
import secrets
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.urls import reverse

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


def enabled():
    return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)


def redirect_uri():
    return settings.SITE_URL + reverse("accounts:google_callback")


def authorization_url(request):
    state = secrets.token_urlsafe(24)
    request.session["google_state"] = state
    params = {"client_id": settings.GOOGLE_CLIENT_ID, "redirect_uri": redirect_uri(), "response_type": "code",
              "scope": "openid email profile", "state": state, "prompt": "select_account"}
    return f"{AUTH_URL}?{urlencode(params)}"


def fetch_profile(request):
    """Trả về dict {sub, email, email_verified, name} hoặc None nếu lỗi / state sai."""
    state = request.session.pop("google_state", None)
    if not state or state != request.GET.get("state") or not request.GET.get("code"):
        return None
    try:
        token = requests.post(TOKEN_URL, data={
            "code": request.GET["code"], "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET, "redirect_uri": redirect_uri(),
            "grant_type": "authorization_code"}, timeout=10).json()
        access = token.get("access_token")
        if not access:
            return None
        info = requests.get(USERINFO_URL, headers={"Authorization": f"Bearer {access}"}, timeout=10).json()
    except (requests.RequestException, ValueError):
        return None
    if not info.get("sub") or not info.get("email"):
        return None
    return info
