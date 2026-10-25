"""Kiểm tra định kỳ link video (chạy bằng cron, ví dụ mỗi ngày). Video mất link tự ẩn khỏi trang công khai."""
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.common import video as video_lib
from apps.common.notify import notify_editors
from apps.directory.models import Video


class Command(BaseCommand):
    help = "Kiểm tra link video và cập nhật thông tin (tiêu đề, ảnh bìa, thời lượng)."

    def add_arguments(self, parser):
        parser.add_argument("--gioi-han", type=int, default=500)

    def handle(self, *args, **opts):
        newly_broken = []
        checked = 0
        for video in Video.objects.filter(status="published").order_by("last_checked_at")[: opts["gioi_han"]]:
            info = video_lib.parse_video_url(video.url)
            if not info:
                continue
            meta, status = video_lib.fetch_oembed(video.url, info.platform)
            if status == "unavailable" and video.availability != "unavailable":
                newly_broken.append(video)
            if status != "unknown":
                video.availability = status
            if meta:
                video.channel_name = video.channel_name or meta["channel_name"]
                video.duration_seconds = video.duration_seconds or meta.get("duration_seconds")
                if meta.get("thumbnail_url") and not video.thumbnail_url:
                    video.thumbnail_url = meta["thumbnail_url"][:500]
            video.last_checked_at = timezone.now()
            video.save()
            checked += 1
        if newly_broken:
            notify_editors(f"{len(newly_broken)} video mất link", "staff_broken_videos", {"videos": newly_broken})
        self.stdout.write(self.style.SUCCESS(f"Đã kiểm tra {checked} video; {len(newly_broken)} video mới mất link."))
