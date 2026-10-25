from django.contrib import admin

from . import models

for m in [models.SiteSettings, models.DonationSettings, models.PolicyDocument, models.PolicyVersion,
          models.PolicyAcceptance, models.InterviewRequest, models.ContactMessage, models.DataRequest]:
    admin.site.register(m)


@admin.register(models.DonationAccount)
class DonationAccountAdmin(admin.ModelAdmin):
    """Tài khoản nhận tài trợ chỉ nên được thêm/duyệt qua /quan-tri/tai-tro/ (cần 2 quản trị viên)."""
    list_display = ["bank_name", "account_number", "account_holder", "state", "created_by", "approved_by"]
    readonly_fields = ["state", "created_by", "approved_by", "approved_at"]

    def has_add_permission(self, request):
        return False
