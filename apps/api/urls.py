from django.urls import path, re_path

from . import views

app_name = "api"

urlpatterns = [
    path("", views.index, name="index"),
    path("openapi.yaml", views.openapi, name="openapi"),
    path("provinces/", views.provinces, name="provinces"),
    path("sectors/", views.sectors, name="sectors"),
    path("sectors/<slug:slug>/", views.sector_detail, name="sector_detail"),
    path("persons/", views.persons, name="persons"),
    path("persons/<slug:slug>/", views.person_detail, name="person_detail"),
    path("companies/", views.companies, name="companies"),
    path("companies/<slug:slug>/", views.company_detail, name="company_detail"),
    path("associations/", views.associations, name="associations"),
    path("associations/<slug:slug>/", views.association_detail, name="association_detail"),
    path("events/", views.events, name="events"),
    path("events/<slug:slug>/", views.event_detail, name="event_detail"),
    path("videos/", views.videos, name="videos"),
    path("search/", views.search, name="search"),
    re_path(r"^(?P<rest>.*)$", views.not_found),
]
