from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.static import serve

from apps.public.sitemaps import SITEMAPS
from apps.public import views as public_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),
    path("thanh-vien/", include("apps.member.urls")),
    path("quan-tri/", include("apps.staff.urls")),
    path("api/v1/", include("apps.api.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    path("robots.txt", public_views.robots_txt),
    path("", include("apps.public.urls")),
]

handler404 = "apps.public.views.page_not_found"
handler500 = "apps.public.views.server_error"

if settings.DEBUG:
    urlpatterns += [path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT})]
