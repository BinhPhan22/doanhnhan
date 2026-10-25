"""
Dữ liệu cốt lõi: tỉnh thành, ngành nghề, doanh nhân, doanh nghiệp, hiệp hội, sự kiện, video
và các liên kết hai chiều giữa chúng.
"""
import re

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from apps.common.text import normalize, unique_slug
from apps.common.validators import image_extensions, max_file_size, validate_tax_code, validate_year
from apps.common.video import PLATFORM_LABELS, format_duration, parse_video_url


class Status(models.TextChoices):
    DRAFT = "draft", "Bản nháp"
    PUBLISHED = "published", "Đã công bố"
    ARCHIVED = "archived", "Đã ẩn"


class Verification(models.TextChoices):
    NONE = "none", "Chưa xác minh"
    BASIC = "basic", "Đã kiểm tra cơ bản"
    VERIFIED = "verified", "Đã xác minh"
    ASSOCIATION = "association", "Hiệp hội xác nhận"


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Status.PUBLISHED)

    def search(self, q):
        q = normalize(q)
        if not q:
            return self
        cond = Q()
        for word in q.split(" "):
            cond &= Q(search_text__contains=word)
        return self.filter(cond)


class SluggedModel(models.Model):
    slug = models.SlugField("Đường dẫn", max_length=90, unique=True, blank=True)
    search_text = models.TextField(blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        abstract = True

    def slug_source(self):  # pragma: no cover - mỗi lớp con định nghĩa
        raise NotImplementedError

    def search_source(self):
        return self.slug_source()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(type(self), self.slug_source(), self.pk)
        self.search_text = normalize(self.search_source())
        super().save(*args, **kwargs)


# --------------------------------------------------------------------------- danh mục
class Province(models.Model):
    code = models.SlugField("Mã", max_length=40, unique=True)
    name = models.CharField("Tên", max_length=80)
    is_city = models.BooleanField("Thành phố", default=False)
    merged_from = models.CharField("Hợp nhất từ", max_length=200, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = verbose_name_plural = "tỉnh, thành phố"

    def __str__(self):
        return self.name


SECTOR_ICONS = {
    "tech": "M3 5h18v11H3z M8 20h8 M12 16v4",
    "factory": "M3 21V10l6 4V10l6 4V6h6v15z M2 21h20",
    "retail": "M5 8h14l-1 13H6z M9 8V6a3 3 0 0 1 6 0v2",
    "food": "M4 8h13v5a6 6 0 0 1-6 6h-1a6 6 0 0 1-6-6z M17 10h2a2 2 0 0 1 0 4h-2",
    "building": "M4 21V5l8-3v19 M12 9h8v12 M2 21h20 M7 8h2 M7 12h2 M7 16h2 M15 13h2 M15 17h2",
    "education": "M2 9l10-5 10 5-10 5z M6 11v5c3 2 9 2 12 0v-5",
    "agri": "M5 19C5 10 11 5 20 4c-1 9-6 15-15 15z M5 19l7-7",
    "logistics": "M2 6h12v10H2z M14 10h4l3 3v3h-7 M5 18a2 2 0 1 0 4 0a2 2 0 1 0-4 0 M15 18a2 2 0 1 0 4 0a2 2 0 1 0-4 0",
    "finance": "M3 10l9-6 9 6 M5 10v8 M9 10v8 M15 10v8 M19 10v8 M3 21h18",
    "health": "M12 21s-7-4.5-9-9a5 5 0 0 1 9-3 5 5 0 0 1 9 3c-2 4.5-9 9-9 9z",
    "creative": "M12 3a9 9 0 1 0 0 18c1 0 2-1 2-2s-1-1.5-1-2.5 1-1.5 2-1.5h2a4 4 0 0 0 4-4c0-4.4-4-8-9-8z",
    "travel": "M2 16l20-6-3-3-7 3-6-6-2 1 4 7-4 1-2-2-1 1z",
}


class Sector(SluggedModel):
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="children",
                               verbose_name="Ngành cấp trên")
    name = models.CharField("Tên ngành", max_length=120)
    description = models.TextField("Mô tả", blank=True)
    icon = models.CharField("Biểu tượng", max_length=20, choices=[(k, k) for k in SECTOR_ICONS], default="tech")
    vsic_code = models.CharField("Mã ngành VSIC 2025 (tham chiếu)", max_length=20, blank=True)
    sort_order = models.PositiveSmallIntegerField("Thứ tự", default=0)
    is_active = models.BooleanField("Đang dùng", default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = verbose_name_plural = "ngành nghề"

    def __str__(self):
        return f"{self.parent.name} › {self.name}" if self.parent_id else self.name

    def slug_source(self):
        return self.name

    def get_absolute_url(self):
        root = self.parent if self.parent_id else self
        url = reverse("public:sector_detail", args=[root.slug])
        return f"{url}?phan-nganh={self.slug}" if self.parent_id else url

    @property
    def icon_path(self):
        return SECTOR_ICONS.get(self.icon if not self.parent_id else self.parent.icon, SECTOR_ICONS["tech"])

    def family_ids(self):
        return [self.pk, *self.children.values_list("pk", flat=True)]


# --------------------------------------------------------------------------- doanh nhân
class Person(SluggedModel):
    full_name = models.CharField("Họ và tên", max_length=120)
    birth_year = models.PositiveSmallIntegerField("Năm sinh", null=True, blank=True, validators=[validate_year])
    hometown = models.ForeignKey(Province, null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
                                 verbose_name="Quê quán")
    current_province = models.ForeignKey(Province, null=True, blank=True, on_delete=models.SET_NULL,
                                         related_name="people", verbose_name="Nơi hoạt động chính")
    headline = models.CharField("Dòng chức danh", max_length=200, blank=True)
    portrait = models.ImageField("Ảnh chân dung", upload_to="portraits/%Y/", blank=True,
                                 validators=[image_extensions, max_file_size])
    email_public = models.EmailField("Email công khai", blank=True)
    phone = models.CharField("Số điện thoại (bảo mật)", max_length=30, blank=True)
    website = models.URLField("Website / LinkedIn", blank=True)
    show_birth_year = models.BooleanField("Công khai năm sinh", default=True)
    show_hometown = models.BooleanField("Công khai quê quán", default=True)
    show_email = models.BooleanField("Công khai email", default=True)
    status = models.CharField("Trạng thái", max_length=10, choices=Status.choices, default=Status.PUBLISHED)
    verification = models.CharField("Xác minh", max_length=12, choices=Verification.choices,
                                    default=Verification.NONE)
    verification_note = models.CharField("Ghi chú xác minh", max_length=255, blank=True)
    verified_at = models.DateField("Ngày xác minh", null=True, blank=True)
    is_featured = models.BooleanField("Nổi bật", default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                              related_name="owned_people", verbose_name="Chính chủ")
    published_at = models.DateTimeField(null=True, blank=True)
    is_demo = models.BooleanField("Dữ liệu mẫu", default=False)
    views_count = models.PositiveIntegerField("Lượt xem", default=0)
    likes_count = models.PositiveIntegerField("Lượt thích / tim", default=0)

    class Meta:
        ordering = ["full_name"]
        verbose_name = verbose_name_plural = "doanh nhân"

    def __str__(self):
        return self.full_name

    def slug_source(self):
        return self.full_name

    def search_source(self):
        companies = " ".join(pc.company.display_name for pc in self.company_links.select_related("company")) if self.pk else ""
        return f"{self.full_name} {self.headline} {companies}"

    def get_absolute_url(self):
        return reverse("public:person_detail", args=[self.slug])

    @property
    def initials(self):
        name = re.sub(r"\(.*?\)", "", self.full_name)
        parts = [p for p in name.split() if p]
        return (parts[-1][0] if parts else "?").upper()

    @property
    def display_phone(self):
        return self.phone or (self.owner.phone if self.owner else "")

    @property
    def masked_phone(self):
        from apps.common.text import mask_phone
        return mask_phone(self.display_phone)

    @property
    def primary_link(self):
        links = list(self.company_links.all())
        return next((l for l in links if l.is_primary), links[0] if links else None)

    @property
    def primary_badge(self):
        return self.awards.select_related("badge").first()

    def sectors(self):
        return Sector.objects.filter(companies__person_links__person=self).distinct()

    def section(self, key):
        return next((s for s in self.sections.all() if s.key == key), None)

    @property
    def cau_gui_lai(self):
        sec = self.section("cau_gui_lai")
        return sec.body_md.strip() if sec and sec.body_md else ""

    def completeness(self):
        """Phần trăm đầy đủ và danh sách mục còn thiếu (dùng cho khung Độ đầy đủ theo khung 7 mục)."""
        sections = {s.key: s for s in self.sections.all()}
        checks = [
            ("Thông tin chung", bool(sections.get("thong_tin_chung") or sections.get("summary"))),
            ("Khởi đầu", bool(sections.get("khoi_dau") or sections.get("biography"))),
            ("Hiện tại", bool(sections.get("hien_tai"))),
            ("Khó khăn / Bước ngoặt", bool(sections.get("kho_khan") or sections.get("buoc_ngoat") or sections.get("journey"))),
            ("Một câu gửi lại", bool(sections.get("cau_gui_lai"))),
            ("Ít nhất 3 dấu mốc", self.milestones.count() >= 3),
            ("Ảnh chân dung", bool(self.portrait)),
            ("Doanh nghiệp", self.company_links.exists()),
            ("Ít nhất 2 nguồn tham khảo", self.sources.count() >= 2),
        ]
        done = sum(1 for _, ok in checks if ok)
        return round(done * 100 / len(checks)), checks


class Company(SluggedModel):
    class Size(models.TextChoices):
        LT10 = "lt10", "Dưới 10 người"
        S10_50 = "10_50", "10 – 50 người"
        S50_200 = "50_200", "50 – 200 người"
        GT200 = "gt200", "Trên 200 người"

    legal_name = models.CharField("Tên theo đăng ký kinh doanh", max_length=255)
    brand_name = models.CharField("Tên thương hiệu", max_length=120, blank=True)
    tax_code = models.CharField("Mã số thuế", max_length=14, unique=True, null=True, blank=True,
                                validators=[validate_tax_code])
    founded_year = models.PositiveSmallIntegerField("Năm thành lập", null=True, blank=True, validators=[validate_year])
    province = models.ForeignKey(Province, null=True, blank=True, on_delete=models.SET_NULL, related_name="companies",
                                 verbose_name="Trụ sở")
    address = models.CharField("Địa chỉ", max_length=255, blank=True)
    size_band = models.CharField("Quy mô nhân sự", max_length=10, choices=Size.choices, blank=True)
    website = models.URLField("Website", blank=True)
    logo = models.ImageField("Logo", upload_to="logos/%Y/", blank=True, validators=[image_extensions, max_file_size])
    cover = models.ImageField("Ảnh trụ sở / sản phẩm", upload_to="company-covers/%Y/", blank=True,
                              validators=[image_extensions, max_file_size])
    primary_sector = models.ForeignKey(Sector, null=True, blank=True, on_delete=models.SET_NULL,
                                       related_name="primary_companies", verbose_name="Ngành chính")
    sectors = models.ManyToManyField(Sector, blank=True, related_name="companies", verbose_name="Ngành, phân ngành")
    status = models.CharField("Trạng thái", max_length=10, choices=Status.choices, default=Status.PUBLISHED)
    verification = models.CharField("Xác minh", max_length=12, choices=Verification.choices,
                                    default=Verification.NONE)
    verification_note = models.CharField("Ghi chú xác minh", max_length=255, blank=True)
    verified_at = models.DateField("Ngày xác minh", null=True, blank=True)
    is_featured = models.BooleanField("Nổi bật", default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                              related_name="owned_companies", verbose_name="Người quản lý")
    published_at = models.DateTimeField(null=True, blank=True)
    is_demo = models.BooleanField("Dữ liệu mẫu", default=False)

    class Meta:
        ordering = ["legal_name"]
        verbose_name = verbose_name_plural = "doanh nghiệp"

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.brand_name or self.legal_name

    @property
    def initials(self):
        return (self.display_name[:1] or "?").upper()

    def slug_source(self):
        return self.display_name

    def search_source(self):
        return f"{self.legal_name} {self.brand_name} {self.tax_code or ''}"

    def get_absolute_url(self):
        return reverse("public:company_detail", args=[self.slug])

    def section(self, key):
        return next((s for s in self.sections.all() if s.key == key), None)

    @property
    def primary_badge(self):
        return self.awards.select_related("badge").first()


class PersonCompany(models.Model):
    class Role(models.TextChoices):
        FOUNDER_CEO = "founder_ceo", "Nhà sáng lập & CEO"
        FOUNDER = "founder", "Nhà sáng lập"
        COFOUNDER = "cofounder", "Đồng sáng lập"
        CEO = "ceo", "Tổng giám đốc / CEO"
        EXECUTIVE = "executive", "Điều hành"
        SHAREHOLDER = "shareholder", "Cổ đông"

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="company_links")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="person_links")
    role = models.CharField("Vai trò", max_length=12, choices=Role.choices, default=Role.FOUNDER_CEO)
    title = models.CharField("Chức danh", max_length=120, blank=True)
    start_year = models.PositiveSmallIntegerField("Từ năm", null=True, blank=True, validators=[validate_year])
    end_year = models.PositiveSmallIntegerField("Đến năm", null=True, blank=True, validators=[validate_year])
    is_primary = models.BooleanField("Doanh nghiệp chính", default=False)

    class Meta:
        unique_together = [("person", "company", "role")]
        ordering = ["-is_primary", "start_year"]

    @property
    def label(self):
        return self.title or self.get_role_display()


