#!/bin/sh
# ==============================================================================
# Script tự động sao lưu định kỳ cơ sở dữ liệu doanhnhan.wiki
# Thiết lập Cron chạy vào lúc 03:00 sáng mỗi ngày:
# 0 3 * * * /path/to/deploy/backup.sh >> /var/log/doanhnhan_backup.log 2>&1
# ==============================================================================
set -e

BACKUP_DIR="${BACKUP_DIR:-/data/backups}"
KEEP_DAYS="${BACKUP_KEEP_DAYS:-7}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Bắt đầu tiến trình sao lưu định kỳ ==="

# Kiểm tra nếu chạy trong môi trường Docker hay trực tiếp trên máy chủ
if command -v docker >/dev/null 2>&1 && [ -f "docker-compose.yml" ]; then
    echo "Thực thi sao lưu qua Docker container 'web'..."
    docker compose exec -T web python manage.py backup_db --output-dir "$BACKUP_DIR" --keep-days "$KEEP_DAYS"
else
    echo "Thực thi sao lưu trực tiếp qua Python..."
    python manage.py backup_db --output-dir "$BACKUP_DIR" --keep-days "$KEEP_DAYS"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Hoàn tất tiến trình sao lưu thành công ==="
