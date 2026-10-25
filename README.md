# doanhnhan.wiki — mã nguồn website

Trang cộng đồng lưu giữ hồ sơ doanh nhân trẻ tiêu biểu Việt Nam: doanh nhân, doanh nghiệp, ngành nghề, hiệp hội, sự kiện, video (chỉ nhúng link). Ai cũng xem được; muốn đưa thông tin lên phải có tài khoản được ban quản trị duyệt, và mọi nội dung đều qua biên tập viên duyệt trước khi công bố.

Công nghệ: **Python 3.12+ / Django 5.2**, **PostgreSQL 16** (máy phát triển dùng được SQLite), giao diện HTML/CSS/JS thuần (không framework), Gunicorn + Nginx + Docker khi triển khai.

---

## 1. Chạy thử trên máy (5 phút)

**Cách nhanh nhất — nhấp đúp một tệp** (cần Python 3.10+; lần đầu tự cài thư viện, tạo CSDL SQLite, nạp dữ liệu thử rồi mở trình duyệt):

- Windows: `chay_local.bat`
- macOS / Linux: `./chay_local.sh` (trong Terminal)
- Có Docker Desktop, muốn dùng PostgreSQL giống máy chủ thật: `docker compose -f docker-compose.local.yml up --build`

Mở http://localhost:8000, đăng nhập thử `quantri1@example.com` / `Demo@2026!`.