# --------------------------------------------------------------------------- nội dung bài viết
PERSON_SECTIONS = [
    ("thong_tin_chung", "Thông tin chung", "50–100 từ: họ tên, năm sinh, quê quán, lĩnh vực, doanh nghiệp và vai trò hiện tại"),
    ("khoi_dau", "Khởi đầu", "100–300 từ: bắt đầu từ đâu, vì sao chọn nghề/ngành này, vốn liếng đầu tiên là gì"),
    ("kho_khan", "Khó khăn lớn nhất", "100–300 từ: giai đoạn khó nhất, đã vượt qua bằng cách nào — viết thật, không tô hồng"),
    ("buoc_ngoat", "Bước ngoặt", "100–300 từ: quyết định hoặc sự kiện làm thay đổi hướng đi"),
    ("bai_hoc", "Bài học", "3–5 ý ngắn: bài học rút ra và lời khuyên cho người đi sau"),
    ("hien_tai", "Hiện tại", "100–200 từ: đang làm gì, doanh nghiệp/dự án hiện tại, định hướng sắp tới"),
    ("cau_gui_lai", "Một câu gửi lại", "Tối đa 200 ký tự: một câu kết, hiển thị nổi bật ở đầu hồ sơ"),
]
COMPANY_SECTIONS = [
    ("overview", "Giới thiệu chung", "80–150 từ"),
    ("history", "Lịch sử hình thành & phát triển", "bài viết chính, từ 400 từ"),
    ("products", "Sản phẩm & dịch vụ", "100–300 từ"),
    ("market", "Thị trường & khách hàng", "tùy chọn"),
    ("achievements", "Thành tựu & chứng nhận", "tùy chọn"),
    ("culture", "Văn hóa & trách nhiệm xã hội", "tùy chọn"),
]
OLD_PERSON_SECTIONS = [
    ("summary", "Tóm tắt"),
    ("biography", "Tiểu sử & học vấn"),
    ("journey", "Hành trình khởi nghiệp & sự nghiệp"),
    ("achievements", "Thành tựu & giải thưởng"),
    ("philosophy", "Triết lý kinh doanh & chia sẻ"),
    ("community", "Hoạt động cộng đồng"),
]
SECTION_LABELS = {
    **{k: label for k, label in OLD_PERSON_SECTIONS},
    **{k: label for k, label, _ in PERSON_SECTIONS + COMPANY_SECTIONS},
}


