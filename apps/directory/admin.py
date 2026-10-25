from django.contrib import admin

from . import models

admin.site.site_header = "doanhnhan.wiki – Django admin (dành cho kỹ thuật)"


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["full_name", "status", "verification", "is_featured", "is_demo", "updated_at"]
    list_filter = ["status", "verification", "is_demo"]
    search_fields = ["full_name", "search_text"]


@admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["legal_name", "brand_name", "tax_code", "status", "verification", "is_demo"]
    list_filter = ["status", "verification", "is_demo"]
    search_fields = ["legal_name", "brand_name", "tax_code"]


@admin.register(models.Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ["title", "story_type", "author_name", "is_featured", "status", "published_at", "views_count"]
    list_filter = ["story_type", "status", "is_featured"]
    search_fields = ["title", "summary", "author_name"]


for m in [models.Province, models.Sector, models.Association, models.Membership, models.Event, models.EventParticipant,
          models.Video, models.PersonCompany, models.ArticleSection, models.Milestone, models.Source,
          models.CompanyProduct, models.MediaImage, models.AwardBadge, models.PersonAward]:
    admin.site.register(m)

