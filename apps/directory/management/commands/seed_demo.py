"""
Dữ liệu MẪU để chạy thử: 24 doanh nhân và 24 doanh nghiệp HƯ CẤU (gắn cờ is_demo, tên có “(hồ sơ mẫu)” / “(mẫu)”),
4 hiệp hội, 6 sự kiện, hội viên, người tham dự, dấu mốc, nguồn, bài viết.
Không tạo mã số thuế (tránh trùng doanh nghiệp thật) và không tạo video (tránh gắn link của người thật).
Kết quả luôn giống nhau giữa các lần chạy (random cố định).
Xóa toàn bộ: python manage.py seed_demo --xoa
"""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.common.text import word_count
from apps.directory.models import (
    ArticleSection, Association, Company, CompanyProduct, Event, EventParticipant, Membership, Milestone, Person,
    PersonCompany, Province, Sector, Source,
)
from apps.moderation.models import Revision

SURNAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương"]
MIDDLE = ["Minh", "Thu", "Quốc", "Thanh", "Hải", "Ngọc", "Đức", "Gia", "Khánh", "Bảo", "Thảo", "Anh"]
GIVEN = ["An", "Hà", "Bảo", "Linh", "Nam", "Vy", "Phúc", "Trang", "Khoa", "Mai", "Tuấn", "Châu",
         "Long", "Nhi", "Huy", "Ngân", "Sơn", "Thư", "Đạt", "Yến", "Tín", "My", "Quân", "Hương"]
BRANDS = ["An Phát", "Lá Xanh", "Bảo Long", "Sao Mai", "Hưng Thịnh", "Mộc Lan", "Việt Tín", "Phương Nam",
          "Đại Dương", "Hòa Bình", "Tân Tiến", "Ánh Dương", "Trường Sơn", "Kim Ngân", "Bình Minh", "Thiên Phú",
          "Hồng Hà", "Cửu Long", "Nhật Quang", "Minh Khang", "Gia Hưng", "Phú Quý", "Thành Đạt", "Vạn Xuân"]
SUBSECTORS = ["Phần mềm doanh nghiệp", "Thương mại điện tử", "Fintech", "AI & Dữ liệu", "Edtech", "Marketing số",
              "Cơ khí – chế tạo", "Vật liệu xây dựng", "Dệt may – da giày", "Bao bì – nhựa", "Chuỗi bán lẻ",
              "Phân phối", "Xuất nhập khẩu", "Chuỗi nhà hàng", "Cà phê – đồ uống", "Thực phẩm chế biến",
              "Thi công xây dựng", "Nội thất – kiến trúc", "Đào tạo kỹ năng", "Ngoại ngữ", "Nông sản sạch",
              "Thủy sản", "Vận tải", "Kho bãi"]
PROVINCES = ["tp-ho-chi-minh", "ha-noi", "da-nang", "can-tho", "hai-phong", "dong-nai", "bac-ninh", "khanh-hoa",
             "lam-dong", "an-giang", "nghe-an", "hue"]
ROLES = ["founder_ceo", "founder_ceo", "cofounder", "ceo", "founder"]
SIZES = ["lt10", "10_50", "10_50", "50_200", "gt200"]

ASSOCIATIONS = [
    ("Hội Doanh nhân trẻ mẫu Toàn quốc (mẫu)", "HDNT-TQ", "national", "ha-noi", True, None),
    ("Hội Doanh nhân trẻ mẫu TP. Hồ Chí Minh (mẫu)", "HDNT-HCM", "provincial", "tp-ho-chi-minh", True, 0),
    ("Chi hội Doanh nhân trẻ mẫu Sài Gòn (mẫu)", "CH-SG", "branch", "tp-ho-chi-minh", True, 1),
    ("CLB Doanh nhân Công nghệ mẫu (mẫu)", "CLB-CN", "club", "da-nang", False, 0),
]
EVENTS = [
    ("Diễn đàn Doanh nhân trẻ mẫu (mẫu)", "conference", 30, 1, "tp-ho-chi-minh", True),
    ("Kết nối giao thương mẫu Quý IV (mẫu)", "b2b", 45, 2, "tp-ho-chi-minh", False),
    ("Lễ vinh danh Doanh nhân trẻ mẫu (mẫu)", "award", 75, 0, "ha-noi", False),
    ("Khóa đào tạo quản trị mẫu (mẫu)", "training", -20, 3, "da-nang", False),
    ("Hội thảo chuyển đổi số mẫu (mẫu)", "conference", -60, 3, "da-nang", False),
    ("Đại hội Chi hội mẫu (mẫu)", "gala", -120, 2, "tp-ho-chi-minh", False),
]

