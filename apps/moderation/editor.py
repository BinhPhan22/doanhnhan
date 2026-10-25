"""Ngữ cảnh dùng chung cho form nhập liệu doanh nhân / doanh nghiệp (thành viên và ban biên tập)."""
from apps.directory.models import (
    COMPANY_SECTIONS, PERSON_SECTIONS, Association, AwardBadge, Company, Milestone, PersonCompany, Province, Sector, Source,
    Status, Verification,
)

SECTION_HELP = {
    # 7 mục chuẩn mới cho doanh nhân
    "thong_tin_chung": ("50–100 từ: họ tên, năm sinh, quê quán, lĩnh vực, doanh nghiệp và vai trò hiện tại (bắt buộc).", 4),
    "khoi_dau": ("100–300 từ: bắt đầu từ đâu, vì sao chọn nghề/ngành này, vốn liếng đầu tiên là gì (bắt buộc).", 6),
    "kho_khan": ("100–300 từ: giai đoạn khó nhất, đã vượt qua bằng cách nào — viết thật, không tô hồng (nên có).", 6),
    "buoc_ngoat": ("100–300 từ: quyết định hoặc sự kiện làm thay đổi hướng đi (nên có).", 6),
    "bai_hoc": ("3–5 ý ngắn: bài học rút ra và lời khuyên cho người đi sau (nên có).", 5),
    "hien_tai": ("100–200 từ: đang làm gì, doanh nghiệp/dự án hiện tại, định hướng sắp tới (bắt buộc).", 5),
    "cau_gui_lai": ("Tối đa 200 ký tự: một câu kết, hiển thị nổi bật ở đầu hồ sơ (nên có).", 3),

    # Khung doanh nghiệp
    "overview": ("Doanh nghiệp làm gì, cho ai, điểm khác biệt.", 4),
    "history": ("Hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.", 12),
    "products": ("Các dòng sản phẩm, dịch vụ chính; công nghệ, tiêu chuẩn chất lượng áp dụng.", 5),
    "market": ("Khu vực hoạt động, nhóm khách hàng chính, đối tác tiêu biểu đã công khai.", 4),
    "culture": ("Giá trị cốt lõi, môi trường làm việc, hoạt động cộng đồng của doanh nghiệp.", 4),

    # Khóa cũ (giữ để tương thích dữ liệu cũ)
    "summary": ("Hiện ở đầu hồ sơ và trên thẻ tìm kiếm: là ai, làm gì, nổi bật vì điều gì.", 3),
    "biography": ("Xuất thân, quá trình học tập, bằng cấp, những người hoặc trải nghiệm ảnh hưởng.", 5),
    "journey": ("Phần quan trọng nhất: ý tưởng ban đầu, khó khăn, bước ngoặt, cách vượt qua, kết quả.", 14),
    "achievements": ("Giải thưởng, danh hiệu, con số có nguồn kiểm chứng.", 5),
    "philosophy": ("Quan điểm, giá trị cốt lõi, lời khuyên.", 5),
    "community": ("Hiệp hội, chức danh trong hội, thiện nguyện.", 4),
}
SECTION_HELP_COMPANY = {"achievements": ("Giải thưởng, chứng nhận ISO/HACCP… đã công bố, kèm nguồn.", 4)}

NEW_PERSON = {"show_birth_year": True, "show_hometown": True, "show_email": True, "status": Status.PUBLISHED,
              "verification": Verification.NONE}
NEW_COMPANY = {"status": Status.PUBLISHED, "verification": Verification.NONE, "sectors": []}


def sections_def(entity_type):
    out = []
    for key, label, hint in (PERSON_SECTIONS if entity_type == "person" else COMPANY_SECTIONS):
        help_text, rows = (SECTION_HELP_COMPANY.get(key) if entity_type == "company" else None) or SECTION_HELP[key]
        out.append({"key": key, "label": label, "hint": hint, "help": help_text, "rows": rows})
    return out


def editor_context(entity_type, data, errors=None, staff=False, note=""):
    ctx = {
        "entity_type": entity_type, "data": data, "errors": errors or {}, "staff": staff, "note": note,
        "blank_rows": [{}], "provinces": Province.objects.all(), "sections_def": sections_def(entity_type),
        "role_choices": PersonCompany.Role.choices, "milestone_kinds": Milestone.Kind.choices,
        "source_kinds": Source.Kind.choices, "status_choices": Status.choices,
        "verification_choices": Verification.choices,
        "available_badges": AwardBadge.objects.all().order_by("sort_order", "name"),
    }
    if entity_type == "person":
        ctx["associations"] = Association.objects.published().order_by("name")
    else:
        ctx["size_choices"] = Company.Size.choices
        ctx["sector_options"] = sector_options()
    return ctx


def sector_options():
    """Ngành cấp 1 kèm phân ngành ngay bên dưới, theo thứ tự hiển thị."""
    out = []
    for root in Sector.objects.filter(is_active=True, parent__isnull=True).prefetch_related("children"):
        out.append(root)
        out.extend(c for c in root.children.all() if c.is_active)
    return out