class ArticleSection(models.Model):
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.CASCADE, related_name="sections")
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name="sections")
    key = models.CharField(max_length=20)
    body_md = models.TextField()
    word_count = models.PositiveIntegerField(default=0)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]
        constraints = [
            models.UniqueConstraint(fields=["person", "key"], name="uniq_person_section"),
            models.UniqueConstraint(fields=["company", "key"], name="uniq_company_section"),
        ]

    @property
    def label(self):
        return SECTION_LABELS.get(self.key, self.key)


class Milestone(models.Model):
    class Kind(models.TextChoices):
        FOUNDING = "founding", "Thành lập"
        FUNDING = "funding", "Gọi vốn"
        PRODUCT = "product", "Ra mắt sản phẩm"
        AWARD = "award", "Giải thưởng"
        POSITION = "position", "Chức vụ"
        COMMUNITY = "community", "Cộng đồng"
        OTHER = "other", "Khác"

    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.CASCADE, related_name="milestones")
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name="milestones")
    year = models.PositiveSmallIntegerField("Năm", validators=[validate_year])
    kind = models.CharField("Loại", max_length=12, choices=Kind.choices, default=Kind.OTHER)
    title = models.CharField("Nội dung", max_length=255)
    source_url = models.URLField("Nguồn", blank=True)
    event = models.ForeignKey("Event", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        ordering = ["year", "id"]


class Source(models.Model):
    class Kind(models.TextChoices):
        PRESS = "press", "Báo chí"
        REGISTRY = "registry", "Đăng ký kinh doanh"
        DECISION = "decision", "Quyết định, giấy khen"
        ASSOCIATION = "association", "Xác nhận hiệp hội"
        SELF = "self", "Tự khai"

    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.CASCADE, related_name="sources")
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name="sources")
    number = models.PositiveSmallIntegerField(default=1)
    title = models.CharField("Tiêu đề nguồn", max_length=300)
    url = models.URLField("Link", blank=True)
    kind = models.CharField("Loại", max_length=12, choices=Kind.choices, default=Kind.PRESS)

    class Meta:
        ordering = ["number"]


