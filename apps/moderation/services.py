"""
Luồng nhập liệu & duyệt cho doanh nhân / doanh nghiệp.

Dữ liệu một hồ sơ được biểu diễn bằng một "payload" (dict JSON) giống nhau ở mọi nơi:
- form nhập liệu đọc từ payload để hiển thị và tạo payload từ POST;
- bản sửa đổi (Revision) lưu payload;
- khi duyệt, payload được ghi vào các bảng chính (apply_revision).
"""
from __future__ import annotations

import difflib
import os
import uuid

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.validators import EmailValidator, URLValidator
from django.db import transaction
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe

from apps.common import video as video_lib
from apps.common.text import normalize, word_count
from apps.common.validators import TAX_CODE_RE
from apps.directory.models import (
    COMPANY_SECTIONS, PERSON_SECTIONS, ArticleSection, Association, Company, CompanyProduct, Membership,
    Milestone, Person, PersonCompany, Province, Sector, Source, Status, Video,
)
import re

from .models import Revision, log, private_storage

PERSON_FIELDS = [
    ("full_name", "Họ và tên"), ("birth_year", "Năm sinh"), ("hometown", "Quê quán"),
    ("current_province", "Nơi hoạt động chính"), ("headline", "Dòng chức danh"),
    ("phone", "Số điện thoại (bảo mật)"), ("email_public", "Email công khai"),
    ("website", "Website / LinkedIn"), ("show_birth_year", "Công khai năm sinh"),
    ("show_hometown", "Công khai quê quán"), ("show_email", "Công khai email"),
]
COMPANY_FIELDS = [
    ("legal_name", "Tên theo đăng ký kinh doanh"), ("brand_name", "Tên thương hiệu"), ("tax_code", "Mã số thuế"),
    ("founded_year", "Năm thành lập"), ("province", "Trụ sở"), ("address", "Địa chỉ"),
    ("size_band", "Quy mô nhân sự"), ("website", "Website"), ("primary_sector", "Ngành chính"),
    ("sectors", "Ngành, phân ngành"),
]
STAFF_FIELDS = [("status", "Trạng thái"), ("verification", "Xác minh"), ("verification_note", "Ghi chú xác minh"),
                ("is_featured", "Nổi bật")]
IMAGE_FIELDS = {"person": ["portrait"], "company": ["logo", "cover"]}
UPLOAD_TO = {"portrait": "portraits/%Y/", "logo": "logos/%Y/", "cover": "company-covers/%Y/"}

_url = URLValidator(schemes=["http", "https"])
_email = EmailValidator()


# --------------------------------------------------------------------------- tiện ích
def _int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _rows(post, prefix, fields):
    """Đọc các dòng lặp lại (cùng tên input) thành danh sách dict; bỏ dòng trống hoàn toàn."""
    columns = {f: post.getlist(f"{prefix}_{f}") for f in fields}
    length = max((len(v) for v in columns.values()), default=0)
    rows = []
    for i in range(length):
        row = {f: (columns[f][i].strip() if i < len(columns[f]) else "") for f in fields}
        if any(row.values()):
            rows.append(row)
    return rows


def _valid_url(value):
    if not value:
        return True
    try:
        _url(value)
        return True
    except ValidationError:
        return False


def find_company(text):
    """Tìm doanh nghiệp theo tên thương hiệu, tên pháp lý hoặc mã số thuế (chuỗi người dùng gõ)."""
    text = (text or "").strip()
    if not text:
        return None
    if TAX_CODE_RE.match(text):
        return Company.objects.filter(tax_code=text).first()
    if text.endswith(")") and "(MST " in text:
        tax = text.rsplit("(MST ", 1)[1].rstrip(")")
        found = Company.objects.filter(tax_code=tax).first()
        if found:
            return found
        text = text.rsplit("(MST ", 1)[0].strip()
    key = normalize(text)
    for c in Company.objects.filter(search_text__contains=key)[:20]:
        if normalize(c.display_name) == key or normalize(c.legal_name) == key:
            return c
    return None


def find_person(text):
    text = (text or "").strip()
    if not text:
        return None
    if text.endswith(")") and "(#" in text:
        found = Person.objects.filter(pk=_int(text.rsplit("(#", 1)[1].rstrip(")"))).first()
        if found:
            return found
        text = text.rsplit("(#", 1)[0].strip()
    key = normalize(text)
    matches = [p for p in Person.objects.filter(search_text__contains=key)[:20] if normalize(p.full_name) == key]
    return matches[0] if len(matches) == 1 else None


def company_label(c):
    return f"{c.display_name} (MST {c.tax_code})" if c.tax_code else c.display_name


def person_label(p):
    return f"{p.full_name} (#{p.pk})"


def stash_upload(upload):
    """Lưu ảnh của bản chờ duyệt vào vùng riêng tư; chỉ chuyển ra công khai khi được duyệt."""
    ext = os.path.splitext(upload.name)[1].lower() or ".jpg"
    return private_storage.save(f"pending/{timezone.now():%Y/%m}/{uuid.uuid4().hex}{ext}", upload)


