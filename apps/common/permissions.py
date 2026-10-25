"""Phân quyền: khách, thành viên (đã duyệt), biên tập viên, quản trị viên."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def is_active_member(user):
    return user.is_authenticated and user.is_active and user.status == "active"


def is_editor(user):
    return is_active_member(user) and (user.is_superuser or user.role in ("editor", "admin"))


def is_admin(user):
    return is_active_member(user) and (user.is_superuser or user.role == "admin")


def _guard(check, pending_redirect=None):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if user.status == "pending" and pending_redirect:
                messages.info(request, "Tài khoản của bạn đang chờ ban quản trị duyệt.")
                return redirect(pending_redirect)
            if not check(user):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


member_required = _guard(is_active_member, pending_redirect="member:dashboard")
editor_required = _guard(is_editor)
admin_required = _guard(is_admin)


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
