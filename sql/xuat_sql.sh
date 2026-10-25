#!/usr/bin/env bash
# Sinh lại các tệp SQL từ một CSDL PostgreSQL vừa được tạo bằng: migrate → seed_base → seed_demo
# Dùng: PGDATABASE=dnw_export PGHOST=localhost PGUSER=postgres bash sql/xuat_sql.sh
set -euo pipefail
cd "$(dirname "$0")"
DUMP="pg_dump --no-owner --no-privileges"
TODAY=$(date +%d/%m/%Y)
hdr() { printf -- "-- doanhnhan.wiki · %s\n-- Sinh tự động từ PostgreSQL ngày %s bằng sql/xuat_sql.sh. Mã hóa UTF-8.\n-- %s\n\n" "$1" "$TODAY" "$2"; }
data() { echo "BEGIN;"; echo "SET CONSTRAINTS ALL DEFERRED;"; $DUMP --data-only --column-inserts "$@" 2>/dev/null | grep -v '^SET transaction_timeout'; echo "COMMIT;"; }

{ hdr "01 – Cấu trúc bảng" "Tương đương 'python manage.py migrate'; kèm bảng django_migrations để Django biết đã migrate tới đâu."
  $DUMP --schema-only | grep -v '^SET transaction_timeout'
  data -t django_migrations -t django_content_type -t auth_permission; } > 01_cau_truc.sql

{ hdr "02 – Dữ liệu nền (dữ liệu thật)" "34 tỉnh/thành (sắp xếp từ 12/6/2025), cây ngành nghề kèm mã VSIC 2025 cấp 2, văn bản chính sách (điều khoản sử dụng, chính sách dữ liệu), bài viết trang Donate, cài đặt chung."
  data -t directory_province -t directory_sector -t sitecontent_sitesettings -t sitecontent_donationsettings \
       -t sitecontent_policydocument -t sitecontent_policyversion; } > 02_du_lieu_nen.sql

{ hdr "03 – Dữ liệu THỬ NGHIỆM HƯ CẤU" "24 doanh nhân, 24 doanh nghiệp, 4 hiệp hội, 6 sự kiện, 11 tài khoản @example.com (mật khẩu Demo@2026!), bài gửi chờ duyệt, phỏng vấn, liên hệ, tài khoản tài trợ, video link example.com. Không phải người hay doanh nghiệp thật. Xóa trước khi chạy thật: python manage.py seed_test --xoa --xac-nhan"
  data -t directory_association -t directory_association_sectors -t directory_company -t directory_company_sectors \
       -t directory_person -t directory_personcompany -t directory_articlesection -t directory_milestone \
       -t directory_source -t directory_companyproduct -t directory_event -t directory_eventparticipant \
       -t directory_membership -t moderation_revision -t directory_video -t directory_video_persons \
       -t directory_video_companies -t directory_video_events -t directory_video_associations \
       -t accounts_user -t accounts_accountapplication -t accounts_rolechangerequest -t sitecontent_policyacceptance \
       -t moderation_profileclaim -t moderation_auditlog -t sitecontent_interviewrequest -t sitecontent_contactmessage \
       -t sitecontent_datarequest -t sitecontent_donationaccount; } > 03_du_lieu_thu_nghiem_hu_cau.sql
echo "Đã ghi 01_cau_truc.sql, 02_du_lieu_nen.sql, 03_du_lieu_thu_nghiem_hu_cau.sql"