def promote_upload(path, field):
    if not path or not path.startswith("pending/") or not private_storage.exists(path):
        return path
    with private_storage.open(path, "rb") as fh:
        name = default_storage.save(timezone.now().strftime(UPLOAD_TO[field]) + os.path.basename(path),
                                    ContentFile(fh.read()))
    return name


# --------------------------------------------------------------------------- POST → payload
def parse_post(entity_type, request, base=None, staff=False):
    """Đọc form nhập liệu. Trả về (payload, errors)."""
    post, files = request.POST, request.FILES
    base = base or {}
    data, errors = {}, {}
    sections_def = PERSON_SECTIONS if entity_type == "person" else COMPANY_SECTIONS

    if entity_type == "person":
        data["full_name"] = post.get("full_name", "").strip()
        if not data["full_name"]:
            errors["full_name"] = "Vui lòng nhập họ và tên."
        data["birth_year"] = _int(post.get("birth_year"))
        if data["birth_year"] and not 1920 <= data["birth_year"] <= timezone.now().year:
            errors["birth_year"] = "Năm sinh không hợp lệ."
        data["hometown"] = _int(post.get("hometown"))
        data["current_province"] = _int(post.get("current_province"))
        data["headline"] = post.get("headline", "").strip()[:200]
        data["phone"] = ""
        raw_phone = post.get("phone", "").strip()[:30]
        if raw_phone:
            if "*" in raw_phone:
                data["phone"] = base.get("phone", "")
            else:
                cleaned = re.sub(r"[\s\.\-\(\)]", "", raw_phone)
                if len(cleaned) < 9 or not re.match(r"^(\+?84|0)\d{8,11}$", cleaned):
                    errors["phone"] = "Số điện thoại không hợp lệ (từ 9 đến 11 chữ số, bắt đầu bằng 0 hoặc +84)."
                else:
                    data["phone"] = raw_phone
        data["email_public"] = post.get("email_public", "").strip()
        if data["email_public"]:
            try:
                _email(data["email_public"])
            except ValidationError:
                errors["email_public"] = "Email không hợp lệ."
        data["website"] = post.get("website", "").strip()
        for key in ("show_birth_year", "show_hometown", "show_email"):
            data[key] = post.get(key) == "on"
        data["companies"] = []
        for row in _rows(post, "company", ["name", "tax", "role", "title", "start", "end", "primary"]):
            raw_tax = row.get("tax", "").strip()
            found = None
            if raw_tax and TAX_CODE_RE.match(raw_tax):
                found = Company.objects.filter(tax_code=raw_tax).first()
            if not found and row.get("name"):
                found = find_company(row["name"])

            company_tax = found.tax_code if (found and found.tax_code) else raw_tax
            data["companies"].append({
                "company_id": found.pk if found else None,
                "company_name": found.display_name if found else row["name"],
                "tax_code": company_tax,
                "role": row["role"] or "founder_ceo", "title": row["title"][:120],
                "start_year": _int(row["start"]), "end_year": _int(row["end"]), "is_primary": row["primary"] == "1",
            })
        if data["companies"] and not any(c["is_primary"] for c in data["companies"]):
            data["companies"][0]["is_primary"] = True
        data["memberships"] = []
        for row in _rows(post, "assoc", ["id", "position", "start"]):
            if _int(row["id"]):
                data["memberships"].append({"association_id": _int(row["id"]),
                                            "position": row["position"][:100] or "Hội viên",
                                            "start_year": _int(row["start"])})
    else:
        data["legal_name"] = post.get("legal_name", "").strip()
        if not data["legal_name"]:
            errors["legal_name"] = "Vui lòng nhập tên theo đăng ký kinh doanh."
        data["brand_name"] = post.get("brand_name", "").strip()[:120]
        existing_tax = (base.get("tax_code") or "").strip()
        is_existing_company = bool(base.get("id"))
        if existing_tax:
            # Mã số thuế đã có thì không thể thay đổi (bất biến)
            data["tax_code"] = existing_tax
        else:
            tax = post.get("tax_code", "").strip()
            data["tax_code"] = tax
            if not tax:
                if not is_existing_company:
                    errors["tax_code"] = "Vui lòng nhập mã số thuế doanh nghiệp (bắt buộc)."
            elif not TAX_CODE_RE.match(tax):
                errors["tax_code"] = "Mã số thuế gồm 10 chữ số (hoặc 10 số kèm -xxx cho chi nhánh)."
        data["founded_year"] = _int(post.get("founded_year"))
        if data["founded_year"] and not 1900 <= data["founded_year"] <= timezone.now().year:
            errors["founded_year"] = "Năm thành lập không hợp lệ."
        data["province"] = _int(post.get("province"))
        data["address"] = post.get("address", "").strip()[:255]
        data["size_band"] = post.get("size_band", "")
        data["website"] = post.get("website", "").strip()
        data["primary_sector"] = _int(post.get("primary_sector"))
        data["sectors"] = sorted({i for i in (_int(v) for v in post.getlist("sectors")) if i})
        data["leaders"] = []
        for row in _rows(post, "leader", ["name", "role", "title", "start", "primary"]):
            found = find_person(row["name"])
            data["leaders"].append({
                "person_id": found.pk if found else None,
                "person_name": found.full_name if found else row["name"],
                "role": row["role"] or "founder_ceo", "title": row["title"][:120],
                "start_year": _int(row["start"]), "is_primary": row["primary"] == "1",
            })
        data["products"] = [{"name": r["name"][:150], "description": r["description"][:300]}
                            for r in _rows(post, "product", ["name", "description"]) if r["name"]]

    data["awards"] = []
    for row in _rows(post, "award", ["badge_id", "year", "title", "citation"]):
        bid = _int(row["badge_id"])
        if bid:
            data["awards"].append({
                "badge_id": bid,
                "year": _int(row["year"]),
                "year_awarded": _int(row["year"]),
                "title": (row.get("title") or "").strip()[:150],
                "citation": (row.get("citation") or "").strip()[:255],
            })

    if data.get("website") and not _valid_url(data["website"]):
        errors["website"] = "Link phải bắt đầu bằng http:// hoặc https://"

    data["sections"] = {}
    for key, _label, _hint in sections_def:
        body = post.get(f"section_{key}", "").strip()
        if body:
            data["sections"][key] = body

    data["milestones"] = []
    for row in _rows(post, "milestone", ["year", "kind", "title", "source"]):
        year = _int(row["year"])
        if not year or not row["title"]:
            errors["milestones"] = "Mỗi dấu mốc cần có năm và nội dung."
            continue
        if row["source"] and not _valid_url(row["source"]):
            errors["milestones"] = "Link nguồn của dấu mốc không hợp lệ."
        data["milestones"].append({"year": year, "kind": row["kind"] or "other", "title": row["title"][:255],
                                   "source_url": row["source"]})
    data["milestones"].sort(key=lambda m: m["year"])

    data["sources"] = []
    for row in _rows(post, "source", ["title", "url", "kind"]):
        if not row["title"] and not row["url"]:
            continue
        if row["url"] and not _valid_url(row["url"]):
            errors["sources"] = "Link nguồn tham khảo không hợp lệ."
        data["sources"].append({"title": (row["title"] or row["url"])[:300], "url": row["url"],
                                "kind": row["kind"] or "press"})

    data["videos"] = []
    for row in _rows(post, "video", ["url", "title"]):
        if not row["url"]:
            continue
        if not _valid_url(row["url"]):
            errors["videos"] = "Link video không hợp lệ."
            continue
        data["videos"].append({"url": row["url"], "title": row["title"][:300]})

    stashed = request.session.get("stashed_uploads", []) if hasattr(request, "session") else []
    for field in IMAGE_FIELDS[entity_type]:
        data[field] = base.get(field, "")
        keep = post.get(f"keep_{field}", "")
        if keep and keep in stashed:
            data[field] = keep
        if post.get(f"remove_{field}") == "on":
            data[field] = ""
        upload = files.get(field)
        if upload:
            if upload.size > 5 * 1024 * 1024:
                errors[field] = "Ảnh tối đa 5 MB."
            elif os.path.splitext(upload.name)[1].lower() not in (".jpg", ".jpeg", ".png", ".webp"):
                errors[field] = "Chỉ nhận ảnh JPG, PNG hoặc WEBP."
            else:
                data[field] = stash_upload(upload)
                if hasattr(request, "session"):
                    request.session["stashed_uploads"] = (stashed + [data[field]])[-20:]

    if staff:
        data["status"] = post.get("status") if post.get("status") in Status.values else Status.PUBLISHED
        data["verification"] = post.get("verification", "none")
        data["verification_note"] = post.get("verification_note", "").strip()[:255]
        data["is_featured"] = post.get("is_featured") == "on"
    return data, errors


