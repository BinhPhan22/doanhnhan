"""
Bộ dữ liệu THỬ NGHIỆM đầy đủ để kiểm tra sau khi deploy — tất cả hư cấu.

Gồm: dữ liệu mẫu (seed_demo) + tài khoản đủ vai trò + bài gửi đang chờ duyệt / cần bổ sung / nháp
+ yêu cầu nhận quản lý hồ sơ + yêu cầu phỏng vấn, liên hệ, yêu cầu dữ liệu + tài khoản tài trợ (1 đang hiện, 1 chờ duyệt)
+ video mẫu (link example.com, không nhúng được) + nhật ký.

    python manage.py seed_test                       # mật khẩu mặc định Demo@2026!
    python manage.py seed_test --mat-khau "..."      # đặt mật khẩu khác cho mọi tài khoản thử
    python manage.py seed_test --xoa                 # xóa sạch dữ liệu thử + dữ liệu mẫu

Mọi tài khoản thử dùng email @example.com (tên miền dành riêng cho thử nghiệm, không gửi thư được).
Khi DJANGO_DEBUG=0 phải thêm --xac-nhan để tránh chạy nhầm trên hệ thống thật.
"""
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import AccountApplication, RoleChangeRequest, User
from apps.directory.models import Company, Event, Person, Province, Sector, Video
from apps.moderation import services
from apps.moderation.models import ProfileClaim, Revision, log
from apps.sitecontent.models import (
    ContactMessage, DataRequest, DonationAccount, InterviewRequest, PolicyAcceptance, PolicyDocument,
)

DOMAIN = "example.com"
DEFAULT_PASSWORD = "Demo@2026!"

# email, họ tên, vai trò, trạng thái, tư cách đăng ký, tổ chức, mô tả
ACCOUNTS = [
    ("quantri1", "Quản trị Một (thử)", "admin", "active", None, "", "Quản trị viên — duyệt chéo tài trợ, vai trò"),
    ("quantri2", "Quản trị Hai (thử)", "admin", "active", None, "", "Quản trị viên thứ hai"),
    ("bientap", "Biên tập Viên (thử)", "editor", "active", "contributor", "", "Biên tập viên — hàng chờ duyệt, nhập liệu"),
    ("doanhnhan", "Nguyễn Minh An (hồ sơ mẫu)", "member", "active", "entrepreneur", "An Phát (mẫu)",
     "Thành viên chính chủ — quản lý hồ sơ Nguyễn Minh An (mẫu)"),
    ("doanhnghiep", "Đại Diện Doanh Nghiệp (thử)", "member", "active", "company_rep", "Lá Xanh (mẫu)",
     "Đại diện doanh nghiệp — quản lý trang Lá Xanh (mẫu)"),
    ("hiephoi", "Đại Diện Hiệp Hội (thử)", "member", "active", "association_rep", "Hội Doanh nhân trẻ mẫu",
     "Đại diện hiệp hội"),
    ("congtacvien", "Cộng Tác Viên (thử)", "member", "active", "contributor", "", "Thành viên thường"),
    ("choduyet", "Người Chờ Duyệt (thử)", "member", "pending", "entrepreneur", "Công ty Chờ Duyệt (mẫu)",
     "Tài khoản đang chờ duyệt"),
    ("canbosung", "Người Cần Bổ Sung (thử)", "member", "pending", "company_rep", "Công ty Bổ Sung (mẫu)",
     "Đăng ký cần bổ sung thông tin"),
    ("tuchoi", "Người Bị Từ Chối (thử)", "member", "rejected", "contributor", "", "Đăng ký bị từ chối"),
    ("bikhoa", "Người Bị Khóa (thử)", "member", "suspended", "contributor", "", "Tài khoản đã bị khóa"),
]

VIDEOS = [
    ("Phỏng vấn: hành trình khởi nghiệp phần mềm (mẫu)", "interview", "persons", 0),
    ("Câu chuyện doanh nghiệp: chuỗi cà phê Lá Xanh (mẫu)", "company", "companies", 1),
    ("Bài nói tại Diễn đàn Doanh nhân trẻ (mẫu)", "talk", "persons", 2),
    ("Ghi hình Lễ vinh danh Doanh nhân trẻ (mẫu)", "event", "events", 0),
    ("Phỏng vấn: xây dựng nhà máy vật liệu (mẫu)", "interview", "persons", 3),
    ("Câu chuyện doanh nghiệp: logistics Bảo Long (mẫu)", "company", "companies", 2),
]


