# Tệp SQL cho PostgreSQL 16

Nạp vào một CSDL trống theo đúng thứ tự:

```bash
createdb doanhnhan
psql -d doanhnhan -f 01_cau_truc.sql
psql -d doanhnhan -f 02_du_lieu_nen.sql
psql -d doanhnhan -f 03_du_lieu_thu_nghiem_hu_cau.sql   # tùy chọn, để chạy thử
```

Sau đó trỏ ứng dụng vào CSDL (`DATABASE_URL=postgres://.../doanhnhan`) và tạo tài khoản quản trị: `python manage.py createsuperuser`.

- `01_cau_truc.sql` đã gồm bảng `django_migrations`, nên `python manage.py migrate` chỉ chạy các migration mới hơn.
- Cách tương đương bằng Django (khuyến nghị): `migrate` → `seed_base` → `seed_test`.
- `03_du_lieu_thu_nghiem_hu_cau.sql` là dữ liệu **hư cấu**: 24 hồ sơ, 24 doanh nghiệp, 11 tài khoản `@example.com` (mật khẩu `Demo@2026!`), bài chờ duyệt, phỏng vấn, liên hệ, tài khoản tài trợ, video link example.com. Tệp giấy tờ của yêu cầu nhận hồ sơ không nằm trong SQL (trang tải giấy tờ báo không tìm thấy tệp). Xóa sạch bằng `python manage.py seed_test --xoa --xac-nhan`.
- Các tệp được sinh lại bằng `sql/xuat_sql.sh` mỗi khi mô hình dữ liệu thay đổi.