# --------------------------------------------------------------------------- bản ghi → payload
def serialize_person(p: Person) -> dict:
    return {
        "full_name": p.full_name, "birth_year": p.birth_year, "hometown": p.hometown_id,
        "current_province": p.current_province_id, "headline": p.headline, "email_public": p.email_public,
        "phone": p.phone or "",
        "website": p.website, "show_birth_year": p.show_birth_year, "show_hometown": p.show_hometown,
        "show_email": p.show_email, "portrait": p.portrait.name if p.portrait else "",
        "sections": {s.key: s.body_md for s in p.sections.all()},
        "companies": [{"company_id": l.company_id, "company_name": l.company.display_name,
                       "tax_code": l.company.tax_code or "", "role": l.role,
                       "title": l.title, "start_year": l.start_year, "end_year": l.end_year,
                       "is_primary": l.is_primary} for l in p.company_links.select_related("company")],
        "memberships": [{"association_id": m.association_id, "position": m.position, "start_year": m.start_year}
                        for m in p.memberships.exclude(state="rejected")],
        "milestones": [{"year": m.year, "kind": m.kind, "title": m.title, "source_url": m.source_url}
                       for m in p.milestones.all()],
        "sources": [{"title": s.title, "url": s.url, "kind": s.kind} for s in p.sources.all()],
        "videos": [{"url": v.url, "title": v.title} for v in p.videos.all()],
        "awards": [{"badge_id": a.badge_id, "year": a.year, "year_awarded": a.year, "title": a.title, "citation": a.citation}
                   for a in p.awards.all()],
        "status": p.status, "verification": p.verification, "verification_note": p.verification_note,
        "is_featured": p.is_featured,
    }


