"""Đăng ký, đăng nhập (email hoặc Google), đồng ý điều khoản, hồ sơ tài khoản."""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from apps.common.forms import StyledFormMixin
from apps.common.notify import notify_editors, send
from apps.common.permissions import client_ip
from apps.moderation.models import log
from apps.sitecontent.models import PolicyAcceptance, PolicyDocument, PolicyVersion

from . import google
from .forms import LoginForm, ProfileForm, SignupForm
from .middleware import missing_acceptances
from .models import AccountApplication, User

BACKEND = "apps.accounts.backends.EmailBackend"


def _safe_next(request, default="member:dashboard"):
    nxt = request.POST.get("next") or request.GET.get("next")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()},
                                               require_https=request.is_secure()):
        return nxt
    return reverse(default)


def _required_policies():
    """Phiên bản hiện hành của Điều khoản sử dụng và Chính sách dữ liệu (để hiển thị số phiên bản khi đăng ký)."""
    out = {}
    for doc in PolicyDocument.objects.filter(requires_acceptance=True):
        version = doc.current_version()
        if version:
            out[doc.code] = version
    return out


def _record_acceptances(request, user, method):
    for version in _required_policies().values():
        PolicyAcceptance.objects.get_or_create(
            user=user, version=version,
            defaults={"ip": client_ip(request), "user_agent": request.META.get("HTTP_USER_AGENT", "")[:255],
                      "method": method})
    request.session.pop("policy_ok", None)


def _create_application(user, data):
    app, _ = AccountApplication.objects.update_or_create(user=user, defaults={
        "applicant_type": data["applicant_type"], "organization": data.get("organization", ""),
        "intro": data.get("intro", ""), "reference_url": data.get("reference_url", ""),
        "status": AccountApplication.Status.PENDING})
    notify_editors("Đăng ký tài khoản mới", "staff_new_account", {"user": user, "app": app})
    send(user.email, "Đã nhận đăng ký tài khoản", "account_received", {"user": user})
    return app


