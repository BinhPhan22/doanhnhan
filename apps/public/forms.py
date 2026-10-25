from django import forms

from apps.common.forms import StyledFormMixin
from apps.sitecontent.models import ContactMessage, DataRequest, InterviewRequest


class ConsentMixin(forms.Form):
    consent = forms.BooleanField(
        label="Tôi đồng ý để doanhnhan.wiki dùng thông tin trên để liên hệ trao đổi về yêu cầu này.",
        required=True, widget=forms.CheckboxInput(attrs={"data-required": ""}))
    website_hp = forms.CharField(required=False, label="Để trống ô này", widget=forms.TextInput(
        attrs={"tabindex": "-1", "autocomplete": "off"}))  # bẫy spam

    def clean_website_hp(self):
        if self.cleaned_data.get("website_hp"):
            raise forms.ValidationError("Không gửi được yêu cầu.")
        return ""


class InterviewForm(StyledFormMixin, forms.ModelForm, ConsentMixin):
    preferred_time = forms.DateTimeField(
        label="Thời gian thuận tiện",
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]
    )

    class Meta:
        model = InterviewRequest
        fields = ["full_name", "title", "company", "phone", "email", "kind", "story", "format", "address", "preferred_time",
                  "reference_url"]
        widgets = {
            "story": forms.Textarea(attrs={"rows": 4, "placeholder": "Hành trình khởi nghiệp, sản phẩm, dấu mốc, bài học…"}),
            "title": forms.TextInput(attrs={"placeholder": "Nhà sáng lập, CEO…"}),
            "address": forms.TextInput(attrs={"placeholder": "Địa chỉ cụ thể (văn phòng, nhà máy, địa điểm sự kiện...) để Ban quản trị khảo sát"}),
            "reference_url": forms.URLInput(attrs={"placeholder": "https://"}),
            "phone": forms.TextInput(attrs={"type": "tel", "autocomplete": "tel", "placeholder": "Ví dụ: 0912 345 678"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fmt = (self.data.get("format") if self.is_bound else self.initial.get("format")) or ""
        if not self.is_bound and not fmt:
            fmt = InterviewRequest.Format.ONSITE
        if fmt and fmt != InterviewRequest.Format.ONLINE:
            self.fields["address"].required = True
            self.fields["address"].error_messages["required"] = (
                "Vui lòng nhập địa chỉ dự kiến ghi hình để Ban quản trị xem xét và xác nhận khả năng thực hiện."
            )
        else:
            self.fields["address"].required = False

    def clean(self):
        cleaned_data = super().clean()
        fmt = cleaned_data.get("format")
        address = (cleaned_data.get("address") or "").strip()
        if fmt and fmt != InterviewRequest.Format.ONLINE and not address:
            if "address" not in self.errors:
                self.add_error("address", "Vui lòng nhập địa chỉ dự kiến ghi hình để Ban quản trị xem xét và xác nhận khả năng thực hiện.")
        return cleaned_data


import re


class ContactForm(StyledFormMixin, forms.ModelForm, ConsentMixin):
    class Meta:
        model = ContactMessage
        fields = ["topic", "full_name", "organization", "email", "phone", "source_url", "message"]
        widgets = {
            "source_url": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Nhập một hoặc nhiều đường link đối chiếu, kiểm chứng (mỗi link một hàng hoặc cách nhau bằng dấu phẩy)...",
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "Ví dụ: 0912 345 678",
                "type": "tel",
                "autocomplete": "tel",
            }),
            "message": forms.Textarea(attrs={"rows": 5}),
        }
        help_texts = {
            "source_url": "",
            "phone": "",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].required = True
        topic = (self.data.get("topic") if self.is_bound else self.initial.get("topic")) or ""
        if topic == "correction":
            self.fields["source_url"].required = True
            self.fields["source_url"].error_messages["required"] = (
                "Vui lòng cung cấp đường link nguồn (bài báo, cổng ĐKKD, quyết định...) để Ban biên tập đối chiếu và xác nhận thông tin."
            )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        cleaned = re.sub(r"[\s\.\-\(\)]", "", phone)
        if len(cleaned) < 9 or not re.match(r"^(\+?84|0)\d{8,11}$", cleaned):
            raise forms.ValidationError("Vui lòng nhập số điện thoại hợp lệ (từ 9 đến 11 chữ số) để Ban biên tập liên hệ xác minh.")
        return phone


class DataRequestForm(StyledFormMixin, forms.ModelForm, ConsentMixin):
    class Meta:
        model = DataRequest
        fields = ["kind", "full_name", "email", "profile_url", "detail"]
        widgets = {"detail": forms.Textarea(attrs={"rows": 5}),
                   "profile_url": forms.TextInput(attrs={"placeholder": "https://doanhnhan.wiki/doanh-nhan/…"})}