def serialize_company(c: Company) -> dict:
    return {
        "id": c.pk,
        "legal_name": c.legal_name, "brand_name": c.brand_name, "tax_code": c.tax_code or "",
        "founded_year": c.founded_year, "province": c.province_id, "address": c.address, "size_band": c.size_band,
        "website": c.website, "primary_sector": c.primary_sector_id,
        "sectors": sorted(c.sectors.values_list("pk", flat=True)),
        "logo": c.logo.name if c.logo else "", "cover": c.cover.name if c.cover else "",
        "sections": {s.key: s.body_md for s in c.sections.all()},
        "leaders": [{"person_id": l.person_id, "person_name": l.person.full_name, "role": l.role, "title": l.title,
                     "start_year": l.start_year, "is_primary": l.is_primary}
                    for l in c.person_links.select_related("person")],
        "products": [{"name": p.name, "description": p.description} for p in c.products.all()],
        "milestones": [{"year": m.year, "kind": m.kind, "title": m.title, "source_url": m.source_url}
                       for m in c.milestones.all()],
        "sources": [{"title": s.title, "url": s.url, "kind": s.kind} for s in c.sources.all()],
        "videos": [{"url": v.url, "title": v.title} for v in c.videos.all()],
        "awards": [{"badge_id": a.badge_id, "year": a.year, "year_awarded": a.year, "title": a.title, "citation": a.citation}
                   for a in c.awards.all()],
        "status": c.status, "verification": c.verification, "verification_note": c.verification_note,
        "is_featured": c.is_featured,
    }


def serialize(entity):
    return serialize_person(entity) if isinstance(entity, Person) else serialize_company(entity)


def display_title(entity_type, data):
    if entity_type == "person":
        return data.get("full_name") or "(chưa có tên)"
    return data.get("brand_name") or data.get("legal_name") or "(chưa có tên)"


# --------------------------------------------------------------------------- gợi ý tự động (theo quy tắc)
def compute_checks(entity_type, data, instance=None):
    """
    Kiểm tra tự động theo quy tắc — KHÔNG dùng AI. Mỗi mục: {"level": ok|warn|info, "text": ..., "url": ...}.
    Biên tập viên xem các gợi ý này trước khi duyệt.
    """
    checks = []
    exclude_pk = instance.pk if instance else None
    if entity_type == "person":
        key = normalize(data.get("full_name", ""))
        if key:
            dupes = [p for p in Person.objects.filter(search_text__contains=key).exclude(pk=exclude_pk)[:10]
                     if normalize(p.full_name) == key]
            for p in dupes:
                checks.append({"level": "warn", "text": f"Đã có hồ sơ trùng tên: {p.full_name} – {p.headline}",
                               "url": p.get_absolute_url()})
        new_companies = [f"{c['company_name']}{' (MST ' + c['tax_code'] + ')' if c.get('tax_code') else ''}"
                         for c in data.get("companies", []) if not c.get("company_id") and c.get("company_name")]
        if new_companies:
            checks.append({"level": "info", "text": "Doanh nghiệp chưa có trong hệ thống, sẽ được tạo ở trạng thái "
                                                    "bản nháp: " + ", ".join(new_companies)})
        if not data.get("companies"):
            checks.append({"level": "warn", "text": "Chưa gắn doanh nghiệp nào."})
        main, main_label, minimum = "journey", "Hành trình khởi nghiệp", 500
    else:
        tax = data.get("tax_code")
        if tax:
            other = Company.objects.filter(tax_code=tax).exclude(pk=exclude_pk).first()
            if other:
                checks.append({"level": "warn", "text": f"Mã số thuế {tax} đã thuộc về {other.display_name}.",
                               "url": other.get_absolute_url()})
            else:
                checks.append({"level": "ok", "text": f"Mã số thuế {tax} đúng định dạng và chưa bị trùng. "
                                                      "Nhớ đối chiếu trên Cổng thông tin quốc gia về đăng ký doanh nghiệp."})
        else:
            checks.append({"level": "warn", "text": "Chưa có mã số thuế — khó xác minh doanh nghiệp."})
        key = normalize(data.get("brand_name") or data.get("legal_name") or "")
        if key:
            for c in Company.objects.filter(search_text__contains=key).exclude(pk=exclude_pk)[:5]:
                if normalize(c.display_name) == key or normalize(c.legal_name) == key:
                    checks.append({"level": "warn", "text": f"Đã có doanh nghiệp trùng tên: {c.legal_name}",
                                   "url": c.get_absolute_url()})
        new_people = [l["person_name"] for l in data.get("leaders", []) if not l.get("person_id")]
        if new_people:
            checks.append({"level": "info", "text": "Người điều hành chưa có hồ sơ, sẽ được tạo ở trạng thái "
                                                    "bản nháp: " + ", ".join(new_people)})
        if not data.get("primary_sector"):
            checks.append({"level": "warn", "text": "Chưa chọn ngành chính."})
        main, main_label, minimum = "history", "Lịch sử hình thành & phát triển", 400

    sections = data.get("sections", {})
    words = word_count(sections.get(main, ""))
    if words < minimum:
        checks.append({"level": "warn", "text": f"Bài viết “{main_label}” mới có {words} từ (khuyến nghị từ {minimum} từ)."})
    else:
        checks.append({"level": "ok", "text": f"Bài viết “{main_label}” có {words} từ."})
    summary_key = "summary" if entity_type == "person" else "overview"
    if not sections.get(summary_key):
        checks.append({"level": "warn", "text": "Thiếu đoạn tóm tắt / giới thiệu chung."})
    if len(data.get("milestones", [])) < 3:
        checks.append({"level": "warn", "text": "Nên có ít nhất 3 dấu mốc để dựng dòng thời gian."})
    source_count = len(data.get("sources", []))
    if source_count == 0:
        checks.append({"level": "warn", "text": "Chưa có nguồn tham khảo nào."})
    elif source_count < 2:
        checks.append({"level": "info", "text": "Mới có 1 nguồn tham khảo — nên có từ 2 nguồn."})
    import re

    cited = {int(n) for body in sections.values() for n in re.findall(r"\[\^(\d{1,3})\]", body)}
    missing = sorted(n for n in cited if n > source_count)
    if missing:
        checks.append({"level": "warn", "text": "Chú thích trỏ tới nguồn chưa có: " + ", ".join(f"[{n}]" for n in missing)})
    for v in data.get("videos", []):
        info = video_lib.parse_video_url(v["url"])
        if not info or not info.embed_url:
            checks.append({"level": "info", "text": f"Link video không nhúng được, sẽ chỉ hiện nút mở link gốc: {v['url']}"})
    return checks