class CompanyProduct(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="products")
    name = models.CharField("Sản phẩm / dịch vụ", max_length=150)
    description = models.CharField("Mô tả ngắn", max_length=300, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]


class MediaImage(models.Model):
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.CASCADE, related_name="images")
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="gallery/%Y/", validators=[image_extensions, max_file_size])
    caption = models.CharField("Chú thích", max_length=255, blank=True)
    credit = models.CharField("Nguồn ảnh", max_length=150, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]


# --------------------------------------------------------------------------- giải thưởng & huy hiệu danh dự
class AwardBadge(models.Model):
    class BadgeType(models.TextChoices):
        SAO_DO = "sao_do", "Giải thưởng Sao Đỏ"
        SAO_VANG = "sao_vang", "Giải thưởng Sao Vàng Đất Việt"
        KHOI_NGHIEP = "khoi_nghiep", "Doanh nhân trẻ Khởi nghiệp xuất sắc"
        TIEU_BIEU = "tieu_bieu", "Doanh nhân tiêu biểu"
        DN_TIEU_BIEU = "dn_tieu_bieu", "Doanh nghiệp tiêu biểu / TOP VNR"
        HUAN_CHUONG = "huan_chuong", "Huân chương / Bằng khen Nhà nước"
        OTHER = "other", "Giải thưởng khác"

    code = models.SlugField("Mã định danh", max_length=50, unique=True)
    name = models.CharField("Tên giải thưởng / huy hiệu", max_length=150)
    badge_type = models.CharField("Phân loại", max_length=20, choices=BadgeType.choices, default=BadgeType.SAO_DO)
    issuer = models.CharField("Đơn vị trao tặng", max_length=200, default="Trung ương Hội Doanh nhân trẻ Việt Nam")
    icon = models.CharField("Biểu tượng", max_length=30, default="star", help_text="star, medal, award, trophy")
    color = models.CharField("Màu sắc nhãn", max_length=30, default="gold", help_text="gold, red, blue, green")
    description = models.TextField("Mô tả giải thưởng", blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "nhãn giải thưởng"
        verbose_name_plural = "nhãn giải thưởng"

    def __str__(self):
        return self.name


class PersonAward(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="awards", verbose_name="Doanh nhân")
    badge = models.ForeignKey(AwardBadge, on_delete=models.CASCADE, related_name="awardees", verbose_name="Giải thưởng")
    year = models.PositiveSmallIntegerField("Năm vinh danh", null=True, blank=True, validators=[validate_year])
    title = models.CharField("Danh hiệu / Chi tiết", max_length=150, blank=True,
                             help_text="Ví dụ: Top 10, Top 100...")
    citation = models.CharField("Ghi chú / Quyết định", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "id"]
        verbose_name = "giải thưởng doanh nhân"
        verbose_name_plural = "giải thưởng doanh nhân"

    def __str__(self):
        y = f" ({self.year})" if self.year else ""
        return f"{self.person.full_name} – {self.badge.name}{y}"


class CompanyAward(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="awards", verbose_name="Doanh nghiệp")
    badge = models.ForeignKey(AwardBadge, on_delete=models.CASCADE, related_name="company_awardees", verbose_name="Giải thưởng")
    year = models.PositiveSmallIntegerField("Năm vinh danh", null=True, blank=True, validators=[validate_year])
    title = models.CharField("Danh hiệu / Chi tiết", max_length=150, blank=True,
                             help_text="Ví dụ: Top 10, Top 100, Huân chương...")
    citation = models.CharField("Ghi chú / Quyết định", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "id"]
        verbose_name = "giải thưởng doanh nghiệp"
        verbose_name_plural = "giải thưởng doanh nghiệp"

    def __str__(self):
        y = f" ({self.year})" if self.year else ""
        return f"{self.company.display_name} – {self.badge.name}{y}"


# --------------------------------------------------------------------------- hiệp hội
class Association(SluggedModel):
    class Level(models.TextChoices):
        NATIONAL = "national", "Toàn quốc"
        PROVINCIAL = "provincial", "Tỉnh / thành"
        BRANCH = "branch", "Chi hội"
        CLUB = "club", "CLB ngành"

    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children",
                               verbose_name="Thuộc hiệp hội")
    name = models.CharField("Tên hiệp hội", max_length=200)
    short_name = models.CharField("Tên viết tắt", max_length=30, blank=True)
    level = models.CharField("Cấp", max_length=12, choices=Level.choices, default=Level.PROVINCIAL)
    province = models.ForeignKey(Province, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Tỉnh / thành")
    is_partner = models.BooleanField("Đối tác xác minh", default=False)
    partner_since = models.DateField("Đối tác từ ngày", null=True, blank=True)
    description = models.TextField("Giới thiệu (markdown)", blank=True)
    logo = models.ImageField("Logo", upload_to="associations/%Y/", blank=True, validators=[image_extensions, max_file_size])
    website = models.URLField("Website", blank=True)
    sectors = models.ManyToManyField(Sector, blank=True, related_name="associations", verbose_name="Ngành liên quan")
    status = models.CharField("Trạng thái", max_length=10, choices=Status.choices, default=Status.PUBLISHED)

    class Meta:
        ordering = ["name"]
        verbose_name = verbose_name_plural = "hiệp hội"

    def __str__(self):
        return self.name

    def slug_source(self):
        return self.short_name or self.name

    def search_source(self):
        return f"{self.name} {self.short_name}"

    def get_absolute_url(self):
        return reverse("public:association_detail", args=[self.slug])

    @property
    def initials(self):
        if self.short_name:
            return self.short_name[:4]
        return {"branch": "CH", "club": "CLB"}.get(self.level, "HH")


class Membership(models.Model):
    class State(models.TextChoices):
        PENDING = "pending", "Chờ xác nhận"
        CONFIRMED = "confirmed", "Đã xác nhận"
        REJECTED = "rejected", "Không xác nhận"

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="memberships")
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name="memberships")
    position = models.CharField("Chức danh trong hội", max_length=100, default="Hội viên")
    is_leadership = models.BooleanField("Thuộc ban chấp hành", default=False)
    sort_order = models.PositiveSmallIntegerField(default=100)
    start_year = models.PositiveSmallIntegerField(null=True, blank=True, validators=[validate_year])
    end_year = models.PositiveSmallIntegerField(null=True, blank=True, validators=[validate_year])
    state = models.CharField(max_length=10, choices=State.choices, default=State.CONFIRMED)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("person", "association")]
        ordering = ["-is_leadership", "sort_order", "person__full_name"]


