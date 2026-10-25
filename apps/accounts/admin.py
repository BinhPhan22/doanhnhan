from django.contrib import admin

from .models import AccountApplication, RoleChangeRequest, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "full_name", "role", "status", "date_joined"]
    list_filter = ["role", "status", "auth_provider"]
    search_fields = ["email", "full_name"]
    exclude = ["password"]
    readonly_fields = ["last_login", "date_joined", "google_sub", "failed_logins", "locked_until"]


admin.site.register(AccountApplication)
admin.site.register(RoleChangeRequest)