class Command(BaseCommand):
    help = "Tạo (hoặc --xoa) bộ dữ liệu thử nghiệm đầy đủ, gồm tài khoản đủ vai trò. Tất cả hư cấu."

    def add_arguments(self, parser):
        parser.add_argument("--mat-khau", default=DEFAULT_PASSWORD, help="Mật khẩu chung cho các tài khoản thử")
        parser.add_argument("--xoa", action="store_true", help="Xóa toàn bộ dữ liệu thử và dữ liệu mẫu")
        parser.add_argument("--xac-nhan", action="store_true", help="Bắt buộc khi DJANGO_DEBUG=0")

    def handle(self, *args, **o):
        if not settings.DEBUG and not o["xac_nhan"]:
            raise CommandError("Đang chạy chế độ production (DJANGO_DEBUG=0). Thêm --xac-nhan nếu chắc chắn "
                               "muốn tạo/xóa dữ liệu thử trên máy chủ này.")
        if o["xoa"]:
            return self.remove()
        if User.objects.filter(email=f"quantri1@{DOMAIN}").exists():
            self.stdout.write("Dữ liệu thử đã có. Muốn tạo lại: seed_test --xoa rồi seed_test.")
            return
        if not Province.objects.exists():
            call_command("seed_base", stdout=self.stdout)
        if not Person.objects.filter(is_demo=True).exists():
            call_command("seed_demo", stdout=self.stdout)
        with transaction.atomic():
            self.create(o["mat_khau"])
        cache.clear()

    # ------------------------------------------------------------------ tạo
    def create(self, password):
        now = timezone.now()
        users = {}
        policies = [d.current_version() for d in PolicyDocument.objects.filter(requires_acceptance=True)]
        for key, name, role, status, kind, org, _desc in ACCOUNTS:
            u = User.objects.create_user(email=f"{key}@{DOMAIN}", password=password, full_name=name, role=role,
                                         status=status, phone="0900000000", is_staff=role == "admin")
            users[key] = u
            for v in policies:
                if v:
                    PolicyAcceptance.objects.create(user=u, version=v, method="signup", ip="127.0.0.1")
            if kind:
                app_status = {"active": "approved", "pending": "pending", "rejected": "rejected",
                              "suspended": "approved"}[status]
                AccountApplication.objects.create(
                    user=u, applicant_type=kind, organization=org, status=app_status,
                    intro=f"Hồ sơ đăng ký thử nghiệm: {name}.", reference_url="https://example.com/gioi-thieu",
                    reviewed_by=None if app_status == "pending" else users.get("bientap"),
                    reviewed_at=None if app_status == "pending" else now,
                    review_note="Thông tin chưa đủ để xác minh (dữ liệu thử)." if status == "rejected" else "")
        AccountApplication.objects.filter(user=users["canbosung"]).update(
            status="needs_info", review_note="Vui lòng gửi link website hoặc giấy đăng ký kinh doanh (dữ liệu thử).",
            reviewed_by=users["bientap"], reviewed_at=now)
        editor, member = users["bientap"], users["doanhnhan"]

        # Chính chủ & người quản lý trang
        an = Person.objects.filter(is_demo=True, full_name__startswith="Nguyễn Minh An").first()
        if an:
            an.owner = member
            an.save(update_fields=["owner"])
        la_xanh = Company.objects.filter(is_demo=True, brand_name__startswith="Lá Xanh").first()
        if la_xanh:
            la_xanh.owner = users["doanhnghiep"]
            la_xanh.save(update_fields=["owner"])

        people = list(Person.objects.filter(is_demo=True).order_by("pk"))
        companies = list(Company.objects.filter(is_demo=True).order_by("pk"))
        hcm = Province.objects.get(code="tp-ho-chi-minh")
        fintech = Sector.objects.get(name="Fintech")

        # 1) Hồ sơ mới chờ duyệt (thành viên gửi)
        new_person = {
            "full_name": "Phạm Gia Huy (hồ sơ thử)", "birth_year": 1993, "hometown": hcm.pk, "current_province": hcm.pk,
            "headline": "Nhà sáng lập Ví Mẫu (thử)", "email_public": "", "website": "",
            "show_birth_year": True, "show_hometown": True, "show_email": False, "portrait": "",
            "companies": [{"company_id": None, "company_name": "Ví Mẫu (thử)", "role": "founder_ceo", "title": "",
                           "start_year": 2020, "end_year": None, "is_primary": True}],
            "memberships": [],
            "sections": {"summary": "Phạm Gia Huy là nhân vật thử nghiệm, sáng lập một ví điện tử mẫu.[^1]",
                         "journey": "Đoạn hành trình thử nghiệm, chưa đủ 500 từ để biên tập viên thấy cảnh báo."},
            "milestones": [{"year": 2020, "kind": "founding", "title": "Thành lập Ví Mẫu (thử)", "source_url": ""}],
            "sources": [{"title": "Nguồn thử nghiệm", "url": "https://example.com/bai-bao", "kind": "press"}],
            "videos": [],
        }
        services.submit_revision(entity_type="person", data=new_person, author=users["congtacvien"],
                                 note="Hồ sơ thử: kiểm tra cảnh báo thiếu bài viết, thiếu dấu mốc.")

        # 2) Doanh nghiệp mới chờ duyệt (đại diện doanh nghiệp gửi)
        new_company = {
            "legal_name": "Công ty Cổ phần Ví Mẫu (thử)", "brand_name": "Ví Mẫu (thử)", "tax_code": "",
            "founded_year": 2020, "province": hcm.pk, "address": "Số 1 đường Thử Nghiệm", "size_band": "10_50",
            "website": "https://example.com", "primary_sector": fintech.pk, "sectors": [fintech.pk],
            "logo": "", "cover": "",
            "sections": {"overview": "Doanh nghiệp thử nghiệm trong lĩnh vực fintech."},
            "leaders": [{"person_id": None, "person_name": "Phạm Gia Huy (hồ sơ thử)", "role": "founder_ceo",
                         "title": "", "start_year": 2020, "is_primary": True}],
            "products": [{"name": "Ứng dụng ví (thử)", "description": "Mô tả thử nghiệm."}],
            "milestones": [], "sources": [], "videos": [],
        }
        services.submit_revision(entity_type="company", data=new_company, author=users["doanhnghiep"],
                                 note="Doanh nghiệp thử: chưa có mã số thuế → có cảnh báo.")

        # 3) Chính chủ đề xuất sửa hồ sơ của mình (cập nhật chức danh + thêm dấu mốc)
        if an:
            data = services.serialize(an)
            data["headline"] = "Nhà sáng lập & CEO An Phát (mẫu), Chủ tịch Hội mẫu"
            data["milestones"].append({"year": now.year, "kind": "position", "title": "Được bầu Chủ tịch Hội (thử)",
                                       "source_url": "https://example.com/quyet-dinh"})
            data["sections"]["summary"] = data["sections"].get("summary", "") + " Cập nhật thử nghiệm năm nay."
            services.submit_revision(entity_type="person", data=data, author=member, instance=an,
                                     note="Chính chủ cập nhật chức danh và dấu mốc mới.")

        # 4) Bản cần bổ sung + 5) bản nháp
        if len(companies) > 2:
            data = services.serialize(companies[2])
            data["size_band"] = "50_200"
            rev = services.submit_revision(entity_type="company", data=data, author=users["congtacvien"],
                                           instance=companies[2], note="Đề nghị đổi quy mô nhân sự.")
            services.reject(rev, editor, "Vui lòng thêm nguồn xác nhận quy mô nhân sự (dữ liệu thử).", needs_info=True)
        if len(people) > 5:
            data = services.serialize(people[5])
            data["website"] = "https://example.com/linkedin"
            services.submit_revision(entity_type="person", data=data, author=users["congtacvien"],
                                     instance=people[5], as_draft=True, note="Bản nháp chưa gửi.")

        # 6) Nhận quản lý hồ sơ chờ duyệt (giấy tờ là tệp PDF giả)
        if len(people) > 1:
            claim = ProfileClaim(person=people[1], user=users["hiephoi"], note="Tôi là chính chủ (dữ liệu thử).")
            claim.evidence.save("giay-to-thu.pdf", ContentFile(b"%PDF-1.4\n% Tep thu nghiem doanhnhan.wiki\n%%EOF\n"),
                                save=False)
            claim.save()

        # 7) Liên hệ, phỏng vấn, yêu cầu dữ liệu
        for i, (state, kind, fmt) in enumerate([("new", "interview", "onsite"), ("scheduled", "company", "studio"),
                                                ("published", "event", "event")]):
            InterviewRequest.objects.create(
                full_name=f"Người Liên Hệ {i + 1} (thử)", title="Nhà sáng lập", company=f"Công ty Liên Hệ {i + 1} (thử)",
                phone="0900000000", email=f"lienhe{i + 1}@{DOMAIN}", kind=kind, format=fmt, state=state,
                story="Câu chuyện thử nghiệm muốn chia sẻ.",
                preferred_time=timezone.now() + timezone.timedelta(days=7 + i),
                address="123 Đường Số 1, Quận 1, TP. Hồ Chí Minh",
                assignee=editor if state != "new" else None)
        ContactMessage.objects.create(topic="partner", full_name="Đại diện Hội thử", organization="Hội thử",
                                      email=f"doitac@{DOMAIN}", message="Đăng ký làm hiệp hội đối tác (thử).")
        ContactMessage.objects.create(topic="correction", full_name="Người đọc thử", email=f"docgia@{DOMAIN}",
                                      message="Năm thành lập trên một hồ sơ mẫu chưa đúng (thử).")
        DataRequest.objects.create(full_name="Người yêu cầu thử", email=f"dulieu@{DOMAIN}", kind="correct",
                                   profile_url="/doanh-nhan/", detail="Đề nghị sửa quê quán (dữ liệu thử).")

        # 8) Tài khoản tài trợ: 1 đang hiện (đã duyệt chéo), 1 chờ quản trị viên thứ hai
        DonationAccount.objects.create(
            bank_name="Ngân hàng Mẫu (dữ liệu thử)", account_number="0000000001",
            account_holder="CONG TY MAU - DU LIEU THU", state="active", created_by=users["quantri1"],
            approved_by=users["quantri2"], approved_at=now)
        DonationAccount.objects.create(
            bank_name="Ngân hàng Mẫu 2 (dữ liệu thử)", account_number="0000000002",
            account_holder="CONG TY MAU - DU LIEU THU", state="pending", created_by=users["quantri1"])

        # 9) Yêu cầu nâng quyền chờ quản trị viên thứ hai
        RoleChangeRequest.objects.create(target=editor, new_role="admin", requested_by=users["quantri1"])

        # 10) Video mẫu — link example.com: hiện nút “Xem trên nền tảng khác”, không nhúng
        events = list(Event.objects.filter(title__endswith="(mẫu)").order_by("pk"))
        for i, (title, kind, target, idx) in enumerate(VIDEOS):
            v = Video.objects.create(url=f"https://example.com/video-mau-{i + 1}", title=title, kind=kind,
                                     duration_seconds=300 + i * 95, channel_name="Kênh mẫu (thử)",
                                     published_on=(now - timedelta(days=10 * i)).date(), availability="ok",
                                     is_featured=i == 0)
            if target == "persons" and people:
                v.persons.add(people[idx])
            elif target == "companies" and companies:
                v.companies.add(companies[idx])
            elif events:
                v.events.add(events[idx])

        log(users["quantri1"], "test_data.create", None, "Tạo bộ dữ liệu thử nghiệm")
        self.print_summary(password)

    def print_summary(self, password):
        self.stdout.write(self.style.SUCCESS("\nĐã tạo bộ dữ liệu thử nghiệm (hư cấu). Tài khoản đăng nhập:"))
        for key, _name, role, status, _k, _o, desc in ACCOUNTS:
            self.stdout.write(f"  {key + '@' + DOMAIN:28} {role:7} {status:10} {desc}")
        self.stdout.write(f"  Mật khẩu chung: {password}")
        self.stdout.write("Xóa toàn bộ trước khi chạy thật: python manage.py seed_test --xoa")

    # ------------------------------------------------------------------ xóa
    def remove(self):
        with transaction.atomic():
            users = User.objects.filter(email__endswith=f"@{DOMAIN}")
            Revision.objects.filter(author__in=users).delete()
            Revision.objects.filter(title__contains="(thử)").delete()
            for c in ProfileClaim.objects.filter(user__in=users):
                c.evidence.delete(save=False)
                c.delete()
            InterviewRequest.objects.filter(email__endswith=f"@{DOMAIN}").delete()
            ContactMessage.objects.filter(email__endswith=f"@{DOMAIN}").delete()
            DataRequest.objects.filter(email__endswith=f"@{DOMAIN}").delete()
            DonationAccount.objects.filter(bank_name__contains="(dữ liệu thử)").delete()
            Video.objects.filter(url__startswith="https://example.com/video-mau-").delete()
            Person.objects.filter(full_name__endswith="(hồ sơ thử)").delete()
            Company.objects.filter(brand_name__endswith="(thử)").delete()
            Company.objects.filter(legal_name__endswith="(thử)").delete()
            n = users.count()
            users.delete()
        call_command("seed_demo", "--xoa", stdout=self.stdout)
        cache.clear()
        self.stdout.write(self.style.SUCCESS(f"Đã xóa {n} tài khoản thử và dữ liệu thử nghiệm."))