# --------------------------------------------------------------------------- so sánh
def _word_diff(old, new):
    a, b = (old or "").split(), (new or "").split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            chunk = a[i1:i2]
            out.append(escape(" ".join(chunk if len(chunk) < 40 else chunk[:15] + ["…"] + chunk[-15:])))
        if op in ("delete", "replace"):
            out.append(f"<del>{escape(' '.join(a[i1:i2]))}</del>")
        if op in ("insert", "replace"):
            out.append(f"<ins>{escape(' '.join(b[j1:j2]))}</ins>")
    return mark_safe(" ".join(out))


def _label_value(field, value):
    if value in (None, "", []):
        return "—"
    if field == "phone":
        from apps.common.text import mask_phone
        return mask_phone(value)
    if field in ("hometown", "current_province", "province"):
        return Province.objects.filter(pk=value).values_list("name", flat=True).first() or value
    if field == "primary_sector":
        return Sector.objects.filter(pk=value).values_list("name", flat=True).first() or value
    if field == "sectors":
        return ", ".join(Sector.objects.filter(pk__in=value).values_list("name", flat=True))
    if field == "size_band":
        return dict(Company.Size.choices).get(value, value)
    if isinstance(value, bool):
        return "Có" if value else "Không"
    return value


def _list_lines(key, items):
    if key == "companies":
        return [f"{c['company_name']}{' (MST ' + c['tax_code'] + ')' if c.get('tax_code') else ''} · {dict(PersonCompany.Role.choices).get(c['role'], c['role'])}"
                f"{' · ' + c['title'] if c.get('title') else ''}{' (chính)' if c.get('is_primary') else ''}" for c in items]
    if key == "leaders":
        return [f"{l['person_name']} · {l.get('title') or dict(PersonCompany.Role.choices).get(l['role'], '')}" for l in items]
    if key == "memberships":
        names = dict(Association.objects.filter(pk__in=[m["association_id"] for m in items]).values_list("pk", "name"))
        return [f"{names.get(m['association_id'], m['association_id'])} · {m['position']}" for m in items]
    if key == "milestones":
        return [f"{m['year']} — {m['title']}" for m in items]
    if key == "sources":
        return [f"[{i}] {s['title']}" for i, s in enumerate(items, 1)]
    if key == "products":
        return [f"{p['name']}: {p['description']}" for p in items]
    if key == "videos":
        return [v.get("title") or v["url"] for v in items]
    if key == "awards":
        from apps.directory.models import AwardBadge
        badges = dict(AwardBadge.objects.filter(pk__in=[a["badge_id"] for a in items if a.get("badge_id")]).values_list("pk", "name"))
        return [f"{badges.get(a['badge_id'], 'Giải thưởng')}{' (' + str(a['year']) + ')' if a.get('year') else ''}{' · ' + a['title'] if a.get('title') else ''}" for a in items]
    return [str(i) for i in items]


LIST_LABELS = {"companies": "Doanh nghiệp", "leaders": "Người điều hành", "memberships": "Hiệp hội",
               "milestones": "Dấu mốc", "sources": "Nguồn tham khảo", "products": "Sản phẩm & dịch vụ",
               "videos": "Video", "awards": "Danh hiệu & Giải thưởng"}


