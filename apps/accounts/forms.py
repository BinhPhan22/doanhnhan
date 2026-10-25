from django import forms
from django.contrib.auth import password_validation

from apps.common.forms import StyledFormMixin

from .models import AccountApplication, User


class SignupForm(StyledFormMixin, forms.Form):
    full_name = forms.CharField(label="Họ và tên", max_length=150,
                                widget=forms.TextInput(attrs={"autocomplete": "name"}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    phone = forms.CharField(label="Số điện thoại", max_length=30,
                            widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}))
    password1 = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput(
        attrs={"autocomplete": "new-password", "minlength": 8, "data-password": ""}),
        help_text="Tối thiểu 8 ký tự, không quá phổ biến, không toàn số.")
    password2 = forms.CharField(label="Nhập lại mật khẩu", widget=forms.PasswordInput(
        attrs={"autocomplete": "new-password", "data-password-confirm": ""}))
    applicant_type = forms.ChoiceField(label="Bạn đăng ký với tư cách", choices=AccountApplication.Kind.choices)
    organization = forms.CharField(label="Doanh nghiệp / tổ chức", max_length=200, required=False,
                                   widget=forms.TextInput(attrs={"placeholder": "Tên doanh nghiệp hoặc mã số thuế"}))
    intro = forms.CharField(label="Giới thiệu ngắn", required=False, widget=forms.Textarea(
        attrs={"rows": 3, "placeholder": "Bạn là ai, muốn đưa thông tin gì lên doanhnhan.wiki"}))
    reference_url = forms.URLField(label="Link tham chiếu (website, LinkedIn, bài báo — giúp duyệt nhanh hơn)",
                                   required=False, widget=forms.URLInput(attrs={"placeholder": "https://"}))
    accept_terms = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={"data-required": ""}))
    accept_data = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={"data-required": ""}))
    newsletter = forms.BooleanField(required=False)
    website_hp = forms.CharField(required=False)

    def __init__(self, *args, with_password=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not with_password:
            for name in ("password1", "password2", "email"):
                self.fields.pop(name)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email này đã có tài khoản. Hãy đăng nhập hoặc dùng chức năng quên mật khẩu.")
        return email

    def clean_website_hp(self):
        if self.cleaned_data.get("website_hp"):
            raise forms.ValidationError("Không gửi được đăng ký.")
        return ""

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if "password1" in self.fields and p1:
            if p1 != p2:
                self.add_error("password2", "Mật khẩu nhập lại chưa khớp.")
            else:
                try:
                    password_validation.validate_password(
                        p1, User(email=data.get("email", ""), full_name=data.get("full_name", "")))
                except forms.ValidationError as e:
                    self.add_error("password1", e)
        return data


class LoginForm(StyledFormMixin, forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autocomplete": "email", "autofocus": True}))
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput(
        attrs={"autocomplete": "current-password", "id": "dn-pw"}))
    remember = forms.BooleanField(label="Ghi nhớ đăng nhập trên thiết bị này", required=False, initial=True)


class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ["full_name", "phone", "newsletter"]
