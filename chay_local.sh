#!/usr/bin/env bash
# Chạy doanhnhan.wiki trên máy cá nhân (macOS / Linux) — SQLite, không cần cài PostgreSQL.
# Lần đầu: tạo môi trường, cài thư viện, tạo CSDL, nạp dữ liệu nền + dữ liệu thử. Các lần sau: chỉ khởi động.
set -e
cd "$(dirname "$0")"

PY=""
for c in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "Cần Python 3.10 trở lên. Cài tại https://www.python.org/downloads/ rồi chạy lại."; exit 1
fi

if [ ! -d .venv ]; then
  echo "==> Tạo môi trường Python (.venv)"
  "$PY" -m venv .venv
fi
source .venv/bin/activate

if [ ! -f .venv/.cai-xong ] || [ requirements.txt -nt .venv/.cai-xong ]; then
  echo "==> Cài thư viện (lần đầu mất 1–2 phút)"
  pip install -q --upgrade pip
  pip install -q -r requirements.txt
  touch .venv/.cai-xong
fi

export DJANGO_DEBUG=1
echo "==> Cập nhật cơ sở dữ liệu"
python manage.py migrate --noinput -v0

if [ ! -f .du-lieu-da-nap ]; then
  echo "==> Nạp dữ liệu nền + dữ liệu thử (hư cấu)"
  python manage.py seed_base
  python manage.py seed_test
  touch .du-lieu-da-nap
fi

PORT="${PORT:-8000}"
echo ""
echo "============================================================"
echo " doanhnhan.wiki đang chạy:  http://localhost:$PORT"
echo " Quản trị:                  http://localhost:$PORT/quan-tri/"
echo " Đăng nhập thử: quantri1@example.com / Demo@2026!"
echo " (bientap@, doanhnhan@, doanhnghiep@... xem README)"
echo " Dừng: nhấn Ctrl + C"
echo "============================================================"
( sleep 2; (command -v open >/dev/null && open "http://localhost:$PORT") || (command -v xdg-open >/dev/null && xdg-open "http://localhost:$PORT") ) >/dev/null 2>&1 &
python manage.py runserver "127.0.0.1:$PORT"