def diff_payload(entity_type, old, new):
    """Danh sách thay đổi để hiển thị khi duyệt. old rỗng = hồ sơ mới."""
    from apps.directory.models import SECTION_LABELS

    rows = []
    fields = (PERSON_FIELDS if entity_type == "person" else COMPANY_FIELDS) + STAFF_FIELDS
    for field, label in fields:
        if field not in new:
            continue
        a, b = old.get(field), new.get(field)
        if (a or None) != (b or None):
            rows.append({"label": label, "kind": "field", "old": _label_value(field, a), "new": _label_value(field, b)})
    for field in IMAGE_FIELDS[entity_type]:
        if (old.get(field) or "") != (new.get(field) or ""):
            rows.append({"label": {"portrait": "Ảnh chân dung", "logo": "Logo", "cover": "Ảnh bìa"}[field],
                         "kind": "image", "old": old.get(field), "new": new.get(field)})
    old_sections, new_sections = old.get("sections", {}), new.get("sections", {})
    for key in dict.fromkeys([*new_sections, *old_sections]):
        a, b = old_sections.get(key, ""), new_sections.get(key, "")
        if a != b:
            rows.append({"label": SECTION_LABELS.get(key, key), "kind": "text",
                         "html": _word_diff(a, b), "words": word_count(b), "is_new": not a})
    for key in LIST_LABELS:
        if key not in new and key not in old:
            continue
        a, b = _list_lines(key, old.get(key, [])), _list_lines(key, new.get(key, []))
        if a != b:
            rows.append({"label": LIST_LABELS[key], "kind": "list",
                         "removed": [x for x in a if x not in b], "added": [x for x in b if x not in a]})
    return rows


# --------------------------------------------------------------------------- tạo bản sửa đổi & duyệt
def submit_revision(*, entity_type, data, author, instance=None, note="", as_draft=False, request=None):
    """Thành viên gửi bản sửa đổi (chờ duyệt). Biên tập viên dùng save_by_staff()."""
    role = "owner" if instance is not None and instance.owner_id == author.pk else "member"
    rev = Revision.objects.create(
        entity_type=entity_type,
        kind=Revision.Kind.UPDATE if instance else Revision.Kind.CREATE,
        person=instance if entity_type == "person" else None,
        company=instance if entity_type == "company" else None,
        title=display_title(entity_type, data), data=data,
        previous_data=serialize(instance) if instance else {},
        checks=compute_checks(entity_type, data, instance), note=note,
        state=Revision.State.DRAFT if as_draft else Revision.State.PENDING,
        author=author, author_role=role,
    )
    log(author, "revision.save_draft" if as_draft else "revision.submit", rev, rev.title, request=request)
    return rev


def update_revision(rev, data, note="", as_draft=False, request=None):
    rev.data = data
    rev.title = display_title(rev.entity_type, data)
    rev.checks = compute_checks(rev.entity_type, data, rev.target)
    rev.note = note
    rev.state = Revision.State.DRAFT if as_draft else Revision.State.PENDING
    rev.save()
    log(rev.author, "revision.resubmit" if not as_draft else "revision.save_draft", rev, rev.title, request=request)
    return rev


def save_by_staff(*, entity_type, data, editor, instance=None, note="", request=None):
    """Biên tập viên sửa trực tiếp: tạo bản sửa đổi và duyệt ngay (vẫn lưu lịch sử)."""
    rev = Revision.objects.create(
        entity_type=entity_type, kind=Revision.Kind.UPDATE if instance else Revision.Kind.CREATE,
        person=instance if entity_type == "person" else None,
        company=instance if entity_type == "company" else None,
        title=display_title(entity_type, data), data=data, previous_data=serialize(instance) if instance else {},
        checks=compute_checks(entity_type, data, instance), note=note or "Ban biên tập cập nhật",
        state=Revision.State.PENDING, author=editor, author_role="editor",
    )
    return approve(rev, editor, note="", request=request, silent=True)


@transaction.atomic
def approve(rev, reviewer, note="", request=None, silent=False):
    rev = Revision.objects.select_for_update().get(pk=rev.pk)
    if rev.state not in (Revision.State.PENDING, Revision.State.NEEDS_INFO):
        raise ValueError("Bản sửa đổi này không còn chờ duyệt.")
    staff = reviewer.is_editor
    if rev.entity_type == "person":
        entity = _apply_person(rev.person, rev.data, rev, staff)
        rev.person = entity
        count = Revision.objects.filter(person=entity, state=Revision.State.APPROVED).count()
    else:
        entity = _apply_company(rev.company, rev.data, rev, staff)
        rev.company = entity
        count = Revision.objects.filter(company=entity, state=Revision.State.APPROVED).count()
    rev.state = Revision.State.APPROVED
    rev.revision_no = count + 1
    rev.reviewer = reviewer
    rev.reviewed_at = timezone.now()
    rev.review_note = note
    rev.save()
    log(reviewer, "revision.approve", rev, rev.title, {"entity": rev.entity_type, "id": entity.pk}, request=request)
    if not silent and rev.author and rev.author != reviewer:
        from apps.common.notify import send

        send(rev.author.email, f"Đã duyệt: {rev.title}", "revision_approved",
             {"revision": rev, "entity": entity, "note": note})
    return rev


