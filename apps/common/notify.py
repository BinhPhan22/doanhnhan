"""Gửi email thông báo. Lỗi gửi thư không làm hỏng thao tác chính."""
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

log = logging.getLogger(__name__)


def send(to, subject, template, context=None):
    recipients = [to] if isinstance(to, str) else [r for r in to if r]
    if not recipients:
        return
    ctx = {"site_url": settings.SITE_URL, **(context or {})}
    body = render_to_string(f"emails/{template}.txt", ctx)
    try:
        send_mail(f"[doanhnhan.wiki] {subject}", body, settings.DEFAULT_FROM_EMAIL, recipients)
    except Exception:  # noqa: BLE001 — chỉ ghi log, không chặn luồng chính
        log.exception("Không gửi được email '%s' tới %s", subject, recipients)


def notify_editors(subject, template, context=None):
    if settings.EDITORIAL_NOTIFY_EMAILS:
        send(settings.EDITORIAL_NOTIFY_EMAILS, subject, template, context)
