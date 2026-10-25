"""
Lệnh sao lưu cơ sở dữ liệu tự động cho doanhnhan.wiki.

Hỗ trợ cả PostgreSQL và SQLite, tự động nén gzip và tự dọn dẹp (rotation)
các bản sao lưu cũ theo số ngày cấu hình.

Cách dùng:
    python manage.py backup_db
    python manage.py backup_db --keep-days 14 --output-dir /data/backups
"""
import gzip
import os
import shutil
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Sao lưu CSDL (PostgreSQL / SQLite) có nén gzip và dọn dẹp bản sao lưu cũ."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            default=os.environ.get("BACKUP_DIR", str(settings.BASE_DIR / "backups")),
            help="Thư mục chứa các tệp sao lưu (mặc định: backups/ trong thư mục dự án)",
        )
        parser.add_argument(
            "--keep-days",
            type=int,
            default=int(os.environ.get("BACKUP_KEEP_DAYS", "7")),
            help="Số ngày lưu giữ bản sao lưu trước khi tự động xóa bản cũ (mặc định: 7 ngày)",
        )

    def handle(self, *args, **options):
        output_dir = Path(options["output_dir"]).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        keep_days = options["keep_days"]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        db_conf = settings.DATABASES["default"]
        engine = db_conf.get("ENGINE", "")

        self.stdout.write(self.style.NOTICE(f"[{datetime.now().strftime('%H:%M:%S')}] Bắt đầu sao lưu CSDL..."))

        if "sqlite3" in engine:
            backup_file = self._backup_sqlite(db_conf, output_dir, timestamp)
        elif "postgresql" in engine or "postgres" in engine:
            backup_file = self._backup_postgres(db_conf, output_dir, timestamp)
        else:
            backup_file = self._backup_dumpdata(output_dir, timestamp)

        size_kb = backup_file.stat().st_size / 1024
        if size_kb > 1024:
            size_str = f"{size_kb / 1024:.2f} MB"
        else:
            size_str = f"{size_kb:.1f} KB"

        self.stdout.write(self.style.SUCCESS(f"✓ Sao lưu thành công: {backup_file.name} ({size_str})"))

        # Dọn dẹp bản sao lưu cũ (Rotation)
        if keep_days > 0:
            removed_count = self._prune_old_backups(output_dir, keep_days)
            if removed_count > 0:
                self.stdout.write(self.style.WARNING(f"✓ Đã dọn dẹp {removed_count} bản sao lưu cũ hơn {keep_days} ngày."))

    def _backup_sqlite(self, db_conf, output_dir: Path, timestamp: str) -> Path:
        backup_file = output_dir / f"backup_doanhnhan_{timestamp}.sqlite3.gz"

        from django.db import connection
        src_conn = None
        close_src = False

        if hasattr(connection, "connection") and connection.connection:
            src_conn = connection.connection
        else:
            source_path = Path(db_conf.get("NAME", settings.BASE_DIR / "db.sqlite3"))
            if not source_path.exists():
                return self._backup_dumpdata(output_dir, timestamp)
            src_conn = sqlite3.connect(source_path)
            close_src = True

        temp_mem_conn = sqlite3.connect(":memory:")
        src_conn.backup(temp_mem_conn)
        if close_src:
            src_conn.close()

        with gzip.open(backup_file, "wb") as f_out:
            for line in temp_mem_conn.iterdump():
                f_out.write(f"{line}\n".encode("utf-8"))
        temp_mem_conn.close()

        return backup_file

    def _backup_postgres(self, db_conf, output_dir: Path, timestamp: str) -> Path:
        pg_dump_bin = shutil.which("pg_dump")
        if not pg_dump_bin:
            self.stdout.write(self.style.WARNING("! Không tìm thấy công cụ pg_dump trên hệ thống, chuyển sang dumpdata JSON."))
            return self._backup_dumpdata(output_dir, timestamp)

        backup_file = output_dir / f"backup_doanhnhan_{timestamp}.sql.gz"
        env = os.environ.copy()
        if db_conf.get("PASSWORD"):
            env["PGPASSWORD"] = str(db_conf.get("PASSWORD"))

        cmd = [
            pg_dump_bin,
            "-h", str(db_conf.get("HOST", "localhost")),
            "-p", str(db_conf.get("PORT", "5432")),
            "-U", str(db_conf.get("USER", "postgres")),
            "-d", str(db_conf.get("NAME", "doanhnhan")),
            "--no-owner",
            "--clean",
            "--if-exists",
        ]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        with gzip.open(backup_file, "wb") as f_out:
            shutil.copyfileobj(proc.stdout, f_out)
        proc.wait()

        if proc.returncode != 0:
            err_msg = proc.stderr.read().decode("utf-8", errors="replace")
            if backup_file.exists():
                backup_file.unlink()
            raise CommandError(f"Lỗi khi thực thi pg_dump: {err_msg}")

        return backup_file

    def _backup_dumpdata(self, output_dir: Path, timestamp: str) -> Path:
        backup_file = output_dir / f"backup_doanhnhan_{timestamp}.json.gz"
        with gzip.open(backup_file, "wt", encoding="utf-8") as f_out:
            call_command("dumpdata", exclude=["contenttypes", "auth.permission"], stdout=f_out, indent=2)
        return backup_file

    def _prune_old_backups(self, output_dir: Path, keep_days: int) -> int:
        cutoff_seconds = time.time() - (keep_days * 86400)
        removed = 0
        for item in output_dir.glob("backup_doanhnhan_*.*"):
            if item.is_file() and item.stat().st_mtime < cutoff_seconds:
                try:
                    item.unlink()
                    removed += 1
                except OSError as e:
                    self.stdout.write(self.style.WARNING(f"Không thể xóa {item.name}: {e}"))
        return removed
