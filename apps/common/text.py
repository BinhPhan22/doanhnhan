"""Xử lý văn bản tiếng Việt: chuẩn hóa để tìm kiếm, tạo slug, đếm từ, hiển thị markdown an toàn."""
import re
import unicodedata

import markdown as md
import nh3
from django.utils.safestring import mark_safe

_SPACES = re.compile(r"\s+")
_NON_SLUG = re.compile(r"[^a-z0-9]+")
_CITE = re.compile(r"\[\^(\d{1,3})\]")


def normalize(value: str) -> str:
    """Bỏ dấu, chữ thường, gom khoảng trắng: 'Nguyễn Đức' -> 'nguyen duc'."""
    if not value:
        return ""
    value = value.replace("đ", "d").replace("Đ", "D")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return _SPACES.sub(" ", value.lower()).strip()


def slugify_vi(value: str, max_length: int = 80) -> str:
    slug = _NON_SLUG.sub("-", normalize(value)).strip("-")
    return slug[:max_length].strip("-") or "muc"


def unique_slug(model, value: str, instance_pk=None, field: str = "slug") -> str:
    base = slugify_vi(value)
    slug, n = base, 2
    qs = model._default_manager.all()
    if instance_pk:
        qs = qs.exclude(pk=instance_pk)
    while qs.filter(**{field: slug}).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


ALLOWED_TAGS = {
    "p", "br", "h2", "h3", "h4", "ul", "ol", "li", "strong", "em", "b", "i",
    "a", "blockquote", "sup", "code", "pre", "hr", "img", "figure", "figcaption",
}
ALLOWED_ATTRS = {
    "a": {"href", "title"},
    "sup": {"class"},
    "img": {"src", "alt", "title", "class", "loading", "width", "height"},
    "figure": {"class"},
    "figcaption": {"class"},
}


def render_markdown(text: str) -> str:
    """Markdown -> HTML đã lọc. Chú thích [^n] trỏ tới mục Nguồn tham khảo số n."""
    if not text:
        return ""
    text = _CITE.sub(lambda m: f'<sup class="cite"><a href="#nguon-{m.group(1)}">[{m.group(1)}]</a></sup>', text)
    html = md.markdown(text, extensions=["sane_lists", "nl2br"], output_format="html")
    # Tiêu đề do người dùng viết bắt đầu từ cấp 3 để không lấn tiêu đề mục (h2) của trang.
    html = re.sub(r"<(/?)h2>", r"<\1h3>", html)
    clean = nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer nofollow",
    )
    return mark_safe(clean)


def plain_excerpt(text: str, length: int = 180) -> str:
    """Bỏ ký hiệu markdown để làm đoạn trích ngắn."""
    text = _CITE.sub("", text or "")
    text = re.sub(r"[#*_>`\[\]]", "", text)
    text = re.sub(r"\(https?://[^)]+\)", "", text)
    text = _SPACES.sub(" ", text).strip()
    return text if len(text) <= length else text[: length - 1].rsplit(" ", 1)[0] + "…"


def mask_phone(phone: str) -> str:
    """
    Ẩn số điện thoại bảo mật thành dấu *.
    Chỉ giữ lại các chữ số đầu và cuối, toàn bộ chữ số ở giữa chuyển thành *.
    Ví dụ:
      '0912345678'     -> '0912****78'
      '0912 345 678'   -> '0912 *** *78'
      '+84912345678'   -> '+8491****78'
    """
    if not phone:
        return ""
    digits = [c for c in phone if c.isdigit()]
    total_digits = len(digits)
    if total_digits < 5:
        return "****"
    # Với số từ 9 số trở lên: giữ 4 số đầu và 2 số cuối. Ngắn hơn: giữ 3 số đầu và 1 số cuối.
    prefix_len = 4 if total_digits >= 9 else 3
    suffix_len = 2 if total_digits >= 8 else 1

    digit_idx = 0
    res = []
    for ch in phone:
        if ch.isdigit():
            if digit_idx < prefix_len or digit_idx >= (total_digits - suffix_len):
                res.append(ch)
            else:
                res.append("*")
            digit_idx += 1
        else:
            res.append(ch)
    return "".join(res)