def reject(rev, reviewer, note, needs_info=False, request=None):
    if rev.state not in (Revision.State.PENDING, Revision.State.NEEDS_INFO):
        raise ValueError("Bản sửa đổi này không còn chờ duyệt.")
    rev.state = Revision.State.NEEDS_INFO if needs_info else Revision.State.REJECTED
    rev.reviewer = reviewer
    rev.reviewed_at = timezone.now()
    rev.review_note = note
    rev.save()
    log(reviewer, "revision.needs_info" if needs_info else "revision.reject", rev, rev.title,
        {"note": note}, request=request)
    if rev.author:
        from apps.common.notify import send

        send(rev.author.email, ("Cần bổ sung: " if needs_info else "Chưa được duyệt: ") + rev.title,
             "revision_needs_info" if needs_info else "revision_rejected", {"revision": rev, "note": note})
    return rev


# --------------------------------------------------------------------------- ghi payload vào bảng chính
def _set_children(entity, field, data):
    kw = {field: entity}
    ArticleSection.objects.filter(**kw).delete()
    sections_def = PERSON_SECTIONS if field == "person" else COMPANY_SECTIONS
    order = {k: i for i, (k, _l, _h) in enumerate(sections_def)}
    for key, body in data.get("sections", {}).items():
        if key in order and body.strip():
            ArticleSection.objects.create(key=key, body_md=body, word_count=word_count(body), sort_order=order[key], **kw)
    Milestone.objects.filter(**kw).delete()
    for m in data.get("milestones", []):
        Milestone.objects.create(year=m["year"], kind=m.get("kind") or "other", title=m["title"],
                                 source_url=m.get("source_url", ""), **kw)
    Source.objects.filter(**kw).delete()
    for i, s in enumerate(data.get("sources", []), 1):
        Source.objects.create(number=i, title=s["title"], url=s.get("url", ""), kind=s.get("kind") or "press", **kw)


def _attach_videos(entity, related_name, items):
    from django.db import IntegrityError

    keep = []
    for item in items:
        video = Video.objects.filter(url=item["url"]).first()
        if video is None:
            title = item.get("title") or ""
            meta = {}
            info = video_lib.parse_video_url(item["url"])
            if info:
                meta, _status = video_lib.fetch_oembed(item["url"], info.platform)
            try:
                with transaction.atomic():
                    video = Video.objects.create(
                        url=item["url"], title=(title or meta.get("title") or "Video")[:300],
                        channel_name=meta.get("channel_name", ""),
                        thumbnail_url=(meta.get("thumbnail_url") or "")[:500],
                        duration_seconds=meta.get("duration_seconds"),
                        availability="ok" if meta else "unknown",
                        kind=Video.Kind.INTERVIEW if related_name == "persons" else Video.Kind.COMPANY,
                    )
            except IntegrityError:
                video = Video.objects.get(url=item["url"])
        keep.append(video)
    getattr(entity, "videos").set(keep)


def _apply_images(entity, data, entity_type):
    for field in IMAGE_FIELDS[entity_type]:
        path = data.get(field, "")
        current = getattr(entity, field).name if getattr(entity, field) else ""
        if path != current:
            new_name = promote_upload(path, field) if path else ""
            setattr(entity, field, new_name or None)
            data[field] = new_name