# --------------------------------------------------------------------------- sự kiện
class Event(SluggedModel):
    class Kind(models.TextChoices):
        CONFERENCE = "conference", "Hội thảo"
        B2B = "b2b", "Kết nối giao thương"
        AWARD = "award", "Trao giải"
        TRAINING = "training", "Đào tạo"
        GALA = "gala", "Gala – Đại hội"
        OTHER = "other", "Khác"

    class EventStatus(models.TextChoices):
        DRAFT = "draft", "Bản nháp"
        PUBLISHED = "published", "Đã công bố"
        CANCELLED = "cancelled", "Đã hủy"
        ARCHIVED = "archived", "Đã ẩn"

    title = models.CharField("Tên sự kiện", max_length=200)
    kind = models.CharField("Loại", max_length=12, choices=Kind.choices, default=Kind.CONFERENCE)
    starts_at = models.DateTimeField("Bắt đầu")
    ends_at = models.DateTimeField("Kết thúc", null=True, blank=True)
    venue = models.CharField("Địa điểm", max_length=255, blank=True)
    province = models.ForeignKey(Province, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Tỉnh / thành")
    is_online = models.BooleanField("Trực tuyến", default=False)
    organizer = models.ForeignKey(Association, null=True, blank=True, on_delete=models.SET_NULL, related_name="events",
                                  verbose_name="Đơn vị tổ chức")
    organizer_text = models.CharField("Đơn vị tổ chức (khác)", max_length=200, blank=True)
    description = models.TextField("Mô tả (markdown)", blank=True)
    registration_url = models.URLField("Link đăng ký", blank=True)
    cover = models.ImageField("Ảnh bìa", upload_to="events/%Y/", blank=True, validators=[image_extensions, max_file_size])
    sectors = models.ManyToManyField(Sector, blank=True, related_name="events", verbose_name="Ngành liên quan")
    status = models.CharField("Trạng thái", max_length=10, choices=EventStatus.choices, default=EventStatus.PUBLISHED)
    is_featured = models.BooleanField("Nổi bật", default=False)
    views_count = models.PositiveIntegerField("Lượt xem", default=0)
    likes_count = models.PositiveIntegerField("Lượt quan tâm / tim", default=0)

    class Meta:
        ordering = ["-starts_at"]
        verbose_name = verbose_name_plural = "sự kiện"

    def __str__(self):
        return self.title

    def slug_source(self):
        return f"{self.title} {self.starts_at:%Y}" if self.starts_at else self.title

    def get_absolute_url(self):
        return reverse("public:event_detail", args=[self.slug])

    @property
    def is_upcoming(self):
        return (self.ends_at or self.starts_at) >= timezone.now()

    @property
    def organizer_name(self):
        return self.organizer.name if self.organizer_id else self.organizer_text

    @property
    def location_label(self):
        if self.venue and self.province:
            return f"{self.venue}, {self.province.name}"
        return self.venue or (self.province.name if self.province else "Toàn quốc / Trực tuyến")


class EventParticipant(models.Model):
    class Role(models.TextChoices):
        SPEAKER = "speaker", "Diễn giả"
        SPONSOR = "sponsor", "Nhà tài trợ"
        AWARDEE = "awardee", "Nhận giải"
        ORGANIZER = "organizer", "Ban tổ chức"
        ATTENDEE = "attendee", "Tham dự"

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="participants")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="event_participations")
    role = models.CharField("Vai trò", max_length=10, choices=Role.choices, default=Role.ATTENDEE)
    note = models.CharField("Ghi chú (tên giải, chủ đề bài nói…)", max_length=200, blank=True)
    milestone = models.ForeignKey(Milestone, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        unique_together = [("event", "person", "role")]
        ordering = ["role", "person__full_name"]


# --------------------------------------------------------------------------- video (chỉ lưu link)
class Video(models.Model):
    class Kind(models.TextChoices):
        INTERVIEW = "interview", "Phỏng vấn doanh nhân"
        COMPANY = "company", "Câu chuyện doanh nghiệp"
        EVENT = "event", "Sự kiện"
        TALK = "talk", "Bài nói"

    class VStatus(models.TextChoices):
        PUBLISHED = "published", "Đang hiển thị"
        HIDDEN = "hidden", "Đã ẩn"

    url = models.URLField("Link video", unique=True, max_length=500)
    platform = models.CharField(max_length=10, editable=False, default="other")
    external_id = models.CharField(max_length=64, blank=True, editable=False)
    title = models.CharField("Tiêu đề", max_length=300)
    description = models.TextField("Mô tả", blank=True)
    kind = models.CharField("Loại", max_length=10, choices=Kind.choices, default=Kind.INTERVIEW)
    thumbnail_url = models.URLField("Ảnh bìa", blank=True, max_length=500)
    duration_seconds = models.PositiveIntegerField("Thời lượng (giây)", null=True, blank=True)
    channel_name = models.CharField("Kênh", max_length=200, blank=True)
    published_on = models.DateField("Ngày đăng", null=True, blank=True)
    status = models.CharField("Trạng thái", max_length=10, choices=VStatus.choices, default=VStatus.PUBLISHED)
    availability = models.CharField(max_length=12, default="unknown", editable=False)  # ok | unavailable | unknown
    last_checked_at = models.DateTimeField(null=True, blank=True, editable=False)
    is_featured = models.BooleanField("Nổi bật", default=False)
    persons = models.ManyToManyField(Person, blank=True, related_name="videos", verbose_name="Doanh nhân")
    companies = models.ManyToManyField(Company, blank=True, related_name="videos", verbose_name="Doanh nghiệp")
    events = models.ManyToManyField(Event, blank=True, related_name="videos", verbose_name="Sự kiện")
    associations = models.ManyToManyField(Association, blank=True, related_name="videos", verbose_name="Hiệp hội")
    search_text = models.TextField(blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_on", "-created_at"]
        verbose_name = verbose_name_plural = "video"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        info = parse_video_url(self.url)
        if info:
            self.platform = info.platform
            self.external_id = info.external_id
            if not self.thumbnail_url and info.thumbnail_url:
                self.thumbnail_url = info.thumbnail_url
        self.search_text = normalize(f"{self.title} {self.channel_name} {self.description}")
        super().save(*args, **kwargs)

    @property
    def platform_label(self):
        return PLATFORM_LABELS.get(self.platform, "Nền tảng khác")

    @property
    def embeddable(self):
        return self.platform in ("youtube", "vimeo", "facebook", "tiktok")

    @property
    def duration_label(self):
        return format_duration(self.duration_seconds)

    @property
    def related_label(self):
        names = [p.full_name for p in self.persons.all()[:1]] or [c.display_name for c in self.companies.all()[:1]] \
            or [e.title for e in self.events.all()[:1]]
        return names[0] if names else self.channel_name


def visible_videos():
    """Video được phép hiện: đã duyệt, đang hiển thị và link chưa bị báo mất."""
    return Video.objects.filter(status=Video.VStatus.PUBLISHED).exclude(availability="unavailable")


# --------------------------------------------------------------------------- Câu chuyện & Phóng sự (Story)
class Story(SluggedModel):
    class StoryType(models.TextChoices):
        PORTRAIT = "portrait", "Chân dung nhân vật"
        JOURNEY = "journey", "Hành trình khởi nghiệp"
        CASE_STUDY = "case_study", "Bài học thương trường"
        EVENT = "event", "Phóng sự sự kiện"
        INTERVIEW = "interview", "Phỏng vấn chuyên sâu"
        INSIGHT = "insight", "Góc nhìn doanh nhân"

    title = models.CharField("Tiêu đề bài viết", max_length=255)
    story_type = models.CharField("Phân loại", max_length=30, choices=StoryType.choices, default=StoryType.PORTRAIT)
    summary = models.TextField("Tóm tắt / Sa-pô bài viết", blank=True, help_text="Đoạn văn mở đầu định dạng báo chí, khơi gợi và tóm lược nội dung chính.")
    content_md = models.TextField("Nội dung bài viết (Markdown)", blank=True, help_text="Hỗ trợ đầy đủ định dạng văn bản, tiêu đề, trích dẫn, ảnh, liên kết...")
    cover_image = models.ImageField("Ảnh bìa đại diện", upload_to="stories/%Y/%m/", blank=True, validators=[image_extensions, max_file_size])
    cover_caption = models.CharField("Chú thích ảnh bìa", max_length=255, blank=True)
    author_name = models.CharField("Tác giả / Bút danh", max_length=120, blank=True, default="Ban Biên tập doanhnhan.wiki")
    source_name = models.CharField("Nguồn / Đơn vị phối hợp", max_length=150, blank=True)
    source_url = models.URLField("Liên kết nguồn gốc", blank=True)

    featured_person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL, related_name="stories", verbose_name="Doanh nhân nhân vật chính")
    featured_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL, related_name="stories", verbose_name="Doanh nghiệp liên quan")
    featured_event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL, related_name="stories", verbose_name="Sự kiện liên quan")

    is_featured = models.BooleanField("Ghim nổi bật (Featured)", default=False, help_text="Hiển thị ở vị trí tiêu điểm trên đầu trang Story.")
    status = models.CharField("Trạng thái", max_length=20, choices=Status.choices, default=Status.PUBLISHED)
    published_at = models.DateTimeField("Thời điểm xuất bản", default=timezone.now)
    views_count = models.PositiveIntegerField("Lượt xem", default=0)
    likes_count = models.PositiveIntegerField("Lượt thích / tim", default=0)

    class Meta:
        verbose_name = "câu chuyện doanh nhân"
        verbose_name_plural = "câu chuyện doanh nhân (Story)"
        ordering = ["-is_featured", "-published_at", "-id"]

    def slug_source(self):
        return self.title

    def search_source(self):
        return f"{self.title} {self.summary} {self.author_name} {self.source_name}"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("public:story_detail", kwargs={"slug": self.slug})

    @property
    def reading_time_minutes(self):
        words = len((self.content_md or "").split())
        return max(1, round(words / 200))