def signup(request):
    if request.user.is_authenticated:
        return redirect("member:dashboard")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        with transaction.atomic():
            user = User.objects.create_user(email=d["email"], password=d["password1"], full_name=d["full_name"].strip(),
                                            phone=d["phone"].strip(), newsletter=d["newsletter"])
            _create_application(user, d)
            _record_acceptances(request, user, "signup")
        log(user, "account.signup", user, user.email, request=request)
        login(request, user, backend=BACKEND)
        messages.success(request, "Đã gửi đăng ký. Tài khoản của bạn đang chờ ban quản trị duyệt.")
        return redirect("member:dashboard")
    return render(request, "accounts/signup.html", {"form": form, "policies": _required_policies()})


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_safe_next(request))
    form = LoginForm(request.POST or None)
    error = None
    if request.method == "POST" and form.is_valid():
        from django.contrib.auth import authenticate

        user = authenticate(request, email=form.cleaned_data["email"], password=form.cleaned_data["password"])
        locked = getattr(request, "login_locked_until", None)
        if user is not None:
            login(request, user, backend=BACKEND)
            if not form.cleaned_data["remember"]:
                request.session.set_expiry(0)
            log(user, "account.login", user, user.email, request=request)
            return redirect(_safe_next(request))
        if locked:
            minutes = max(1, int((locked - timezone.now()).total_seconds() // 60) + 1)
            error = f"Tài khoản tạm khóa do nhập sai mật khẩu nhiều lần. Vui lòng thử lại sau {minutes} phút hoặc đặt lại mật khẩu."
        else:
            error = "Email hoặc mật khẩu chưa đúng."
    return render(request, "accounts/login.html", {"form": form, "error": error,
                                                   "next": request.GET.get("next", "")})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Bạn đã đăng xuất.")
    return redirect("public:home")


# --------------------------------------------------------------------------- Google
def google_start(request):
    if not google.enabled():
        messages.error(request, "Đăng nhập bằng Google chưa được bật.")
        return redirect("accounts:login")
    request.session["after_google"] = _safe_next(request)
    return redirect(google.authorization_url(request))


def google_callback(request):
    if not google.enabled():
        return redirect("accounts:login")
    info = google.fetch_profile(request)
    if not info:
        messages.error(request, "Không đăng nhập được bằng Google. Vui lòng thử lại.")
        return redirect("accounts:login")
    user = User.objects.filter(google_sub=info["sub"]).first()
    if user is None and info.get("email_verified"):
        user = User.objects.filter(email__iexact=info["email"]).first()
        if user:
            user.google_sub = info["sub"]
            user.save(update_fields=["google_sub"])
    if user is None:
        user = User.objects.create_user(email=info["email"].lower(), password=None,
                                        full_name=info.get("name") or info["email"].split("@")[0],
                                        auth_provider="google", google_sub=info["sub"])
        log(user, "account.signup_google", user, user.email, request=request)
    if user.status == User.Status.SUSPENDED or not user.is_active:
        messages.error(request, "Tài khoản đã bị khóa.")
        return redirect("accounts:login")
    login(request, user, backend=BACKEND)
    if not hasattr(user, "application") and not user.is_editor:
        return redirect("accounts:complete_signup")
    return redirect(request.session.pop("after_google", reverse("member:dashboard")))


@login_required
def complete_signup(request):
    """Người đăng ký bằng Google bổ sung thông tin và đồng ý điều khoản."""
    if hasattr(request.user, "application"):
        return redirect("member:dashboard")
    form = SignupForm(request.POST or None, with_password=False,
                      initial={"full_name": request.user.full_name})
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        user = request.user
        user.full_name, user.phone, user.newsletter = d["full_name"].strip(), d["phone"].strip(), d["newsletter"]
        user.save()
        _create_application(user, d)
        _record_acceptances(request, user, "google")
        messages.success(request, "Đã gửi đăng ký. Tài khoản của bạn đang chờ ban quản trị duyệt.")
        return redirect("member:dashboard")
    return render(request, "accounts/signup.html", {"form": form, "policies": _required_policies(), "complete": True})


# --------------------------------------------------------------------------- đồng ý điều khoản mới
@login_required
def accept_policies(request):
    ids = missing_acceptances(request.user)
    versions = PolicyVersion.objects.filter(pk__in=ids).select_related("document")
    if not versions:
        return redirect(_safe_next(request, "public:home"))
    if request.method == "POST":
        if all(request.POST.get(f"v{v.pk}") == "on" for v in versions):
            for v in versions:
                PolicyAcceptance.objects.get_or_create(user=request.user, version=v, defaults={
                    "ip": client_ip(request), "user_agent": request.META.get("HTTP_USER_AGENT", "")[:255],
                    "method": "reaccept"})
            request.session.pop("policy_ok", None)
            messages.success(request, "Cảm ơn bạn đã xác nhận.")
            return redirect(_safe_next(request, "public:home"))
        messages.error(request, "Vui lòng đánh dấu đồng ý với tất cả văn bản.")
    return render(request, "accounts/accept_policies.html", {"versions": versions, "next": request.GET.get("next", "")})


# --------------------------------------------------------------------------- tài khoản
@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã lưu thông tin tài khoản.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {
        "form": form, "acceptances": request.user.policy_acceptances.select_related("version__document")})


class StyledPasswordResetForm(StyledFormMixin, PasswordResetForm):
    pass


class StyledSetPasswordForm(StyledFormMixin, SetPasswordForm):
    pass


class StyledPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    pass


password_reset = auth_views.PasswordResetView.as_view(
    template_name="accounts/password_reset.html", form_class=StyledPasswordResetForm,
    email_template_name="emails/password_reset.txt", subject_template_name="emails/password_reset_subject.txt",
    success_url=reverse_lazy("accounts:password_reset_done"),
    extra_email_context={"site_url": settings.SITE_URL})
password_reset_done = auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html")
password_reset_confirm = auth_views.PasswordResetConfirmView.as_view(
    template_name="accounts/password_reset_confirm.html", form_class=StyledSetPasswordForm,
    success_url=reverse_lazy("accounts:password_reset_complete"))
password_reset_complete = auth_views.PasswordResetCompleteView.as_view(
    template_name="accounts/password_reset_complete.html")
password_change = auth_views.PasswordChangeView.as_view(
    template_name="accounts/password_change.html", form_class=StyledPasswordChangeForm,
    success_url=reverse_lazy("accounts:profile"))