def _apply_person(person, data, rev, staff):
    creating = person is None
    person = person or Person()
    for field in ("full_name", "headline", "email_public", "website", "show_birth_year", "show_hometown", "show_email"):
        if field in data:
            setattr(person, field, data[field])
    if "phone" in data and "*" not in data["phone"]:
        person.phone = data["phone"]
    person.birth_year = data.get("birth_year")
    person.hometown_id = data.get("hometown")
    person.current_province_id = data.get("current_province")
    if staff and "status" in data:
        person.status = data["status"]
        person.verification = data.get("verification", person.verification)
        person.verification_note = data.get("verification_note", "")
        person.is_featured = data.get("is_featured", False)
        if person.verification != "none" and not person.verified_at:
            person.verified_at = timezone.localdate()
    elif creating:
        person.status = Status.PUBLISHED
    if creating and rev.author and rev.author_role != "editor" and _is_self_submission(rev):
        person.owner = rev.author
    _apply_images(person, data, "person")
    if person.status == Status.PUBLISHED and not person.published_at:
        person.published_at = timezone.now()
    person.save()
    _set_children(person, "person", data)

    PersonCompany.objects.filter(person=person).delete()
    for c in data.get("companies", []):
        company = Company.objects.filter(pk=c.get("company_id")).first() if c.get("company_id") else None
        tax = (c.get("tax_code") or "").strip()
        if company is None and tax and TAX_CODE_RE.match(tax):
            company = Company.objects.filter(tax_code=tax).first()
        if company is None and c.get("company_name"):
            company = find_company(c["company_name"])
        if company is None and c.get("company_name"):
            create_kwargs = {"legal_name": c["company_name"], "status": Status.DRAFT}
            if tax and TAX_CODE_RE.match(tax) and not Company.objects.filter(tax_code=tax).exists():
                create_kwargs["tax_code"] = tax
            company = Company.objects.create(**create_kwargs)
        elif company and tax and not company.tax_code and TAX_CODE_RE.match(tax) and not Company.objects.filter(tax_code=tax).exclude(pk=company.pk).exists():
            company.tax_code = tax
            company.save(update_fields=["tax_code", "search_text"])
        if company:
            PersonCompany.objects.get_or_create(
                person=person, company=company, role=c.get("role") or "founder_ceo",
                defaults={"title": c.get("title", ""), "start_year": c.get("start_year"),
                          "end_year": c.get("end_year"), "is_primary": c.get("is_primary", False)})

    wanted = {m["association_id"]: m for m in data.get("memberships", [])}
    for existing in Membership.objects.filter(person=person):
        if existing.association_id not in wanted:
            existing.delete()
    for assoc_id, m in wanted.items():
        if not Association.objects.filter(pk=assoc_id).exists():
            continue
        obj, created = Membership.objects.get_or_create(
            person=person, association_id=assoc_id,
            defaults={"position": m["position"], "start_year": m.get("start_year"),
                      "state": Membership.State.CONFIRMED if rev.author_role == "editor" else Membership.State.PENDING})
        if not created:
            obj.position, obj.start_year = m["position"], m.get("start_year")
            obj.save()
    if staff and "awards" in data:
        from apps.directory.models import AwardBadge, PersonAward
        PersonAward.objects.filter(person=person).delete()
        for a in data["awards"]:
            bid = a.get("badge_id")
            if bid and AwardBadge.objects.filter(pk=bid).exists():
                PersonAward.objects.create(
                    person=person,
                    badge_id=bid,
                    year=a.get("year") or a.get("year_awarded"),
                    title=a.get("title", ""),
                    citation=a.get("citation", ""),
                )
    _attach_videos(person, "persons", data.get("videos", []))
    person.save()  # cập nhật search_text với tên doanh nghiệp
    return person


def _is_self_submission(rev):
    app = getattr(rev.author, "application", None)
    return bool(app and app.applicant_type == "entrepreneur"
                and normalize(rev.author.full_name) == normalize(rev.data.get("full_name", "")))


def _apply_company(company, data, rev, staff):
    creating = company is None
    company = company or Company()
    for field in ("legal_name", "brand_name", "address", "size_band", "website"):
        if field in data:
            setattr(company, field, data[field])
    if creating:
        company.tax_code = data.get("tax_code") or None
    elif not company.tax_code and data.get("tax_code"):
        company.tax_code = data.get("tax_code")
    # Nếu company đã có tax_code thì giữ nguyên, không thay đổi
    company.founded_year = data.get("founded_year")
    company.province_id = data.get("province")
    company.primary_sector_id = data.get("primary_sector")
    if staff and "status" in data:
        company.status = data["status"]
        company.verification = data.get("verification", company.verification)
        company.verification_note = data.get("verification_note", "")
        company.is_featured = data.get("is_featured", False)
        if company.verification != "none" and not company.verified_at:
            company.verified_at = timezone.localdate()
    elif creating or company.status == Status.DRAFT:
        company.status = Status.PUBLISHED
    if creating and rev.author and rev.author_role != "editor":
        app = getattr(rev.author, "application", None)
        if app and app.applicant_type == "company_rep":
            company.owner = rev.author
    _apply_images(company, data, "company")
    if company.status == Status.PUBLISHED and not company.published_at:
        company.published_at = timezone.now()
    company.save()
    sectors = set(data.get("sectors", []))
    if data.get("primary_sector"):
        sectors.add(data["primary_sector"])
    company.sectors.set(Sector.objects.filter(pk__in=sectors))
    _set_children(company, "company", data)

    CompanyProduct.objects.filter(company=company).delete()
    for i, p in enumerate(data.get("products", [])):
        CompanyProduct.objects.create(company=company, name=p["name"], description=p.get("description", ""), sort_order=i)

    PersonCompany.objects.filter(company=company).delete()
    for l in data.get("leaders", []):
        person = Person.objects.filter(pk=l.get("person_id")).first() if l.get("person_id") else None
        if person is None and l.get("person_name"):
            person = find_person(l["person_name"]) or Person.objects.create(full_name=l["person_name"], status=Status.DRAFT)
        if person:
            PersonCompany.objects.get_or_create(
                person=person, company=company, role=l.get("role") or "founder_ceo",
                defaults={"title": l.get("title", ""), "start_year": l.get("start_year"),
                          "is_primary": l.get("is_primary", False)})
            person.save()
    if staff and "awards" in data:
        from apps.directory.models import AwardBadge, CompanyAward
        CompanyAward.objects.filter(company=company).delete()
        for a in data["awards"]:
            bid = a.get("badge_id")
            if bid and AwardBadge.objects.filter(pk=bid).exists():
                CompanyAward.objects.create(
                    company=company,
                    badge_id=bid,
                    year=a.get("year") or a.get("year_awarded"),
                    title=a.get("title", ""),
                    citation=a.get("citation", ""),
                )
    _attach_videos(company, "companies", data.get("videos", []))
    return company
