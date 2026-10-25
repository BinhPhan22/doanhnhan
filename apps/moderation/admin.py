from django.contrib import admin

from .models import AuditLog, ProfileClaim, Revision


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ["title", "entity_type", "kind", "state", "author", "created_at"]
    list_filter = ["state", "entity_type", "kind"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "actor", "action", "target_type", "target_label"]
    list_filter = ["action"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.register(ProfileClaim)