Cài thủ công từng bước:

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_base          # 34 tỉnh/thành, ngành nghề, chính sách, bài viết trang Donate
python manage.py seed_test          # (tùy chọn) dữ liệu thử HƯ CẤU + 11 tài khoản đủ vai trò; xóa: seed_test --xoa
python manage.py createsuperuser    # tài khoản quản trị đầu tiên
python manage.py runserver
```

Mở http://localhost:8000 — trang quản trị ở http://localhost:8000/quan-tri/. Email (thông báo duyệt, đặt lại mật khẩu) in ra cửa sổ dòng lệnh khi chạy ở máy.

Chạy kiểm thử: `python manage.py test` (29 kịch bản: đăng ký → duyệt tài khoản → gửi hồ sơ → duyệt → công bố, yêu cầu bổ sung, khóa đăng nhập, tài khoản tài trợ cần 2 quản trị viên, đồng ý lại điều khoản, ẩn video hỏng, API…).

**Dùng tệp SQL thay cho lệnh seed** (PostgreSQL): xem `sql/README.md` — `01_cau_truc.sql`, `02_du_lieu_nen.sql`, `03_du_lieu_mau_hu_cau.sql`.

### Tài khoản thử nghiệm (`seed_test`)

Mật khẩu chung `Demo@2026!` (đổi bằng `--mat-khau`). Trên máy chủ có `DJANGO_DEBUG=0` phải thêm `--xac-nhan`.

| Email | Vai trò | Dùng để thử |
|---|---|---|
| quantri1@example.com, quantri2@example.com | Quản trị viên | Duyệt chéo tài khoản tài trợ, xác nhận nâng quyền, chính sách, nhật ký |
| bientap@example.com | Biên tập viên | Hàng chờ duyệt (3 bài chờ, 1 cần bổ sung), duyệt tài khoản, nhận hồ sơ, phỏng vấn |
| doanhnhan@example.com | Thành viên (chính chủ) | Quản lý hồ sơ Nguyễn Minh An (mẫu), đã gửi 1 đề xuất sửa |
| doanhnghiep@example.com | Thành viên (đại diện DN) | Quản lý trang Lá Xanh (mẫu), đã gửi 1 doanh nghiệp mới |
| hiephoi@example.com | Thành viên (đại diện hội) | Có 1 yêu cầu nhận quản lý hồ sơ đang chờ |
| congtacvien@example.com | Thành viên | Có 1 bài cần bổ sung, 1 bản nháp |
| choduyet@, canbosung@, tuchoi@, bikhoa@example.com | Chờ duyệt / cần bổ sung / từ chối / bị khóa | Kiểm tra các trạng thái tài khoản |

**Trước khi mở cửa thật:** `python manage.py seed_test --xoa --xac-nhan` — chỉ còn lại dữ liệu nền.

## 2. Triển khai lên máy chủ (Docker)

```bash
cp .env.example .env        # điền DJANGO_SECRET_KEY, POSTGRES_PASSWORD, SMTP, tên miền…
docker compose up -d --build
docker compose exec web python manage.py seed_base
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_test --xac-nhan   # (tùy chọn) dữ liệu thử
```

- Nginx phục vụ `/media/` (ảnh đã duyệt). Thư mục **private_media** (giấy tờ xác minh, ảnh chờ duyệt) **không** được Nginx phục vụ — chỉ tải qua trang quản trị có kiểm tra quyền.
- Đặt HTTPS phía trước (Cloudflare, Caddy hoặc certbot). Khi đã có HTTPS: `SECURE_SSL_REDIRECT=1`, `SECURE_HSTS_SECONDS=31536000`.
- Sao lưu: `docker compose exec db pg_dump -U doanhnhan doanhnhan > backup.sql` và sao lưu 2 volume `media`, `private_media`.

**Việc định kỳ (cron)** — kiểm tra link video mỗi ngày, video hỏng tự ẩn và email báo ban biên tập:

```
0 3 * * *  cd /srv/doanhnhan && docker compose exec -T web python manage.py check_videos
```

## 3. Phân quyền

| Vai trò | Làm được gì |
|---|---|
| Khách (không tài khoản) | Xem toàn bộ thông tin công khai, tìm kiếm, gửi liên hệ ghi hình/phỏng vấn, góp ý, yêu cầu về dữ liệu cá nhân |
| Thành viên **chờ duyệt** | Đăng nhập, chỉ thấy thông báo “đang chờ duyệt” |
| Thành viên **đã duyệt** | Gửi hồ sơ doanh nhân / doanh nghiệp, đề xuất sửa, lưu nháp, bổ sung khi được yêu cầu, nhận quản lý hồ sơ của chính mình |
| Biên tập viên | Hàng chờ duyệt (so sánh thay đổi + gợi ý tự động), duyệt tài khoản thành viên, nhập liệu trực tiếp mọi mục, hội viên hiệp hội, sự kiện & người tham gia, video, yêu cầu phỏng vấn, liên hệ |
| Quản trị viên | Thêm: người dùng & vai trò, trang tài trợ, chính sách & điều khoản, yêu cầu dữ liệu cá nhân, nhật ký hệ thống, cài đặt chung |

Hai thao tác nhạy cảm cần **hai quản trị viên khác nhau**: (1) cấp/thu hồi quyền Quản trị viên; (2) thêm hoặc thay tài khoản nhận tài trợ (người tạo không tự duyệt được).

## 4. Nhập liệu & quản trị từng mục

| Mục | Ai nhập | Ở đâu | Ghi chú |
|---|---|---|---|
| Doanh nhân | Thành viên (chờ duyệt) / Biên tập viên (công bố ngay) | `/thanh-vien/gui/doanh-nhan/`, `/quan-tri/doanh-nhan/` | Thông tin cơ bản, ảnh, doanh nghiệp + vai trò, hiệp hội, 6 mục bài viết (markdown, chú thích `[^1]`), dấu mốc, video, nguồn |
| Doanh nghiệp | như trên | `/thanh-vien/gui/doanh-nghiep/`, `/quan-tri/doanh-nghiep/` | MST (kiểm tra định dạng + trùng), ngành chính & phân ngành, 6 mục bài viết, ban lãnh đạo, sản phẩm, dấu mốc, video, nguồn |
| Ngành nghề | Biên tập viên | `/quan-tri/nganh-nghe/` | 2 cấp: ngành → phân ngành; biểu tượng, mã VSIC |
| Hiệp hội | Biên tập viên | `/quan-tri/hiep-hoi/` | Cấp, trực thuộc, đối tác; **Hội viên**: thêm, xác nhận, ban chấp hành |
| Sự kiện | Biên tập viên | `/quan-tri/su-kien/` | Người tham gia (diễn giả, nhận giải…), tùy chọn ghi thành **dấu mốc** trên hồ sơ |
| Video | Biên tập viên (hoặc kèm hồ sơ khi thành viên gửi) | `/quan-tri/video/` | Chỉ dán link YouTube/Vimeo/Facebook/TikTok; tự lấy tiêu đề, ảnh bìa; gắn với doanh nhân, doanh nghiệp, sự kiện, hiệp hội |
| Trang Donate | Quản trị viên | `/quan-tri/tai-tro/` | Sửa bài kêu gọi, nội dung chuyển khoản; tài khoản nhận cần quản trị viên thứ hai duyệt |
| Chính sách | Quản trị viên | `/quan-tri/chinh-sach/` | Phiên bản, ngày hiệu lực, lên lịch, yêu cầu đồng ý lại |

**Liên kết tự động:** gõ tên doanh nghiệp/doanh nhân sẽ có gợi ý; chọn gợi ý thì hồ sơ được nối với nhau (trang doanh nghiệp tự hiện ban lãnh đạo, trang doanh nhân tự hiện doanh nghiệp, trang ngành tự hiện doanh nhân của các doanh nghiệp thuộc ngành, trang hiệp hội tự hiện hội viên, trang sự kiện tự hiện người tham gia, khối video tự hiện ở mọi trang liên quan và **tự ẩn khi không có video**). Tên chưa có trong hệ thống được tạo thành bản nháp để ban biên tập hoàn thiện.

**Lịch sử sửa đổi:** mọi lần công bố là một phiên bản (`/doanh-nhan/<tên>/lich-su/`). Nhật ký hệ thống (`/quan-tri/nhat-ky/`) chỉ ghi thêm, không sửa/xóa.

## 5. API v1 (đọc công khai)

`/api/v1/` trả JSON dữ liệu đã công bố: `provinces`, `sectors`, `persons`, `companies`, `associations`, `events`, `videos`, `search`. Không cần khóa, CORS mở, phân trang `page`/`page_size` (≤ 100), giới hạn `API_RATE_LIMIT_PER_MIN` (mặc định 120). Đặc tả OpenAPI 3.1: `docs/openapi.yaml` (cũng tại `/api/v1/openapi.yaml`). API ghi (giai đoạn 2) chưa triển khai — đề xuất trong tài liệu bàn giao.

## 6. Cấu trúc mã nguồn

```
config/            cấu hình (đọc từ biến môi trường), URL gốc
apps/common/       tiện ích: bỏ dấu tìm kiếm, slug, markdown an toàn, nhận dạng video, phân quyền, email
apps/accounts/     người dùng, đăng ký/duyệt tài khoản, Google, khóa đăng nhập, đồng ý điều khoản
apps/directory/    dữ liệu chính: tỉnh, ngành, doanh nhân, doanh nghiệp, bài viết, dấu mốc, nguồn, hiệp hội, sự kiện, video
apps/moderation/   bản sửa đổi (Revision), luồng duyệt, so sánh, gợi ý tự động, nhận quản lý hồ sơ, nhật ký
apps/sitecontent/  cài đặt, trang tài trợ, chính sách & phiên bản, liên hệ, phỏng vấn, yêu cầu dữ liệu
apps/public/       trang công khai     apps/member/  khu vực thành viên     apps/staff/  bảng quản trị
templates/         giao diện (giữ đúng thiết kế đã duyệt)     static/  styles.css, app.css, main.js
```

## 7. Cần lưu ý

- **Văn bản pháp lý** (Điều khoản, Chính sách dữ liệu, Quy định tài trợ) mới là **bản khung** có đánh dấu `[Nội dung do luật sư soạn]` — cần luật sư hoàn thiện rồi đăng phiên bản mới trong `/quan-tri/chinh-sach/`.
- **“Gợi ý tự động”** khi duyệt là kiểm tra **theo quy tắc** (trùng tên, MST, số từ, nguồn, dấu mốc, link video), **không dùng AI**. Có thể nối thêm dịch vụ AI sau trong `apps/moderation/services.py → compute_checks()`.
- **Tra cứu mã số thuế** chỉ kiểm tra định dạng và trùng lặp; đối chiếu với Cổng thông tin quốc gia về đăng ký doanh nghiệp vẫn do biên tập viên làm thủ công (cổng này không có API công khai).
- **Đăng nhập Google** chỉ hiện khi đặt `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`.
- Dữ liệu `seed_demo` là **hư cấu**, có nhãn “Mẫu” — xóa bằng `python manage.py seed_demo --xoa` trước khi chạy thật.
- Mã ngành trong cây ngành nghề là mã **cấp 2 theo VSIC 2025** (Quyết định 36/2025/QĐ-TTg, hiệu lực 15/11/2025) để tham chiếu; đăng ký kinh doanh dùng mã cấp 4.
- Danh sách 34 tỉnh/thành theo sắp xếp đơn vị hành chính cấp tỉnh có hiệu lực từ 12/6/2025; sửa được trong Django admin (`/django-admin/`, chỉ dành cho kỹ thuật).
