from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create(self, email, password, **extra):
        if not email:
            raise ValueError("Cần email")
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("status", User.Status.PENDING)
        return self._create(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.update(is_staff=True, is_superuser=True, role=User.Role.ADMIN, status=User.Status.ACTIVE)
        extra.setdefault("full_name", "Quản trị viên")
        return self._create(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        MEMBER = "member", "Thành viên"
        EDITOR = "editor", "Biên tập viên"
        ADMIN = "admin", "Quản trị viên"

    class Status(models.TextChoices):
        PENDING = "pending", "Chờ duyệt"
        ACTIVE = "active", "Đang hoạt động"
        REJECTED = "rejected", "Bị từ chối"
        SUSPENDED = "suspended", "Đã khóa"

    email = models.EmailField("Email", unique=True)
    full_name = models.CharField("Họ và tên", max_length=150)
    phone = models.CharField("Số điện thoại", max_length=30, blank=True)
    role = models.CharField("Vai trò", max_length=10, choices=Role.choices, default=Role.MEMBER)
    status = models.CharField("Trạng thái", max_length=10, choices=Status.choices, default=Status.PENDING)
    auth_provider = models.CharField(max_length=10, default="email")
    google_sub = models.CharField(max_length=64, unique=True, null=True, blank=True)
    newsletter = models.BooleanField("Nhận bản tin", default=False)
    failed_logins = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField("Vào trang Django admin", default=False)
    date_joined = models.DateTimeField("Ngày đăng ký", default=timezone.now)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = "người dùng"
        verbose_name_plural = "người dùng"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    def get_short_name(self):
        return self.full_name.split(" ")[-1] if self.full_name else self.email

    @property
    def is_editor(self):
        return self.is_active and self.status == self.Status.ACTIVE and (
            self.is_superuser or self.role in (self.Role.EDITOR, self.Role.ADMIN)
        )

    @property
    def is_admin_role(self):
        return self.is_active and self.status == self.Status.ACTIVE and (self.is_superuser or self.role == self.Role.ADMIN)

    @property
    def is_locked(self):
        return bool(self.locked_until and self.locked_until > timezone.now())


class AccountApplication(models.Model):
    class Kind(models.TextChoices):
        ENTREPRENEUR = "entrepreneur", "Doanh nhân (tự đưa hồ sơ của mình)"
        COMPANY = "company_rep", "Đại diện doanh nghiệp"
        ASSOCIATION = "association_rep", "Đại diện hiệp hội / chi hội"
        CONTRIBUTOR = "contributor", "Cộng tác viên biên tập"

    class Status(models.TextChoices):
        PENDING = "pending", "Chờ duyệt"
        APPROVED = "approved", "Đã duyệt"
        NEEDS_INFO = "needs_info", "Cần bổ sung"
        REJECTED = "rejected", "Từ chối"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="application")
    applicant_type = models.CharField("Đăng ký với tư cách", max_length=20, choices=Kind.choices)
    organization = models.CharField("Doanh nghiệp / tổ chức", max_length=200, blank=True)
    intro = models.TextField("Giới thiệu ngắn", blank=True)
    reference_url = models.URLField("Link tham chiếu", blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField("Ghi chú duyệt", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "hồ sơ đăng ký tài khoản"
        verbose_name_plural = "hồ sơ đăng ký tài khoản"
        ordering = ["-created_at"]


class RoleChangeRequest(models.Model):
    """Cấp hoặc thu hồi quyền Quản trị viên cần một quản trị viên thứ hai xác nhận."""

    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name="role_requests")
    new_role = models.CharField(max_length=10, choices=User.Role.choices)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    confirmed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    status = models.CharField(max_length=10, default="pending")  # pending | done | cancelled
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
