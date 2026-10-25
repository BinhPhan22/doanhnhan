"""
Nhận dạng link video (YouTube, Vimeo, Facebook, TikTok) và lấy thông tin qua oEmbed.
Hệ thống chỉ lưu link — không tải hay lưu tệp video.
"""
from dataclasses import dataclass
import logging
import re
from urllib.parse import parse_qs, quote, urlparse

import requests
from django.conf import settings

log = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    platform: str          # youtube | vimeo | facebook | tiktok | other
    external_id: str
    embed_url: str         # rỗng = không nhúng được, chỉ mở link gốc
    thumbnail_url: str = ""

    @property
    def platform_label(self):
        return PLATFORM_LABELS.get(self.platform, "Nền tảng khác")


PLATFORM_LABELS = {
    "youtube": "YouTube",
    "vimeo": "Vimeo",
    "facebook": "Facebook",
    "tiktok": "TikTok",
    "other": "Nền tảng khác",
}

OEMBED = {
    "youtube": "https://www.youtube.com/oembed?format=json&url={url}",
    "vimeo": "https://vimeo.com/api/oembed.json?url={url}",
    "tiktok": "https://www.tiktok.com/oembed?url={url}",
}

_YT_ID = re.compile(r"^[A-Za-z0-9_-]{6,20}$")


def parse_video_url(url: str):
    """Trả về VideoInfo, hoặc None nếu không phải URL http(s) hợp lệ."""
    url = (url or "").strip()
    try:
        u = urlparse(url)
    except ValueError:
        return None
    if u.scheme not in ("http", "https") or not u.netloc:
        return None
    host = u.netloc.lower().split(":")[0]
    for prefix in ("www.", "m.", "mobile."):
        if host.startswith(prefix):
            host = host[len(prefix):]

    if host in ("youtube.com", "youtu.be", "youtube-nocookie.com"):
        vid = ""
        if host == "youtu.be":
            vid = u.path.lstrip("/").split("/")[0]
        else:
            vid = (parse_qs(u.query).get("v") or [""])[0]
            m = re.match(r"^/(shorts|live|embed)/([^/?#]+)", u.path)
            if not vid and m:
                vid = m.group(2)
        if vid and _YT_ID.match(vid):
            return VideoInfo(
                "youtube", vid,
                f"https://www.youtube-nocookie.com/embed/{vid}?autoplay=1&rel=0",
                f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
            )
        return None

    if host in ("vimeo.com", "player.vimeo.com"):
        m = re.search(r"/(\d{5,12})", u.path)
        if m:
            return VideoInfo("vimeo", m.group(1), f"https://player.vimeo.com/video/{m.group(1)}?autoplay=1")
        return None

    if host in ("facebook.com", "fb.watch", "web.facebook.com"):
        m = re.search(r"/videos/(?:[^/]+/)?(\d+)", u.path)
        vid = m.group(1) if m else u.path.strip("/")
        return VideoInfo(
            "facebook", vid,
            "https://www.facebook.com/plugins/video.php?href=" + quote(url, safe="") + "&autoplay=true",
        )

    if host == "tiktok.com":
        m = re.search(r"/video/(\d+)", u.path)
        if m:
            return VideoInfo("tiktok", m.group(1), f"https://www.tiktok.com/embed/v2/{m.group(1)}")
        return None

    return VideoInfo("other", "", "")


def fetch_oembed(url: str, platform: str):
    """Lấy tiêu đề, kênh, ảnh bìa. Trả về dict (có thể rỗng) và trạng thái: ok | unavailable | unknown."""
    if not settings.VIDEO_FETCH_METADATA or platform not in OEMBED:
        return {}, "unknown"
    try:
        resp = requests.get(
            OEMBED[platform].format(url=quote(url, safe="")),
            timeout=settings.VIDEO_OEMBED_TIMEOUT,
            headers={"User-Agent": "doanhnhan.wiki video checker"},
        )
    except requests.RequestException as exc:
        log.info("oEmbed lỗi mạng cho %s: %s", url, exc)
        return {}, "unknown"
    if resp.status_code in (401, 403, 404):
        return {}, "unavailable"
    if resp.status_code != 200:
        return {}, "unknown"
    try:
        data = resp.json()
    except ValueError:
        return {}, "unknown"
    return {
        "title": (data.get("title") or "")[:300],
        "channel_name": (data.get("author_name") or "")[:200],
        "thumbnail_url": data.get("thumbnail_url") or "",
        "duration_seconds": data.get("duration") if isinstance(data.get("duration"), int) else None,
    }, "ok"


def format_duration(seconds):
    if not seconds:
        return ""
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