JOURNEY = (
    "## Ý tưởng ban đầu\n"
    "Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. "
    "Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]\n\n"
    "## Những năm đầu và khó khăn\n"
    "Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện "
    "nên kèm năm và nguồn kiểm chứng.\n\n"
    "> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”\n\n"
    "## Bước ngoặt và phát triển\n"
    "Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]\n\n"
    "## Hiện nay\n"
    "Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới."
)


class Command(BaseCommand):
    help = "Tạo (hoặc --xoa để xóa) bộ dữ liệu mẫu hư cấu để chạy thử."

    def add_arguments(self, parser):
        parser.add_argument("--xoa", action="store_true", help="Xóa toàn bộ dữ liệu mẫu")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["xoa"]:
            return self.remove()
        if not Province.objects.exists() or not Sector.objects.exists():
            self.stderr.write("Chạy python manage.py seed_base trước.")
            return
        if Person.objects.filter(is_demo=True).exists():
            self.stdout.write("Dữ liệu mẫu đã có. Muốn tạo lại: seed_demo --xoa rồi seed_demo.")
            return
        rnd = random.Random(2026)
        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        prov = {p.code: p for p in Province.objects.all()}
        sectors = {s.name: s for s in Sector.objects.select_related("parent")}

        assocs = []
        for name, short, level, pcode, partner, parent_idx in ASSOCIATIONS:
            a = Association.objects.create(
                name=name, short_name=short, level=level, province=prov[pcode], is_partner=partner,
                partner_since=(now - timedelta(days=365)).date() if partner else None,
                parent=assocs[parent_idx] if parent_idx is not None else None,
                description=f"**{name}** là tổ chức hư cấu dùng để minh họa trang hiệp hội trên doanhnhan.wiki.")
            assocs.append(a)
        assocs[3].sectors.set([sectors["Công nghệ & Phần mềm"]])

        events = []
        for i, (title, kind, days, org_idx, pcode, featured) in enumerate(EVENTS):
            start = now + timedelta(days=days, hours=8 - now.hour)
            events.append(Event.objects.create(
                title=title, kind=kind, starts_at=start, ends_at=start + timedelta(hours=4),
                venue=f"Hội trường mẫu số {i + 1}", province=prov[pcode], organizer=assocs[org_idx],
                description=f"Sự kiện **hư cấu** minh họa trang sự kiện: {title}.", is_featured=featured))

        people = []
        for i in range(24):
            name = f"{SURNAMES[i % 12]} {MIDDLE[(i * 5) % 12]} {GIVEN[i]} (hồ sơ mẫu)"
            brand = f"{BRANDS[i]} (mẫu)"
            sub = sectors[SUBSECTORS[i]]
            founded = 2008 + rnd.randint(0, 14)
            pcode = PROVINCES[i % len(PROVINCES)]
            verification = ["verified", "basic", "none", "association"][i % 4]
            tax_code = f"01{10000000 + i:08d}"
            company = Company.objects.create(
                legal_name=f"Công ty TNHH {BRANDS[i]} (mẫu)", brand_name=brand, tax_code=tax_code,
                founded_year=founded, province=prov[pcode], address=f"Số {i + 1} đường Mẫu, {prov[pcode].name}",
                size_band=SIZES[i % 5], primary_sector=sub, verification=verification, is_demo=True,
                published_at=now - timedelta(days=i), is_featured=i < 4)
            company.sectors.set([sub, sub.parent])
            person = Person.objects.create(
                full_name=name, birth_year=1982 + rnd.randint(0, 14), hometown=prov[PROVINCES[(i * 7) % 12]],
                current_province=prov[pcode], headline=f"{dict(PersonCompany.Role.choices)[ROLES[i % 5]]} {brand}",
                phone=f"09{10 + (i % 89):02d}345678",
                is_featured=i < 8, verification=verification, is_demo=True,
                published_at=now - timedelta(days=i * 3), show_email=False)
            PersonCompany.objects.create(person=person, company=company, role=ROLES[i % 5], start_year=founded,
                                         is_primary=True)
            texts = {
                "summary": f"{name.replace(' (hồ sơ mẫu)', '')} là nhân vật hư cấu, {person.headline.lower()}, "
                           f"hoạt động trong lĩnh vực {sub.name.lower()} tại {prov[pcode].name}.[^1]",
                "biography": "Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, "
                             "những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.",
                "journey": JOURNEY,
            }
            if i % 2 == 0:
                texts["achievements"] = f"- {founded + 5} — Giải thưởng doanh nhân trẻ (mẫu).[^2]"
                texts["philosophy"] = "> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”"
            for order, (key, body) in enumerate(texts.items()):
                ArticleSection.objects.create(person=person, key=key, body_md=body, word_count=word_count(body),
                                              sort_order=order)
            for order, (key, body) in enumerate([
                    ("overview", f"{brand} là doanh nghiệp hư cấu trong lĩnh vực {sub.name.lower()}, minh họa "
                                 "trang doanh nghiệp trên doanhnhan.wiki.[^1]"),
                    ("history", "Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng."),
                    ("products", "Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.")]):
                ArticleSection.objects.create(company=company, key=key, body_md=body, word_count=word_count(body),
                                              sort_order=order)
            for y, kind, title in [(founded, "founding", f"Thành lập {brand}"),
                                   (founded + 3, "product", "Ra mắt sản phẩm chủ lực (mẫu)"),
                                   (founded + 6, "award", "Nhận giải thưởng doanh nhân trẻ (mẫu)")]:
                Milestone.objects.create(person=person, year=y, kind=kind, title=title)
                Milestone.objects.create(company=company, year=y, kind=kind, title=title)
            for n, (title, kind) in enumerate([("Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp", "registry"),
                                               ("Nguồn mẫu – Bài báo giới thiệu (hư cấu)", "press")], 1):
                Source.objects.create(person=person, number=n, title=title, kind=kind)
                Source.objects.create(company=company, number=n, title=title, kind=kind)
            CompanyProduct.objects.create(company=company, name=f"Sản phẩm mẫu {i + 1}", description="Mô tả ngắn 1–2 câu.")
            person.save()
            people.append(person)

        positions = ["Chủ tịch", "Phó Chủ tịch", "Tổng Thư ký", "Ủy viên Ban chấp hành"]
        for idx, a in enumerate(assocs):
            members = people[idx * 6:(idx + 1) * 6] + people[idx::5][:3]
            for order, p in enumerate(dict.fromkeys(members)):
                lead = order < 4
                Membership.objects.create(person=p, association=a, position=positions[order] if lead else "Hội viên",
                                          is_leadership=lead, sort_order=order, start_year=2020 + order % 4,
                                          state="confirmed" if order != 8 else "pending", confirmed_at=now)
        roles = ["speaker", "sponsor", "awardee", "attendee", "attendee"]
        for e_idx, e in enumerate(events):
            for k in range(5):
                p = people[(e_idx * 4 + k) % 24]
                role = roles[k]
                ep = EventParticipant.objects.create(event=e, person=p, role=role,
                                                     note="Giải Doanh nhân trẻ tiêu biểu (mẫu)" if role == "awardee" else "")
                if e.starts_at < now and role in ("speaker", "awardee"):
                    ep.milestone = Milestone.objects.create(
                        person=p, year=e.starts_at.year, kind="award" if role == "awardee" else "community",
                        title=f"{ep.get_role_display()} tại {e.title}", event=e)
                    ep.save(update_fields=["milestone"])

        for entity in [*people, *Company.objects.filter(is_demo=True)]:
            is_person = isinstance(entity, Person)
            Revision.objects.create(
                entity_type="person" if is_person else "company", kind="create",
                person=entity if is_person else None, company=None if is_person else entity,
                title=str(entity), data={}, state="approved", revision_no=1, author_role="editor",
                reviewed_at=now, note="Dữ liệu mẫu")
        self.stdout.write(self.style.SUCCESS(
            f"Đã tạo {len(people)} doanh nhân, {len(people)} doanh nghiệp, {len(assocs)} hiệp hội, {len(events)} sự kiện "
            "(tất cả hư cấu). Xóa bằng: python manage.py seed_demo --xoa"))

    def remove(self):
        people = Person.objects.filter(is_demo=True)
        companies = Company.objects.filter(is_demo=True)
        Revision.objects.filter(person__in=people).delete()
        Revision.objects.filter(company__in=companies).delete()
        Event.objects.filter(title__endswith="(mẫu)").delete()
        Association.objects.filter(name__endswith="(mẫu)").delete()
        n = people.count() + companies.count()
        people.delete()
        companies.delete()
        self.stdout.write(self.style.SUCCESS(f"Đã xóa {n} hồ sơ mẫu cùng hiệp hội, sự kiện mẫu."))
