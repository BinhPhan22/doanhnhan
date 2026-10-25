"""Nội dung trang do quản trị cấu hình: thông tin vận hành, tài trợ, chính sách, liên hệ."""
from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.validators import image_extensions, max_file_size


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    operator_name = models.CharField("Đơn vị vận hành", max_length=200, default="Digits Technology")
    contact_email = models.EmailField("Email liên hệ", blank=True)
    editorial_email = models.EmailField("Email ban biên tập", blank=True)
    contact_phone = models.CharField("Số điện thoại", max_length=40, blank=True)
    address = models.CharField("Địa chỉ", max_length=255, blank=True)
    about_md = models.TextField("Giới thiệu (markdown)", blank=True)
    review_days = models.PositiveSmallIntegerField("Số ngày làm việc để duyệt", default=3)
    gemini_api_key = models.CharField(
        "Google Gemini API Key",
        max_length=255,
        blank=True,
        help_text="Khóa API Google Gemini lấy từ https://aistudio.google.com/app/apikey (bắt đầu bằng AIzaSy...).",
    )
    gemini_model = models.CharField(
        "Mô hình AI (Gemini Model)",
        max_length=80,
        default="gemini-2.5-flash",
        blank=True,
        help_text="Mặc định: gemini-2.5-flash (khuyên dùng). Các tùy chọn khác: gemini-1.5-flash, gemini-1.5-pro.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = verbose_name_plural = "cài đặt chung"


class DonationSettings(SingletonModel):
    title = models.CharField("Tiêu đề", max_length=255,
                             default="Cùng doanhnhan.wiki lưu giữ hành trình của doanh nhân trẻ tiêu biểu Việt Nam")
    lead = models.TextField("Đoạn mở đầu", blank=True)
    body_md = models.TextField("Nội dung bài viết (markdown)", blank=True)
    memo = models.CharField("Nội dung chuyển khoản", max_length=120, default="Tài trợ website doanhnhan.wiki")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = verbose_name_plural = "trang tài trợ"


class DonationAccount(models.Model):
    """Tài khoản nhận tài trợ. Tài khoản mới hoặc thay đổi cần quản trị viên thứ hai duyệt mới hiển thị."""

    class State(models.TextChoices):
        PENDING = "pending", "Chờ quản trị viên thứ hai duyệt"
        ACTIVE = "active", "Đang hiển thị"
        RETIRED = "retired", "Đã thay thế / ngừng"

    bank_name = models.CharField("Ngân hàng", max_length=120)
    account_number = models.CharField("Số tài khoản", max_length=40)
    account_holder = models.CharField("Chủ tài khoản", max_length=200)
    qr_image = models.ImageField("Mã QR", upload_to="donation/", blank=True, validators=[image_extensions, max_file_size])
    sort_order = models.PositiveSmallIntegerField("Thứ tự", default=0)
    state = models.CharField(max_length=10, choices=State.choices, default=State.PENDING)
    replaces = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name="+")
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.bank_name} · {self.account_number}"


