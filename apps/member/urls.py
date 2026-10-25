from django.urls import path

from . import views

app_name = "member"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("gui/doanh-nhan/", views.person_create, name="person_create"),
    path("gui/doanh-nghiep/", views.company_create, name="company_create"),
    path("de-xuat-sua/doanh-nhan/<slug:slug>/", views.person_edit, name="person_edit"),
    path("de-xuat-sua/doanh-nghiep/<slug:slug>/", views.company_edit, name="company_edit"),
    path("ban-gui/<int:pk>/", views.revision_view, name="revision_view"),
    path("ban-gui/<int:pk>/sua/", views.revision_edit, name="revision_edit"),
    path("ban-gui/<int:pk>/rut/", views.revision_withdraw, name="revision_withdraw"),
    path("nhan-ho-so/<slug:slug>/", views.claim, name="claim"),
    path("anh-cho-duyet/", views.pending_image, name="pending_image"),
]