# --------------------------------------------------------------------------- Bưu thiếp danh ngôn (Postcard)
class Postcard(SluggedModel):
    class Topic(models.TextChoices):
        STARTUP = "startup", "Khởi nghiệp & Bản lĩnh"
        LEADERSHIP = "leadership", "Quản trị & Lãnh đạo"
        INNOVATION = "innovation", "Đổi mới sáng tạo"
        ETHICS = "ethics", "Đạo đức kinh doanh"
        VISION = "vision", "Tầm nhìn & Khát vọng"
        LESSON = "lesson", "Bài học cuộc sống"

    title = models.CharField("Tiêu đề / Ý niệm", max_length=255, help_text="Tiêu đề ngắn gọn làm nổi bật thông điệp")
    quote = models.TextField("Trích dẫn / Danh ngôn", help_text="Nội dung câu nói, triết lý kinh doanh hoặc bài học sâu sắc")
    person = models.ForeignKey(
        Person,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="postcards",
        verbose_name="Doanh nhân phát biểu",
    )
    author_custom = models.CharField(
        "Tác giả ngoài hệ thống",
        max_length=150,
        blank=True,
        help_text="Nhập nếu câu nói của danh nhân lịch sử hoặc chưa có hồ sơ",
    )
    author_title = models.CharField(
        "Chức vụ / Danh vị",
        max_length=200,
        blank=True,
        help_text="Ví dụ: Chủ tịch Tập đoàn Vingroup, Sáng lập FPT...",
    )
    company = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="postcards",
        verbose_name="Doanh nghiệp liên quan",
    )
    topic = models.CharField(
        "Chủ đề",
        max_length=40,
        choices=Topic.choices,
        default=Topic.STARTUP,
    )
    image = models.ImageField(
        "Ảnh thiết kế Postcard",
        upload_to="postcards/%Y/%m/",
        blank=True,
        validators=[image_extensions, max_file_size],
        help_text="Hình ảnh thiết kế đẹp mắt dạng thiệp/postcard (tỷ lệ 1:1, 4:5 hoặc 16:9)",
    )
    context = models.CharField(
        "Bối cảnh phát biểu",
        max_length=255,
        blank=True,
        help_text="Ví dụ: Chia sẻ tại Diễn đàn Doanh nghiệp 2024, Trả lời phỏng vấn Forbes...",
    )
    is_featured = models.BooleanField("Ghim nổi bật", default=False)
    status = models.CharField("Trạng thái", max_length=20, choices=Status.choices, default=Status.PUBLISHED)
    published_at = models.DateTimeField("Thời điểm đăng", default=timezone.now)
    views_count = models.PositiveIntegerField("Lượt xem", default=0)
    downloads_count = models.PositiveIntegerField("Lượt tải về", default=0)

    class Meta:
        verbose_name = "bưu thiếp danh ngôn"
        verbose_name_plural = "bưu thiếp danh ngôn (Postcard)"
        ordering = ["-is_featured", "-published_at", "-id"]

    def slug_source(self):
        return self.title or self.quote[:60]

    def search_source(self):
        return f"{self.title} {self.quote} {self.display_author_name} {self.context}"

    def __str__(self):
        return self.title

    @property
    def display_author_name(self):
        if self.person:
            return self.person.name
        return self.author_custom or "Doanh nhân ẩn danh"

    @property
    def display_author_title(self):
        if self.author_title:
            return self.author_title
        if self.person:
            return self.person.current_title or ""
        return ""

    def get_absolute_url(self):
        return reverse("public:postcard_detail", kwargs={"slug": self.slug})


