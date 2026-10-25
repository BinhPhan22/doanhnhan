"""
Bản sửa đổi (revision), nhận quản lý hồ sơ và nhật ký hệ thống.

Mọi thay đổi nội dung doanh nhân / doanh nghiệp đi qua Revision:
- thành viên gửi → status=pending → biên tập viên duyệt → dữ liệu được ghi vào bảng chính;
- biên tập viên sửa trong quản trị → Revision được duyệt ngay (vẫn lưu lịch sử).
"""
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models

from apps.common.validators import document_extensions, max_file_size


class Revision(models.Model):
    class Entity(models.TextChoices):
        PERSON = "person", "Doanh nhân"
        COMPANY = "company", "Doanh nghiệp"

    class Kind(models.TextChoices):
        CREATE = "create", "Hồ sơ mới"
        UPDATE = "update", "Chỉnh sửa"

    class State(models.TextChoices):
        DRAFT = "draft", "Bản nháp"
        PENDING = "pending", "Chờ duyệt"
        NEEDS_INFO = "needs_info", "Cần bổ sung"
        APPROVED = "approved", "Đã duyệt"
        REJECTED = "rejected", "Từ chối"

    entity_type = models.CharField(max_length=10, choices=Entity.choices)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    person = models.ForeignKey("directory.Person", null=True, blank=True, on_delete=models.CASCADE,
                               related_name="revisions")
    company = models.ForeignKey("directory.Company", null=True, blank=True, on_delete=models.CASCADE,
                                related_name="revisions")
    title = models.CharField("Tên hiển thị", max_length=255)
    data = models.JSONField(default=dict)
    previous_data = models.JSONField(default=dict, blank=True)
    checks = models.JSONField(default=list, blank=True)
    note = models.TextField("Ghi chú của người gửi", blank=True)
    state = models.CharField(max_length=12, choices=State.choices, default=State.PENDING)
    revision_no = models.PositiveIntegerField(null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="revisions")
    author_role = models.CharField(max_length=10, default="member")  # owner | member | editor
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name="+")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField("Ghi chú biên tập", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "bản sửa đổi"
        verbose_name_plural = "bản sửa đổi"

    def __str__(self):
        return f"{self.get_kind_display()} · {self.title}"

    @property
    def target(self):
        return self.person if self.entity_type == "person" else self.company

    @property
    def author_label(self):
        return {"owner": "Chính chủ", "editor": "Ban biên tập"}.get(self.author_role, "Thành viên")


private_storage = FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)


class ProfileClaim(models.Model):
    class State(models.TextChoices):
        PENDING = "pending", "Chờ duyệt"
        APPROVED = "approved", "Đã duyệt"
        REJECTED = "rejected", "Từ chối"

    person = models.ForeignKey("directory.Person", on_delete=models.CASCADE, related_name="claims")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="claims")
    evidence = models.FileField("Giấy tờ chứng minh", storage=private_storage, upload_to="claims/%Y/",
                                validators=[document_extensions, max_file_size])
    note = models.TextField("Ghi chú", blank=True)
    state = models.CharField(max_length=10, choices=State.choices, default=State.PENDING)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name="+")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class AuditLog(models.Model):
    """Nhật ký chỉ ghi thêm: ai làm gì, lúc nào."""

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=60)
    target_type = models.CharField(max_length=40, blank=True)
    target_id = models.CharField(max_length=40, blank=True)
    target_label = models.CharField(max_length=255, blank=True)
    detail = models.JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.pk:
            raise RuntimeError("Nhật ký không được sửa.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RuntimeError("Nhật ký không được xóa.")


def log(actor, action, target=None, label="", detail=None, request=None):
    from apps.common.permissions import client_ip

    AuditLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        target_type=type(target).__name__ if target is not None else "",
        target_id=str(getattr(target, "pk", "") or ""),
        target_label=(label or str(target or ""))[:255],
        detail=detail or {},
        ip=client_ip(request) if request else None,
    )