class PolicyDocument(models.Model):
    code = models.SlugField("Mã", unique=True)
    title = models.CharField("Tên văn bản", max_length=200)
    requires_acceptance = models.BooleanField("Bắt buộc đồng ý", default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.title

    def current_version(self):
        return (self.versions.filter(status=PolicyVersion.State.PUBLISHED, effective_at__lte=timezone.now())
                .order_by("-effective_at", "-id").first())


class PolicyVersion(models.Model):
    class State(models.TextChoices):
        DRAFT = "draft", "Bản nháp"
        PUBLISHED = "published", "Đã xuất bản / lên lịch"

    document = models.ForeignKey(PolicyDocument, on_delete=models.CASCADE, related_name="versions")
    version = models.CharField("Số phiên bản", max_length=20)
    effective_at = models.DateTimeField("Ngày hiệu lực", default=timezone.now)
    summary_of_changes = models.TextField("Tóm tắt thay đổi", blank=True)
    summary_points = models.TextField("Tóm tắt dễ hiểu (mỗi dòng một ý)", blank=True)
    body_md = models.TextField("Toàn văn (markdown)")
    status = models.CharField(max_length=10, choices=State.choices, default=State.DRAFT)
    require_reaccept = models.BooleanField("Yêu cầu người dùng đồng ý lại", default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-effective_at", "-id"]
        unique_together = [("document", "version")]

    def __str__(self):
        return f"{self.document.title} {self.version}"

    @property
    def is_scheduled(self):
        return self.status == self.State.PUBLISHED and self.effective_at > timezone.now()


class PolicyAcceptance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="policy_acceptances")
    version = models.ForeignKey(PolicyVersion, on_delete=models.PROTECT, related_name="acceptances")
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    method = models.CharField(max_length=20, default="signup")  # signup | reaccept | google

    class Meta:
        unique_together = [("user", "version")]


class InterviewRequest(models.Model):
    class Kind(models.TextChoices):
        INTERVIEW = "interview", "Phỏng vấn doanh nhân"
        COMPANY = "company", "Câu chuyện doanh nghiệp"
        EVENT = "event", "Ghi hình tại sự kiện"
        OTHER = "other", "Khác"

    class Format(models.TextChoices):
        ONSITE = "onsite", "Tại văn phòng / nhà máy"
        STUDIO = "studio", "Tại trường quay"
        ONLINE = "online", "Trực tuyến"
        EVENT = "event", "Tại sự kiện"

    class State(models.TextChoices):
        NEW = "new", "Mới"
        CONTACTED = "contacted", "Đã liên hệ"
        SCHEDULED = "scheduled", "Đã lên lịch"
        FILMED = "filmed", "Đã ghi hình"
        PUBLISHED = "published", "Đã đăng video"
        DECLINED = "declined", "Không thực hiện"

    full_name = models.CharField("Họ và tên", max_length=150)
    title = models.CharField("Chức vụ", max_length=150, blank=True)
    company = models.CharField("Doanh nghiệp", max_length=200)
    phone = models.CharField("Số điện thoại", max_length=30)
    email = models.EmailField("Email")
    kind = models.CharField("Nội dung muốn thực hiện", max_length=10, choices=Kind.choices, default=Kind.INTERVIEW)
    story = models.TextField("Câu chuyện bạn muốn chia sẻ", blank=True)
    format = models.CharField("Hình thức", max_length=10, choices=Format.choices, default=Format.ONSITE)
    address = models.CharField("Địa chỉ dự kiến ghi hình", max_length=255, blank=True)
    preferred_time = models.DateTimeField("Thời gian thuận tiện", null=True, blank=True)
    reference_url = models.URLField("Website / tư liệu tham khảo", blank=True)
    state = models.CharField("Trạng thái", max_length=10, choices=State.choices, default=State.NEW)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name="+", verbose_name="Phụ trách")
    video = models.ForeignKey("directory.Video", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    staff_note = models.TextField("Ghi chú nội bộ", blank=True)
    consent_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ContactMessage(models.Model):
    class Topic(models.TextChoices):
        PARTNER = "partner", "Đăng ký làm hiệp hội đối tác"
        EVENT = "event", "Gửi sự kiện"
        CORRECTION = "correction", "Góp ý / Báo thông tin cần cập nhật"
        OTHER = "other", "Khác"

    topic = models.CharField("Chủ đề", max_length=12, choices=Topic.choices, default=Topic.OTHER)
    full_name = models.CharField("Họ và tên", max_length=150)
    organization = models.CharField("Tổ chức", max_length=200, blank=True)
    email = models.EmailField("Email")
    phone = models.CharField("Số điện thoại", max_length=30, blank=True)
    source_url = models.TextField("Nguồn đối chiếu / Link kiểm chứng", blank=True,
                                  help_text="Đường link bài báo, cổng ĐKKD, văn bản quyết định... để Ban biên tập đối chiếu.")
    message = models.TextField("Nội dung")
    handled = models.BooleanField("Đã xử lý", default=False)
    staff_note = models.TextField("Ghi chú nội bộ", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class DataRequest(models.Model):
    """Yêu cầu của chủ thể dữ liệu: xem, sửa, xóa, rút đồng ý."""

    class Kind(models.TextChoices):
        ACCESS = "access", "Xem dữ liệu của tôi"
        CORRECT = "correct", "Sửa dữ liệu"
        DELETE = "delete", "Xóa / ẩn hồ sơ"
        WITHDRAW = "withdraw", "Rút lại đồng ý"

    class State(models.TextChoices):
        OPEN = "open", "Mới"
        IN_PROGRESS = "in_progress", "Đang xử lý"
        DONE = "done", "Đã xong"
        REJECTED = "rejected", "Từ chối"

    full_name = models.CharField("Họ và tên", max_length=150)
    email = models.EmailField("Email")
    profile_url = models.CharField("Link hồ sơ liên quan", max_length=300, blank=True)
    kind = models.CharField("Yêu cầu", max_length=10, choices=Kind.choices)
    detail = models.TextField("Chi tiết")
    state = models.CharField(max_length=12, choices=State.choices, default=State.OPEN)
    handled_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    resolved_at = models.DateTimeField(null=True, blank=True)
    staff_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