# --------------------------------------------------------------------------- Chương trình Podcast doanh nhân
class Podcast(SluggedModel):
    class SeriesType(models.TextChoices):
        DIALOGUE = "dialogue", "Đối thoại Doanh nhân"
        STARTUP = "startup", "Chuyện Khởi nghiệp"
        LEADERSHIP = "leadership", "Góc nhìn Quản trị & Lãnh đạo"
        MARKET = "market", "Bản lĩnh Thương trường"
        INNOVATION = "innovation", "Đổi mới sáng tạo & Công nghệ"
        TALK = "talk", "Tâm sự Doanh nhân"

    title = models.CharField("Tiêu đề tập podcast", max_length=255, help_text="Ví dụ: Tập 12: Hành trình từ số 0 đến kỳ lân công nghệ")
    episode_number = models.PositiveIntegerField("Số tập (Episode #)", null=True, blank=True)
    series_type = models.CharField("Chủ đề / Phân loại", max_length=40, choices=SeriesType.choices, default=SeriesType.DIALOGUE)
    series_name = models.CharField("Tên Series / Chương trình", max_length=150, blank=True, default="Đối thoại Doanh nhân")
    host_name = models.CharField("Người dẫn chuyện (Host)", max_length=120, blank=True, default="Ban Biên tập doanhnhan.wiki")
    guest_person = models.ForeignKey(
        Person,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="podcasts",
        verbose_name="Doanh nhân khách mời",
    )
    guest_custom = models.CharField("Khách mời ngoài hệ thống", max_length=150, blank=True)
    guest_title = models.CharField("Chức danh khách mời", max_length=200, blank=True)
    company = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="podcasts",
        verbose_name="Doanh nghiệp liên quan",
    )
    cover_image = models.ImageField(
        "Ảnh bìa tập Podcast",
        upload_to="podcasts/%Y/%m/",
        blank=True,
        validators=[image_extensions, max_file_size],
        help_text="Ảnh bìa tỷ lệ 1:1 (vuông) hoặc 16:9 chất lượng cao",
    )
    summary = models.TextField("Tóm tắt nội dung", blank=True, help_text="Giới thiệu nội dung trọng tâm của buổi trò chuyện")
    content_md = models.TextField(
        "Ghi chú tập & Mốc thời gian (Timestamps)",
        blank=True,
        help_text="Ví dụ: [02:15] Lý do khởi nghiệp; [15:30] Khủng hoảng đầu tiên...",
    )
    audio_url = models.URLField("Đường dẫn file Audio trực tiếp (MP3/Soundcloud)", max_length=500, blank=True)
    video_url = models.URLField("Đường dẫn Video Podcast (YouTube)", max_length=500, blank=True)
    spotify_url = models.URLField("Link nghe trên Spotify", max_length=500, blank=True)
    apple_podcasts_url = models.URLField("Link nghe trên Apple Podcasts", max_length=500, blank=True)
    youtube_url = models.URLField("Link xem trên YouTube", max_length=500, blank=True)
    duration_minutes = models.PositiveIntegerField("Thời lượng (phút)", default=30)

    is_featured = models.BooleanField("Tập tiêu điểm (Featured)", default=False)
    status = models.CharField("Trạng thái", max_length=20, choices=Status.choices, default=Status.PUBLISHED)
    published_at = models.DateTimeField("Thời điểm phát sóng", default=timezone.now)
    views_count = models.PositiveIntegerField("Lượt xem / nghe", default=0)
    listeners_count = models.PositiveIntegerField("Lượt phát âm thanh", default=0)
    likes_count = models.PositiveIntegerField("Lượt thích / tim", default=0)

    class Meta:
        verbose_name = "tập podcast doanh nhân"
        verbose_name_plural = "podcast doanh nhân"
        ordering = ["-is_featured", "-published_at", "-id"]

    def slug_source(self):
        return self.title

    def search_source(self):
        return f"{self.title} {self.summary} {self.display_guest_name} {self.host_name} {self.series_name}"

    def __str__(self):
        ep = f"#{self.episode_number}: " if self.episode_number else ""
        return f"{ep}{self.title}"

    @property
    def display_guest_name(self):
        if self.guest_person:
            return self.guest_person.full_name
        return self.guest_custom or "Khách mời chuyên gia"

    @property
    def display_guest_title(self):
        if self.guest_title:
            return self.guest_title
        if self.guest_person:
            return self.guest_person.current_title or ""
        return ""

    @property
    def youtube_embed_id(self):
        if not self.video_url and not self.youtube_url:
            return ""
        url = self.video_url or self.youtube_url
        match = re.search(r"(?:v=|\/embed\/|youtu\.be\/|\/v\/)([a-zA-Z0-9_-]{11})", url)
        return match.group(1) if match else ""

    def get_absolute_url(self):
        return reverse("public:podcast_detail", kwargs={"slug": self.slug})



