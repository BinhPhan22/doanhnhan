from django import forms
from django.utils import timezone

from apps.common.forms import StyledFormMixin
from apps.directory.models import (
    Association, AwardBadge, Company, CompanyAward, Event, Person, PersonAward, Podcast, Postcard, Sector, Story, Video,
)
from apps.sitecontent.models import (
    ContactMessage, DataRequest, DonationAccount, DonationSettings, InterviewRequest, PolicyDocument, PolicyVersion,
    SiteSettings,
)


SECTOR_ICON_CHOICES = [
    ("tech", "Công nghệ / Kỹ thuật"),
    ("factory", "Sản xuất / Công nghiệp"),
    ("retail", "Bán lẻ / Tiêu dùng"),
    ("food", "Thực phẩm / F&B"),
    ("building", "Bất động sản / Xây dựng"),
    ("education", "Giáo dục / Đào tạo"),
    ("agri", "Nông nghiệp / Thủy sản"),
    ("logistics", "Vận tải / Logistics"),
    ("finance", "Tài chính / Ngân hàng"),
    ("health", "Y tế / Dược phẩm"),
    ("creative", "Truyền thông / Sáng tạo"),
    ("travel", "Du lịch / Khách sạn"),
]


class SectorForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Sector
        fields = ["name", "parent", "description", "icon", "vsic_code", "sort_order", "is_active", "slug"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
        help_texts = {"slug": "Để trống để tạo tự động từ tên.", "icon": "Chỉ áp dụng cho ngành cấp 1.",
                      "vsic_code": "Mã ngành cấp 2 theo VSIC 2025 (QĐ 36/2025/QĐ-TTg), ví dụ 62. Đăng ký kinh doanh dùng mã cấp 4."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["icon"].choices = SECTOR_ICON_CHOICES
        qs = Sector.objects.filter(parent__isnull=True, is_active=True)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        self.fields["parent"].queryset = qs
        self.fields["parent"].empty_label = "— Ngành cấp 1 —"


class AssociationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Association
        fields = ["name", "short_name", "level", "parent", "province", "is_partner", "partner_since", "website",
                  "description", "logo", "sectors", "status", "slug"]
        widgets = {"description": forms.Textarea(attrs={"rows": 8}), "partner_since": forms.DateInput(attrs={"type": "date"}),
                   "sectors": forms.CheckboxSelectMultiple}
        help_texts = {"slug": "Để trống để tạo tự động.", "description": "Hỗ trợ markdown."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["sectors"].queryset = Sector.objects.filter(parent__isnull=True, is_active=True)
        if self.instance.pk:
            self.fields["parent"].queryset = Association.objects.exclude(pk=self.instance.pk)


class EventForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "kind", "starts_at", "ends_at", "is_online", "venue", "province", "organizer",
                  "organizer_text", "registration_url", "description", "cover", "sectors", "status", "is_featured",
                  "slug"]
        widgets = {"starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
                   "ends_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
                   "description": forms.Textarea(attrs={"rows": 8}), "sectors": forms.CheckboxSelectMultiple}
        help_texts = {"slug": "Để trống để tạo tự động.", "description": "Hỗ trợ markdown.",
                      "organizer_text": "Dùng khi đơn vị tổ chức không phải hiệp hội trong hệ thống."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["sectors"].queryset = Sector.objects.filter(parent__isnull=True, is_active=True)
        for f in ("starts_at", "ends_at"):
            self.fields[f].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M"]

    def clean(self):
        data = super().clean()
        if data.get("ends_at") and data.get("starts_at") and data["ends_at"] < data["starts_at"]:
            self.add_error("ends_at", "Thời gian kết thúc phải sau thời gian bắt đầu.")
        return data


class VideoForm(StyledFormMixin, forms.ModelForm):
    duration = forms.CharField(label="Thời lượng (mm:ss hoặc h:mm:ss)", required=False)

    class Meta:
        model = Video
        fields = ["url", "title", "kind", "description", "channel_name", "published_on", "thumbnail_url", "status",
                  "is_featured", "events", "associations"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3}), "published_on": forms.DateInput(attrs={"type": "date"}),
                   "url": forms.URLInput(attrs={"data-video-input": "#video-status", "placeholder": "https://www.youtube.com/watch?v=…"}),
                   "events": forms.SelectMultiple(attrs={"size": 6}), "associations": forms.SelectMultiple(attrs={"size": 6})}
        help_texts = {"title": "Để trống: tự lấy tiêu đề từ nền tảng (YouTube, Vimeo, TikTok).",
                      "thumbnail_url": "Để trống: tự lấy ảnh bìa.", "url": "Chỉ lưu link, không tải tệp video."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = False
        self.fields["events"].required = False
        self.fields["associations"].required = False
        if self.instance.duration_seconds:
            self.initial["duration"] = self.instance.duration_label

    def clean_duration(self):
        raw = self.cleaned_data.get("duration", "").strip()
        if not raw:
            return None
        try:
            parts = [int(p) for p in raw.split(":")]
        except ValueError:
            raise forms.ValidationError("Nhập dạng mm:ss hoặc h:mm:ss")
        seconds = 0
        for p in parts:
            seconds = seconds * 60 + p
        return seconds


class DonationSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = DonationSettings
        fields = ["title", "lead", "body_md", "memo"]
        widgets = {"lead": forms.Textarea(attrs={"rows": 3}), "body_md": forms.Textarea(attrs={"rows": 18})}
        help_texts = {"body_md": "Markdown: ## tiêu đề mục, - gạch đầu dòng, **chữ đậm**."}


class DonationAccountForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = DonationAccount
        fields = ["bank_name", "account_number", "account_holder", "qr_image", "sort_order"]

    def clean_account_number(self):
        value = self.cleaned_data["account_number"].replace(" ", "")
        if not value.isdigit():
            raise forms.ValidationError("Số tài khoản chỉ gồm chữ số.")
        return value


class PolicyDocumentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PolicyDocument
        fields = ["title", "code", "requires_acceptance", "sort_order"]
        help_texts = {"code": "Dùng trong đường dẫn /chinh-sach/<mã>/. Các mã dieu-khoan, chinh-sach-du-lieu, "
                              "quy-che-bien-tap được liên kết ở chân trang."}


class PolicyVersionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PolicyVersion
        fields = ["version", "effective_at", "summary_of_changes", "summary_points", "body_md", "status",
                  "require_reaccept"]
        widgets = {"effective_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
                   "summary_of_changes": forms.Textarea(attrs={"rows": 2}),
                   "summary_points": forms.Textarea(attrs={"rows": 4}), "body_md": forms.Textarea(attrs={"rows": 24})}
        help_texts = {"status": "“Đã xuất bản” với ngày hiệu lực trong tương lai = lên lịch.",
                      "require_reaccept": "Người dùng đã đăng nhập phải đồng ý lại (chỉ dùng cho thay đổi quan trọng)."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["effective_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        if not self.instance.pk:
            self.initial.setdefault("effective_at", timezone.localtime().strftime("%Y-%m-%dT%H:%M"))


class SiteSettingsForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ["operator_name", "contact_email", "editorial_email", "contact_phone", "address",
                  "gemini_api_key", "gemini_model",
                  "review_days", "about_md"]
        widgets = {
            "about_md": forms.Textarea(attrs={"rows": 12}),
            "gemini_api_key": forms.TextInput(attrs={
                "placeholder": "AIzaSy... (dán mã API Key tại đây)",
                "autocomplete": "off",
                "style": "font-family: ui-monospace, monospace; letter-spacing: 0.5px;",
            }),
            "gemini_model": forms.TextInput(attrs={
                "placeholder": "gemini-2.5-flash",
            }),
        }
        help_texts = {
            "gemini_api_key": "Lấy API Key miễn phí tại https://aistudio.google.com/app/apikey. Nhập tại đây sẽ được lưu trữ trực tiếp vào hệ thống, không cần tìm hay sửa file .env.",
            "gemini_model": "Mặc định khuyến nghị: gemini-2.5-flash. Các tùy chọn khác: gemini-1.5-flash, gemini-1.5-pro.",
        }


class InterviewStaffForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = InterviewRequest
        fields = ["state", "assignee", "video", "staff_note"]
        widgets = {"staff_note": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.accounts.models import User

        self.fields["assignee"].queryset = User.objects.filter(role__in=["editor", "admin"], status="active")
        self.fields["video"].queryset = Video.objects.order_by("-created_at")


class ContactStaffForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["handled", "staff_note"]
        widgets = {"staff_note": forms.Textarea(attrs={"rows": 3})}


class DataRequestStaffForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = DataRequest
        fields = ["state", "staff_note"]
        widgets = {"staff_note": forms.Textarea(attrs={"rows": 4})}


class AwardBadgeForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AwardBadge
        fields = ["name", "code", "badge_type", "issuer", "color", "icon", "description", "sort_order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "color": forms.Select(choices=[
                ("gold", "Vàng ánh kim (Gold - Mặc định)"),
                ("red", "Đỏ danh dự (Red)"),
                ("blue", "Xanh dương (Blue)"),
                ("green", "Xanh lá (Green)"),
            ]),
            "icon": forms.Select(choices=[
                ("star", "★ Ngôi sao (star)"),
                ("medal", "🎖️ Huy chương (medal)"),
                ("award", "🏆 Cúp vinh danh (award)"),
                ("trophy", "🏵️ Biểu trưng (trophy)"),
            ]),
        }
        help_texts = {
            "code": "Mã định danh rút gọn (chữ thường, gạch nối, ví dụ: sao-do, khoi-nghiep-xuat-sac).",
            "issuer": "Tên cơ quan, tổ chức trao giải (ví dụ: Trung ương Hội Doanh nhân trẻ Việt Nam).",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["code"].required = False

    def clean_code(self):
        from django.utils.text import slugify
        code = self.cleaned_data.get("code", "").strip()
        if not code:
            code = slugify(self.cleaned_data.get("name", ""))
        return code


class PersonAwardAssignForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PersonAward
        fields = ["person", "year", "title", "citation"]
        widgets = {
            "year": forms.NumberInput(attrs={"placeholder": "2024"}),
            "title": forms.TextInput(attrs={"placeholder": "Ví dụ: Top 10, Top 100, Doanh nhân tiêu biểu..."}),
            "citation": forms.TextInput(attrs={"placeholder": "Ví dụ: Quyết định số 123/QĐ-DNT, Báo Tuổi Trẻ đưa tin..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["person"].queryset = Person.objects.filter(status__in=["published", "draft"]).order_by("full_name")
        self.fields["person"].label = "Doanh nhân vinh danh"
        self.fields["person"].empty_label = "— Chọn doanh nhân —"


class CompanyAwardAssignForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CompanyAward
        fields = ["company", "year", "title", "citation"]
        widgets = {
            "year": forms.NumberInput(attrs={"placeholder": "2024"}),
            "title": forms.TextInput(attrs={"placeholder": "Ví dụ: Top 10, Top 100, Sao Vàng Đất Việt..."}),
            "citation": forms.TextInput(attrs={"placeholder": "Ví dụ: Quyết định số 123/QĐ-DNT, Báo Tuổi Trẻ..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].queryset = Company.objects.filter(status__in=["published", "draft"]).order_by("legal_name")
        self.fields["company"].label = "Doanh nghiệp vinh danh"
        self.fields["company"].empty_label = "— Chọn doanh nghiệp —"


class StoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Story
        fields = [
            "title", "story_type", "summary", "content_md", "cover_image", "cover_caption",
            "author_name", "source_name", "source_url",
            "featured_person", "featured_company", "featured_event",
            "is_featured", "status", "published_at", "slug",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "content_md": forms.Textarea(attrs={"rows": 16}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }
        help_texts = {
            "slug": "Để trống để hệ thống tự động tạo từ tiêu đề.",
            "summary": "Đoạn mở đầu (sa-pô) tóm tắt theo phong cách báo chí.",
            "content_md": "Hỗ trợ đầy đủ định dạng Markdown (tiêu đề #, in đậm **, trích dẫn >, ảnh ![], link...).",
            "is_featured": "Ghim bài viết ở vị trí tiêu điểm trên đầu trang Story.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["published_at"].required = False
        self.fields["featured_person"].queryset = Person.objects.filter(status__in=["published", "draft"]).order_by("full_name")
        self.fields["featured_person"].empty_label = "— Không liên kết —"
        self.fields["featured_company"].queryset = Company.objects.filter(status__in=["published", "draft"]).order_by("legal_name")
        self.fields["featured_company"].empty_label = "— Không liên kết —"
        self.fields["featured_event"].queryset = Event.objects.filter(status__in=["published", "draft"]).order_by("-starts_at")
        self.fields["featured_event"].empty_label = "— Không liên kết —"

        if not self.instance.pk and "published_at" in self.fields:
            self.initial["published_at"] = timezone.now().strftime("%Y-%m-%dT%H:%M")
        elif self.instance.pk and self.instance.published_at:
            self.initial["published_at"] = self.instance.published_at.strftime("%Y-%m-%dT%H:%M")

    def clean_published_at(self):
        return self.cleaned_data.get("published_at") or timezone.now()


class PostcardForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Postcard
        fields = [
            "title", "quote", "person", "author_custom", "author_title", "company",
            "topic", "image", "context", "is_featured", "status", "published_at", "slug",
        ]
        widgets = {
            "quote": forms.Textarea(attrs={"rows": 4, "placeholder": "Nhập nội dung trích dẫn / danh ngôn..."}),
            "context": forms.TextInput(attrs={"placeholder": "Ví dụ: Chia sẻ tại Diễn đàn Doanh nghiệp 2024..."}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }
        help_texts = {
            "slug": "Để trống để hệ thống tự động tạo từ tiêu đề hoặc câu trích dẫn.",
            "quote": "Trích dẫn nguyên văn câu nói, triết lý kinh doanh truyền cảm hứng.",
            "image": "Hình ảnh postcard đã được thiết kế sẵn (hoặc để trống nếu hiển thị thiệp text mặc định).",
            "person": "Chọn doanh nhân trong hệ thống (nếu có hồ sơ).",
            "author_custom": "Điền nếu là nhân vật lịch sử hoặc chưa có hồ sơ.",
            "is_featured": "Ghim nổi bật trên đầu thư viện Postcard.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["published_at"].required = False
        self.fields["person"].queryset = Person.objects.filter(status__in=["published", "draft"]).order_by("full_name")
        self.fields["person"].empty_label = "— Chọn doanh nhân —"
        self.fields["company"].queryset = Company.objects.filter(status__in=["published", "draft"]).order_by("legal_name")
        self.fields["company"].empty_label = "— Chọn doanh nghiệp liên quan (nếu có) —"

        if not self.instance.pk and "published_at" in self.fields:
            self.initial["published_at"] = timezone.now().strftime("%Y-%m-%dT%H:%M")
        elif self.instance.pk and self.instance.published_at:
            self.initial["published_at"] = self.instance.published_at.strftime("%Y-%m-%dT%H:%M")

    def clean_published_at(self):
        return self.cleaned_data.get("published_at") or timezone.now()


class PodcastForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Podcast
        fields = [
            "title", "episode_number", "series_type", "series_name", "host_name",
            "guest_person", "guest_custom", "guest_title", "company",
            "cover_image", "summary", "content_md",
            "audio_url", "video_url", "spotify_url", "apple_podcasts_url", "youtube_url",
            "duration_minutes", "is_featured", "status", "published_at", "slug",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3, "placeholder": "Tóm tắt chủ đề chính của tập podcast..."}),
            "content_md": forms.Textarea(attrs={"rows": 8, "placeholder": "Ghi chú nội dung, mốc thời gian [02:30], trích dẫn nổi bật..."}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }
        help_texts = {
            "slug": "Để trống để tự động tạo từ tiêu đề.",
            "audio_url": "Đường dẫn file MP3 trực tiếp hoặc link audio trực tuyến.",
            "video_url": "Đường dẫn YouTube nếu có bản ghi hình video podcast.",
            "content_md": "Hỗ trợ markdown. Bạn có thể chèn các mốc thời gian để người nghe bấm theo dõi.",
            "is_featured": "Ghim nổi bật trên đầu trang Podcast.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        self.fields["published_at"].required = False
        self.fields["guest_person"].queryset = Person.objects.filter(status__in=["published", "draft"]).order_by("full_name")
        self.fields["guest_person"].empty_label = "— Chọn doanh nhân khách mời —"
        self.fields["company"].queryset = Company.objects.filter(status__in=["published", "draft"]).order_by("legal_name")
        self.fields["company"].empty_label = "— Chọn doanh nghiệp liên quan (nếu có) —"

        if not self.instance.pk and "published_at" in self.fields:
            self.initial["published_at"] = timezone.now().strftime("%Y-%m-%dT%H:%M")
        elif self.instance.pk and self.instance.published_at:
            self.initial["published_at"] = self.instance.published_at.strftime("%Y-%m-%dT%H:%M")

    def clean_published_at(self):
        return self.cleaned_data.get("published_at") or timezone.now()




