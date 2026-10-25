"""Bộ lọc & thẻ dùng chung trong giao diện (được nạp sẵn ở mọi template)."""
from urllib.parse import urlencode

from django import template
from django.utils.html import format_html

from apps.common.text import plain_excerpt, render_markdown

register = template.Library()


@register.filter
def md(value):
    return render_markdown(value or "")


@register.filter
def excerpt(value, length=180):
    return plain_excerpt(value or "", int(length))


@register.filter
def get(mapping, key):
    try:
        return mapping.get(key, "")
    except AttributeError:
        return ""


@register.filter
def initials(name):
    import re

    parts = [p for p in re.sub(r"\(.*?\)", "", name or "").split() if p]
    return (parts[-1][0] if parts else "?").upper()


@register.filter
def lines(value):
    return [l.strip(" -•\t") for l in (value or "").splitlines() if l.strip()]


@register.simple_tag(takes_context=True)
def qs(context, **kwargs):
    """Giữ nguyên tham số truy vấn hiện tại, thay các khóa được chỉ định (giá trị rỗng = bỏ)."""
    params = context["request"].GET.copy()
    for k, v in kwargs.items():
        if v in (None, ""):
            params.pop(k, None)
        else:
            params[k] = v
    if "trang" not in kwargs:
        params.pop("trang", None)
    encoded = urlencode([(k, v) for k in params for v in params.getlist(k)])
    return f"?{encoded}" if encoded else "?"


@register.simple_tag
def svg_path(d, size=22, cls=""):
    return format_html(
        '<svg class="{}" width="{}" height="{}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{}"/></svg>',
        cls, size, size, d,
    )


@register.inclusion_tag("partials/pagination.html", takes_context=True)
def paginate(context, page):
    return {"page": page, "request": context["request"]}
