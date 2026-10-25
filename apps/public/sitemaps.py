from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.directory.models import Association, Company, Event, Person, Sector, Story


class StaticSitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        return [
            "public:home", "public:person_list", "public:story_list", "public:event_list",
            "public:podcast_list", "public:video_list", "public:association_list",
            "public:company_list", "public:sector_list", "public:donate", "public:contact",
        ]

    def location(self, item):
        return reverse(item)


class ModelSitemap(Sitemap):
    changefreq = "weekly"

    def __init__(self, model, published=True):
        self.model, self.published = model, published

    def items(self):
        qs = self.model.objects.all()
        return qs.filter(status="published") if self.published else qs.filter(is_active=True, parent__isnull=True)

    def lastmod(self, obj):
        return getattr(obj, "updated_at", None)


SITEMAPS = {
    "static": StaticSitemap,
    "story": ModelSitemap(Story),
    "doanh-nhan": ModelSitemap(Person),
    "doanh-nghiep": ModelSitemap(Company),
    "hiep-hoi": ModelSitemap(Association),
    "su-kien": ModelSitemap(Event),
    "nganh-nghe": ModelSitemap(Sector, published=False),
}
