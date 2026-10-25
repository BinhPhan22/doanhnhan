"""Đăng nhập bằng email, có khóa tạm sau nhiều lần sai mật khẩu."""
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.utils import timezone

from .models import User


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        email = (email or username or "").strip().lower()
        if not email or not password:
            return None
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            User().set_password(password)  # cân bằng thời gian phản hồi
            return None
        if user.is_locked:
            if request is not None:
                request.login_locked_until = user.locked_until
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            if user.failed_logins or user.locked_until:
                User.objects.filter(pk=user.pk).update(failed_logins=0, locked_until=None)
            return user
        user.failed_logins += 1
        update = {"failed_logins": user.failed_logins}
        if user.failed_logins >= settings.LOGIN_MAX_FAILURES:
            update = {"failed_logins": 0, "locked_until": timezone.now() + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)}
            if request is not None:
                request.login_locked_until = update["locked_until"]
        User.objects.filter(pk=user.pk).update(**update)
        return None

    def user_can_authenticate(self, user):
        return user.is_active and user.status != User.Status.SUSPENDED
