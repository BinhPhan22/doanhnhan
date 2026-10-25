@echo off
chcp 65001 >nul
REM Chạy doanhnhan.wiki trên Windows — SQLite, không cần cài PostgreSQL.
REM Lần đầu: tạo môi trường, cài thư viện, tạo CSDL, nạp dữ liệu nền + dữ liệu thử. Các lần sau: chỉ khởi động.
cd /d "%~dp0"

set PY=
where py >nul 2>nul && (py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul && set PY=py -3)
if "%PY%"=="" (where python >nul 2>nul && (python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul && set PY=python))
if "%PY%"=="" (
  echo Can Python 3.10 tro len. Cai tai https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^) roi chay lai.
  pause
  exit /b 1
)

if not exist .venv (
  echo ==^> Tao moi truong Python ^(.venv^)
  %PY% -m venv .venv || goto :loi
)
call .venv\Scripts\activate.bat

if not exist .venv\.cai-xong (
  echo ==^> Cai thu vien ^(lan dau mat 1-2 phut^)
  python -m pip install -q --upgrade pip
  pip install -q -r requirements.txt || goto :loi
  type nul > .venv\.cai-xong
)

set DJANGO_DEBUG=1
set PYTHONUTF8=1
echo ==^> Cap nhat co so du lieu
python manage.py migrate --noinput -v0 || goto :loi

if not exist .du-lieu-da-nap (
  echo ==^> Nap du lieu nen + du lieu thu ^(hu cau^)
  python manage.py seed_base || goto :loi
  python manage.py seed_test || goto :loi
  type nul > .du-lieu-da-nap
)

if "%PORT%"=="" set PORT=8000
echo.
echo ============================================================
echo  doanhnhan.wiki dang chay:  http://localhost:%PORT%
echo  Quan tri:                  http://localhost:%PORT%/quan-tri/
echo  Dang nhap thu: quantri1@example.com / Demo@2026!
echo  Dung: nhan Ctrl + C
echo ============================================================
start "" http://localhost:%PORT%
python manage.py runserver 127.0.0.1:%PORT%
goto :eof

:loi
echo.
echo Co loi xay ra. Chup man hinh cua so nay gui lai de duoc ho tro.
pause
exit /b 1
