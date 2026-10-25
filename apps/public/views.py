"""Trang công khai: ai cũng xem được, không cần tài khoản."""
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, F, Prefetch, Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from apps.common.notify import notify_editors
from apps.common.permissions import admin_required, is_editor
from apps.common.text import normalize
from apps.directory.models import (
    Association, AwardBadge, Company, CompanyAward, Event, EventParticipant, Membership, Person, PersonAward,
    PersonCompany, Podcast, Postcard, Province, Sector, Status, Story, Video, visible_videos,
)
from apps.moderation.models import Revision, log
from apps.sitecontent.models import DonationAccount, DonationSettings, PolicyDocument, SiteSettings

from .forms import ContactForm, DataRequestForm, InterviewForm

PER_PAGE = 12


def _page(request, qs, per_page=PER_PAGE):
    return Paginator(qs, per_page).get_page(request.GET.get("trang"))


def _people_qs():
    return (Person.objects.published()
            .select_related("current_province")
            .prefetch_related(Prefetch("company_links", queryset=PersonCompany.objects.select_related("company")),
                              Prefetch("awards", queryset=PersonAward.objects.select_related("badge")),
                              "sections")
            .annotate(source_count=Count("sources", distinct=True)))


def _visible(model, slug, request, **filters):
    obj = get_object_or_404(model, slug=slug, **filters)
    if obj.status != Status.PUBLISHED and not is_editor(request.user):
        owner_id = getattr(obj, "owner_id", None)
        if not (request.user.is_authenticated and owner_id and owner_id == request.user.pk):
            raise Http404
    return obj


# --------------------------------------------------------------------------- trang chủ
def home(request):
    people = _people_qs()
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    sectors = (Sector.objects.filter(parent__isnull=True, is_active=True)
               .annotate(person_count=Count("companies__person_links__person",
                                            filter=Q(companies__person_links__person__status=Status.PUBLISHED),
                                            distinct=True)))
    # Xếp hạng bài hot/nổi bật: ưu tiên ghim (is_featured), sau đó đến likes và views
    ctx = {
        "featured": list(people.order_by("-is_featured", "-likes_count", "-views_count", "-updated_at")[:8]),
        "newest": list(people.order_by("-published_at")[:8]),
        "updated": list(people.order_by("-updated_at")[:8]),
        "events": list(Event.objects.filter(status=Event.EventStatus.PUBLISHED)
                       .select_related("province", "organizer")
                       .annotate(participant_count=Count("participants", distinct=True))
                       .order_by("-is_featured", "-likes_count", "starts_at")[:8]),
        "stories": list(Story.objects.filter(status=Status.PUBLISHED)
                        .select_related("featured_person", "featured_company")
                        .order_by("-is_featured", "-likes_count", "-views_count", "-published_at")[:8]),
        "podcasts": list(Podcast.objects.filter(status=Status.PUBLISHED)
                         .select_related("guest_person", "company")
                         .order_by("-is_featured", "-likes_count", "-views_count", "-published_at")[:8]),
        "stats": {
            "persons": Person.objects.published().count(),
            "companies": Company.objects.published().count(),
            "sectors": Sector.objects.filter(is_active=True).count(),
            "updates": Revision.objects.filter(state="approved", reviewed_at__gte=month_start).count(),
        },
        "sectors": sectors,
        "recent": (Revision.objects.filter(state="approved")
                   .filter(Q(person__status=Status.PUBLISHED) | Q(company__status=Status.PUBLISHED))
                   .select_related("person", "company").order_by("-reviewed_at")[:6]),
        "videos": visible_videos().prefetch_related("persons", "companies", "events")[:6],
        "provinces": Province.objects.all(),
        "upcoming": Event.objects.filter(status="published", starts_at__gte=timezone.now()).order_by("starts_at")[:3],
    }
    return render(request, "public/home.html", ctx)


# --------------------------------------------------------------------------- doanh nhân
def person_list(request):
    qs = _people_qs()
    q = request.GET.get("q", "").strip()
    sector = Sector.objects.filter(slug=request.GET.get("nganh")).first()
    province = Province.objects.filter(code=request.GET.get("tinh")).first()
    badge = AwardBadge.objects.filter(code=request.GET.get("danh-hieu")).first()
    if q:
        qs = qs.search(q)
    if sector:
        qs = qs.filter(company_links__company__sectors__in=sector.family_ids()).distinct()
    if province:
        qs = qs.filter(current_province=province)
    if badge:
        qs = qs.filter(awards__badge=badge).distinct()
    if request.GET.get("xac-minh"):
        qs = qs.exclude(verification="none")
    sort = request.GET.get("sap-xep", "cap-nhat")
    qs = qs.order_by({"ten": "full_name", "moi": "-published_at"}.get(sort, "-updated_at"))
    return render(request, "public/person_list.html", {
        "page": _page(request, qs), "q": q, "sector": sector, "province": province, "sort": sort,
        "sectors": Sector.objects.filter(parent__isnull=True, is_active=True),
        "provinces": Province.objects.all(),
        "badges": AwardBadge.objects.all().order_by("sort_order", "name"),
        "selected_badge": badge,
    })


def person_detail(request, slug):
    person = _visible(Person, slug, request)
    person = (Person.objects.select_related("hometown", "current_province", "owner")
              .prefetch_related("sections", "milestones", "sources",
                                Prefetch("awards", queryset=PersonAward.objects.select_related("badge")),
                                Prefetch("company_links", queryset=PersonCompany.objects.select_related(
                                    "company", "company__primary_sector", "company__province")),
                                Prefetch("memberships", queryset=Membership.objects.filter(state="confirmed")
                                         .select_related("association")),
                                Prefetch("event_participations", queryset=EventParticipant.objects
                                         .select_related("event").order_by("-event__starts_at")))
              .get(pk=person.pk))
    sections = {s.key: s for s in person.sections.all()}
    last_rev = person.revisions.filter(state="approved").order_by("-reviewed_at").first()
    pct, checks = person.completeness()
    can_claim = (request.user.is_authenticated and person.owner_id is None
                 and not person.claims.filter(user=request.user, state="pending").exists())
    return render(request, "public/person_detail.html", {
        "person": person, "sections": sections, "last_rev": last_rev,
        "completeness": pct, "missing": [label for label, ok in checks if not ok],
        "videos": visible_videos().filter(persons=person).distinct(),
        "sectors": person.sectors(), "can_claim": can_claim,
        "pending_mine": request.user.is_authenticated and person.revisions.filter(
            author=request.user, state="pending").exists(),
    })


@admin_required
def person_reveal_phone(request, pk):
    """Chỉ Quản trị viên (Admin) mới có quyền mở xem số điện thoại bảo mật."""
    person = get_object_or_404(Person, pk=pk)
    phone = person.display_phone
    if not phone:
        return JsonResponse({"status": "empty", "phone": "", "masked": ""})
    log(request.user, "person.reveal_phone", person, f"Quản trị viên mở xem số điện thoại bảo mật của {person.full_name}", request=request)
    return JsonResponse({"status": "ok", "phone": phone, "masked": person.masked_phone})


def person_history(request, slug):
    person = _visible(Person, slug, request)
    revisions = person.revisions.filter(state="approved").select_related("reviewer").order_by("-revision_no")
    return render(request, "public/history.html", {"entity": person, "kind": "person", "revisions": revisions})


def person_og_image(request, slug):
    """Ảnh OpenGraph (1200x630 PNG) động tạo tự động cho chia sẻ mạng xã hội."""
    person = _visible(Person, slug, request)
    from .og import generate_person_og_image
    png_data = generate_person_og_image(person)
    response = HttpResponse(png_data, content_type="image/png")
    response["Cache-Control"] = "public, max-age=86400"
    return response


def person_print(request, slug):
    """Trang in ấn / xuất file PDF hồ sơ chuẩn A4."""
    person = _visible(Person, slug, request)
    person = (Person.objects.select_related("hometown", "current_province")
              .prefetch_related("sections", "milestones", "sources",
                                Prefetch("awards", queryset=PersonAward.objects.select_related("badge")),
                                Prefetch("company_links", queryset=PersonCompany.objects.select_related(
                                    "company", "company__province", "company__primary_sector")
                                         .filter(company__status=Status.PUBLISHED)))
              .get(pk=person.pk))
    return render(request, "public/person_print.html", {
        "person": person,
        "sections": {s.key: s for s in person.sections.all()},
        "primary_link": person.primary_link,
        "print_now": request.GET.get("in") == "1",
    })


# --------------------------------------------------------------------------- doanh nghiệp
def company_list(request):
    qs = (Company.objects.published().select_related("province", "primary_sector")
          .prefetch_related(Prefetch("person_links", queryset=PersonCompany.objects.select_related("person")
                                     .filter(person__status=Status.PUBLISHED))))
    q = request.GET.get("q", "").strip()
    sector = Sector.objects.filter(slug=request.GET.get("nganh")).first()
    province = Province.objects.filter(code=request.GET.get("tinh")).first()
    badge = AwardBadge.objects.filter(code=request.GET.get("danh-hieu")).first()
    sizes = [s for s in request.GET.getlist("quy-mo") if s in Company.Size.values]
    year_from, year_to = request.GET.get("tu", ""), request.GET.get("den", "")
    if q:
        qs = qs.search(q)
    if sector:
        qs = qs.filter(sectors__in=sector.family_ids()).distinct()
    if province:
        qs = qs.filter(province=province)
    if badge:
        qs = qs.filter(awards__badge=badge).distinct()
    if sizes:
        qs = qs.filter(size_band__in=sizes)
    if year_from.isdigit():
        qs = qs.filter(founded_year__gte=int(year_from))
    if year_to.isdigit():
        qs = qs.filter(founded_year__lte=int(year_to))
    if request.GET.get("xac-minh"):
        qs = qs.exclude(verification="none")
    sort = request.GET.get("sap-xep", "cap-nhat")
    qs = qs.order_by({"ten": "legal_name", "nam": "founded_year"}.get(sort, "-updated_at"))
    page = _page(request, qs, 20)
    return render(request, "public/company_list.html", {
        "page": page, "q": q, "sector": sector, "province": province, "sizes": sizes, "sort": sort,
        "year_from": year_from, "year_to": year_to, "size_choices": Company.Size.choices,
        "sectors": Sector.objects.filter(parent__isnull=True, is_active=True), "provinces": Province.objects.all(),
        "badges": AwardBadge.objects.all().order_by("sort_order", "name"),
        "selected_badge": badge,
    })


def company_detail(request, slug):
    company = _visible(Company, slug, request)
    company = (Company.objects.select_related("province", "primary_sector", "primary_sector__parent")
               .prefetch_related("sections", "milestones", "sources", "products", "sectors",
                                 Prefetch("awards", queryset=CompanyAward.objects.select_related("badge")),
                                 Prefetch("person_links", queryset=PersonCompany.objects.select_related("person")
                                          .filter(person__status=Status.PUBLISHED)))
               .get(pk=company.pk))
    return render(request, "public/company_detail.html", {
        "company": company, "sections": {s.key: s for s in company.sections.all()},
        "last_rev": company.revisions.filter(state="approved").order_by("-reviewed_at").first(),
        "videos": visible_videos().filter(companies=company).distinct(),
        "founders": [l for l in company.person_links.all() if l.role in ("founder", "founder_ceo", "cofounder")],
    })


def company_history(request, slug):
    company = _visible(Company, slug, request)
    revisions = company.revisions.filter(state="approved").select_related("reviewer").order_by("-revision_no")
    return render(request, "public/history.html", {"entity": company, "kind": "company", "revisions": revisions})


def company_og_image(request, slug):
    """Ảnh OpenGraph (1200x630 PNG) động tạo tự động cho doanh nghiệp khi chia sẻ mạng xã hội."""
    company = _visible(Company, slug, request)
    from .og import generate_company_og_image
    png_data = generate_company_og_image(company)
    response = HttpResponse(png_data, content_type="image/png")
    response["Cache-Control"] = "public, max-age=86400"
    return response


def default_og_image(request):
    """Ảnh OpenGraph mặc định (1200x630 PNG) chuẩn nhận diện thương hiệu cho toàn trang web."""
    from .og import generate_default_og_image
    png_data = generate_default_og_image()
    response = HttpResponse(png_data, content_type="image/png")
    response["Cache-Control"] = "public, max-age=86400"
    return response



# --------------------------------------------------------------------------- story (câu chuyện & phóng sự)
def story_list(request):
    qs = (Story.objects.filter(status=Status.PUBLISHED)
          .select_related("featured_person", "featured_company", "featured_event"))
    story_type = request.GET.get("loai", "").strip()
    if story_type in Story.StoryType.values:
        qs = qs.filter(story_type=story_type)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.search(q)

    # Bài viết tiêu điểm (Featured Hero)
    featured = qs.filter(is_featured=True).first()
    if not featured and not story_type and not q:
        featured = qs.first()

    other_qs = qs.exclude(pk=featured.pk) if featured else qs
    page = _page(request, other_qs, per_page=12)

    story_type_label = dict(Story.StoryType.choices).get(story_type, "")

    return render(request, "public/story_list.html", {
        "page": page,
        "featured": featured,
        "story_type": story_type,
        "story_type_label": story_type_label,
        "story_types": Story.StoryType.choices,
        "q": q,
        "total_count": qs.count(),
    })


def story_detail(request, slug):
    story = get_object_or_404(
        Story.objects.select_related("featured_person", "featured_company", "featured_event"),
        slug=slug
    )
    if story.status != Status.PUBLISHED and not is_editor(request.user):
        raise Http404

    # Tăng lượt xem
    Story.objects.filter(pk=story.pk).update(views_count=story.views_count + 1)
    story.views_count += 1

    # Bài viết liên quan
    related_stories = (Story.objects.filter(status=Status.PUBLISHED)
                       .exclude(pk=story.pk)
                       .select_related("featured_person", "featured_company")
                       .order_by("-is_featured", "-published_at")[:4])

    return render(request, "public/story_detail.html", {
        "story": story,
        "related_stories": related_stories,
    })


# --------------------------------------------------------------------------- postcard (bưu thiếp danh ngôn & triết lý kinh doanh)
def postcard_list(request):
    qs = (Postcard.objects.filter(status=Status.PUBLISHED)
          .select_related("person", "company"))
    topic = request.GET.get("chu-de", "").strip()
    if topic in Postcard.Topic.values:
        qs = qs.filter(topic=topic)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.search(q)

    person_slug = request.GET.get("doanh-nhan", "").strip()
    selected_person = None
    if person_slug:
        selected_person = Person.objects.filter(slug=person_slug).first()
        if selected_person:
            qs = qs.filter(person=selected_person)

    total_count = qs.count()
    page = _page(request, qs, per_page=12)
    topic_label = dict(Postcard.Topic.choices).get(topic, "")

    return render(request, "public/postcard_list.html", {
        "page": page,
        "topic": topic,
        "topic_label": topic_label,
        "topics": Postcard.Topic.choices,
        "q": q,
        "selected_person": selected_person,
        "total_count": total_count,
    })


def postcard_detail(request, slug):
    postcard = get_object_or_404(
        Postcard.objects.select_related("person", "company"),
        slug=slug
    )
    if postcard.status != Status.PUBLISHED and not is_editor(request.user):
        raise Http404

    # Tăng lượt xem
    Postcard.objects.filter(pk=postcard.pk).update(views_count=postcard.views_count + 1)
    postcard.views_count += 1

    related_postcards = (Postcard.objects.filter(status=Status.PUBLISHED)
                         .exclude(pk=postcard.pk)
                         .select_related("person", "company")
                         .filter(topic=postcard.topic)[:4])

    return render(request, "public/postcard_detail.html", {
        "postcard": postcard,
        "related_postcards": related_postcards,
    })


def postcard_download(request, slug):
    postcard = get_object_or_404(Postcard, slug=slug)
    if postcard.status != Status.PUBLISHED and not is_editor(request.user):
        raise Http404

    # Tăng lượt tải
    Postcard.objects.filter(pk=postcard.pk).update(downloads_count=postcard.downloads_count + 1)

    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("format") == "json":
        return JsonResponse({"status": "ok", "downloads_count": postcard.downloads_count + 1})

    if postcard.image:
        return redirect(postcard.image.url)
    return redirect("public:postcard_detail", slug=postcard.slug)


# --------------------------------------------------------------------------- podcast (chương trình phát thanh, đối thoại doanh nhân)
def podcast_list(request):
    qs = (Podcast.objects.filter(status=Status.PUBLISHED)
          .select_related("guest_person", "company"))
    series = request.GET.get("chu-de", "").strip()
    if series in Podcast.SeriesType.values:
        qs = qs.filter(series_type=series)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.search(q)

    person_slug = request.GET.get("doanh-nhan", "").strip()
    selected_person = None
    if person_slug:
        selected_person = Person.objects.filter(slug=person_slug).first()
        if selected_person:
            qs = qs.filter(guest_person=selected_person)

    # Tập tiêu điểm (Featured)
    featured = qs.filter(is_featured=True).first()
    if not featured and not series and not q and not selected_person:
        featured = qs.first()

    other_qs = qs.exclude(pk=featured.pk) if featured else qs
    page = _page(request, other_qs, per_page=12)
    series_label = dict(Podcast.SeriesType.choices).get(series, "")

    return render(request, "public/podcast_list.html", {
        "page": page,
        "featured": featured,
        "series": series,
        "series_label": series_label,
        "series_types": Podcast.SeriesType.choices,
        "q": q,
        "selected_person": selected_person,
        "total_count": qs.count(),
    })


def podcast_detail(request, slug):
    podcast = get_object_or_404(
        Podcast.objects.select_related("guest_person", "company"),
        slug=slug
    )
    if podcast.status != Status.PUBLISHED and not is_editor(request.user):
        raise Http404

    # Tăng lượt xem
    Podcast.objects.filter(pk=podcast.pk).update(views_count=podcast.views_count + 1)
    podcast.views_count += 1

    related_podcasts = (Podcast.objects.filter(status=Status.PUBLISHED)
                        .exclude(pk=podcast.pk)
                        .select_related("guest_person", "company")
                        .filter(series_type=podcast.series_type)[:4])

    return render(request, "public/podcast_detail.html", {
        "podcast": podcast,
        "related_podcasts": related_podcasts,
    })


def podcast_track_play(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug)
    if podcast.status != Status.PUBLISHED and not is_editor(request.user):
        raise Http404

    Podcast.objects.filter(pk=podcast.pk).update(listeners_count=podcast.listeners_count + 1)
    return JsonResponse({"status": "ok", "listeners_count": podcast.listeners_count + 1})


# --------------------------------------------------------------------------- ngành nghề
def sector_list(request):
    sectors = (Sector.objects.filter(parent__isnull=True, is_active=True)
               .prefetch_related(Prefetch("children", queryset=Sector.objects.filter(is_active=True)))
               .annotate(person_count=Count("companies__person_links__person",
                                            filter=Q(companies__person_links__person__status=Status.PUBLISHED),
                                            distinct=True),
                         company_count=Count("companies", filter=Q(companies__status=Status.PUBLISHED),
                                             distinct=True)))
    return render(request, "public/sector_list.html", {"sectors": sectors})


def sector_detail(request, slug):
    sector = get_object_or_404(Sector, slug=slug, parent__isnull=True)
    children = list(sector.children.filter(is_active=True))
    child = next((c for c in children if c.slug == request.GET.get("phan-nganh")), None)
    ids = [child.pk] if child else sector.family_ids()
    companies = (Company.objects.published().filter(sectors__in=ids).distinct()
                 .select_related("province", "primary_sector")
                 .prefetch_related(Prefetch("person_links", queryset=PersonCompany.objects.select_related("person")
                                            .filter(person__status=Status.PUBLISHED))))
    people = (_people_qs().filter(company_links__company__in=companies).distinct()
              .order_by("-is_featured", "-updated_at"))
    provinces = (companies.exclude(province__isnull=True).values("province__name", "province__code")
                 .annotate(n=Count("pk", distinct=True)).order_by("-n"))
    provinces = list(provinces[:6])
    top = provinces[0]["n"] if provinces else 1
    for p in provinces:
        p["pct"] = round(p["n"] * 100 / top)
    return render(request, "public/sector_detail.html", {
        "sector": sector, "children": children, "child": child,
        "people": people[:12], "people_count": people.count(),
        "companies": companies.order_by("legal_name")[:50], "company_count": companies.count(),
        "province_count": companies.exclude(province__isnull=True).values("province").distinct().count(),
        "provinces": provinces,
        "associations": Association.objects.published().filter(sectors__in=sector.family_ids()).distinct()[:6],
        "events": Event.objects.filter(status="published", starts_at__gte=timezone.now(),
                                       sectors__in=sector.family_ids()).distinct().order_by("starts_at")[:3],
    })


# --------------------------------------------------------------------------- hiệp hội
def association_list(request):
    qs = (Association.objects.published().select_related("province")
          .annotate(member_count=Count("memberships", filter=Q(memberships__state="confirmed",
                                                               memberships__person__status=Status.PUBLISHED),
                                       distinct=True)))
    level = request.GET.get("loai", "").strip()
    if level in Association.Level.values:
        qs = qs.filter(level=level)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.search(q)

    page = _page(request, qs.order_by("-is_partner", "name"), per_page=12)
    leaders = {m.association_id: m for m in Membership.objects.filter(
        association__in=page.object_list, is_leadership=True, state="confirmed").select_related("person")
        .order_by("sort_order")}
    for a in page.object_list:
        a.leader = leaders.get(a.pk)

    level_label = dict(Association.Level.choices).get(level, "")
    return render(request, "public/association_list.html", {
        "page": page,
        "associations": page.object_list,
        "q": q,
        "level": level,
        "level_label": level_label,
        "levels": Association.Level.choices,
        "total_count": qs.count(),
    })


def association_detail(request, slug):
    association = get_object_or_404(Association.objects.select_related("province", "parent"), slug=slug)
    if association.status != Status.PUBLISHED and not is_editor(request.user):
        raise Http404
    members = (association.memberships.filter(state="confirmed", person__status=Status.PUBLISHED)
               .select_related("person").prefetch_related(
                   Prefetch("person__company_links", queryset=PersonCompany.objects.select_related("company"))))
    return render(request, "public/association_detail.html", {
        "association": association,
        "leadership": [m for m in members if m.is_leadership],
        "members": _page(request, members.filter(is_leadership=False), 30),
        "member_count": members.count(),
        "children": association.children.filter(status=Status.PUBLISHED),
        "upcoming": association.events.filter(status="published", starts_at__gte=timezone.now()).order_by("starts_at"),
        "past": association.events.filter(status="published", starts_at__lt=timezone.now()).order_by("-starts_at")[:10],
        "videos": visible_videos().filter(associations=association).distinct()[:6],
    })


# --------------------------------------------------------------------------- sự kiện
def event_list(request):
    now = timezone.now()
    qs = (Event.objects.filter(status__in=["published", "cancelled"]).select_related("organizer", "province")
          .annotate(participant_count=Count("participants", distinct=True),
                    video_count=Count("videos", filter=Q(videos__status="published"), distinct=True))
          .prefetch_related(Prefetch("participants", queryset=EventParticipant.objects.select_related("person"))))

    time_filter = request.GET.get("thoi-gian", "all").strip()
    if time_filter == "upcoming":
        qs = qs.filter(Q(ends_at__gte=now) | Q(ends_at__isnull=True, starts_at__gte=now)).order_by("starts_at")
    elif time_filter == "past":
        qs = qs.filter(Q(ends_at__lt=now) | Q(ends_at__isnull=True, starts_at__lt=now)).order_by("-starts_at")
    else:
        qs = qs.order_by("-is_featured", "-starts_at")

    kind = request.GET.get("loai", "").strip()
    if kind in Event.Kind.values:
        qs = qs.filter(kind=kind)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.search(q)

    featured = qs.filter(is_featured=True).first()
    if not featured and not kind and not q and time_filter == "all":
        featured = qs.first()

    other_qs = qs.exclude(pk=featured.pk) if featured else qs
    page = _page(request, other_qs, per_page=12)
    kind_label = dict(Event.Kind.choices).get(kind, "")

    upcoming_count = Event.objects.filter(status="published").filter(
        Q(ends_at__gte=now) | Q(ends_at__isnull=True, starts_at__gte=now)
    ).count()
    past_count = Event.objects.filter(status="published").filter(
        Q(ends_at__lt=now) | Q(ends_at__isnull=True, starts_at__lt=now)
    ).count()

    return render(request, "public/event_list.html", {
        "page": page,
        "events": page.object_list,
        "featured": featured,
        "time_filter": time_filter,
        "kind": kind,
        "kind_label": kind_label,
        "kinds": Event.Kind.choices,
        "q": q,
        "total_count": qs.count(),
        "upcoming_count": upcoming_count,
        "past_count": past_count,
    })


def event_detail(request, slug):
    event = get_object_or_404(Event.objects.select_related("organizer", "province"), slug=slug)
    if event.status in ("draft", "archived") and not is_editor(request.user):
        raise Http404
    participants = (event.participants.filter(person__status=Status.PUBLISHED).select_related("person")
                    .prefetch_related(Prefetch("person__company_links",
                                               queryset=PersonCompany.objects.select_related("company"))))
    groups = {}
    for p in participants:
        groups.setdefault(p.get_role_display(), []).append(p)
    return render(request, "public/event_detail.html", {
        "event": event, "groups": groups, "videos": visible_videos().filter(events=event).distinct(),
        "sectors": event.sectors.all(),
    })


# --------------------------------------------------------------------------- video
def video_list(request):
    qs = visible_videos().prefetch_related("persons", "companies", "events")
    kind = request.GET.get("loai", "").strip()
    if kind:
        qs = qs.filter(kind=kind)
    q = request.GET.get("q", "").strip()
    sector = Sector.objects.filter(slug=request.GET.get("nganh")).first()
    if q:
        key = normalize(q)
        qs = qs.filter(Q(search_text__contains=key) | Q(persons__search_text__contains=key)
                       | Q(companies__search_text__contains=key)).distinct()
    if sector:
        ids = sector.family_ids()
        qs = qs.filter(Q(companies__sectors__in=ids) | Q(persons__company_links__company__sectors__in=ids)).distinct()

    current = None
    if request.GET.get("v", "").isdigit():
        current = visible_videos().filter(pk=int(request.GET["v"])).prefetch_related("persons", "companies", "events").first()
    if current is None:
        current = qs.filter(is_featured=True).first() or qs.first()

    page = _page(request, qs, per_page=12)
    return render(request, "public/video_list.html", {
        "page": page,
        "videos": page.object_list,
        "current": current,
        "q": q,
        "kind": kind,
        "sector": sector,
        "sectors": Sector.objects.filter(parent__isnull=True, is_active=True),
        "total_count": qs.count(),
    })


# --------------------------------------------------------------------------- tìm kiếm chung
def search(request):
    q = request.GET.get("q", "").strip()
    ctx = {"q": q}
    if q:
        ctx.update({
            "people": _people_qs().search(q)[:20],
            "companies": Company.objects.published().search(q).select_related("province")[:20],
            "associations": Association.objects.published().search(q)[:10],
            "events": Event.objects.filter(status="published").search(q)[:10],
            "videos": visible_videos().filter(search_text__contains=normalize(q))[:8],
            "sectors": Sector.objects.filter(is_active=True).search(q)[:8],
        })
        ctx["total"] = sum(len(ctx[k]) for k in ("people", "companies", "associations", "events", "videos", "sectors"))
    return render(request, "public/search.html", ctx)


@require_GET
def suggest(request):
    """Gợi ý tên khi nhập liệu hoặc thanh tìm kiếm: /api/goi-y/?loai=company|person&q=…"""
    from apps.moderation.services import company_label, person_label

    q = request.GET.get("q", "").strip()
    kind = request.GET.get("loai")
    results = []
    if len(q) >= 2:
        if kind == "company":
            qs = Company.objects.search(q)
            if not is_editor(request.user):
                qs = qs.published()
            results = [{"id": c.pk, "label": company_label(c), "name": c.display_name, "tax_code": c.tax_code or "", "url": c.get_absolute_url()} for c in qs[:10]]
        elif kind == "person":
            qs = Person.objects.search(q)
            if not is_editor(request.user):
                qs = qs.published()
            results = [{"id": p.pk, "label": person_label(p), "url": p.get_absolute_url()} for p in qs[:10]]
        else:
            # Gợi ý tìm kiếm tức thì cho thanh tìm kiếm chung (omnisearch)
            p_qs = (_people_qs().search(q))[:5]
            c_qs = (Company.objects.published().search(q).select_related("province", "primary_sector"))[:5]
            for p in p_qs:
                first_award = p.awards.first()
                results.append({
                    "id": p.pk,
                    "type": "person",
                    "type_label": "Doanh nhân",
                    "title": p.full_name,
                    "subtitle": p.headline or (p.current_province.name if p.current_province else "Doanh nhân"),
                    "url": p.get_absolute_url(),
                    "image": p.portrait.url if p.portrait else None,
                    "initials": p.initials,
                    "badge": first_award.badge.name if first_award else None,
                })
            for c in c_qs:
                sub = c.brand_name or (c.primary_sector.name if c.primary_sector else "")
                if c.province:
                    sub = f"{sub} · {c.province.name}" if sub else c.province.name
                results.append({
                    "id": c.pk,
                    "type": "company",
                    "type_label": "Doanh nghiệp",
                    "title": c.display_name,
                    "subtitle": sub or c.legal_name,
                    "url": c.get_absolute_url(),
                    "image": c.logo.url if c.logo else None,
                    "initials": c.initials,
                    "badge": f"MST {c.tax_code}" if c.tax_code else None,
                })
    return JsonResponse({"results": results})


# --------------------------------------------------------------------------- trang nội dung
def donate(request):
    return render(request, "public/donate.html", {
        "donation": DonationSettings.load(),
        "accounts": DonationAccount.objects.filter(state=DonationAccount.State.ACTIVE),
    })


def about(request):
    return render(request, "public/about.html", {"site": SiteSettings.load()})


def policy_index(request):
    first = PolicyDocument.objects.first()
    if not first:
        raise Http404
    return redirect("public:policy_detail", code=first.code)


def policy_detail(request, code):
    document = get_object_or_404(PolicyDocument, code=code)
    versions = document.versions.filter(status="published", effective_at__lte=timezone.now())
    version = None
    if request.GET.get("phien-ban"):
        version = versions.filter(version=request.GET["phien-ban"]).first()
    current = document.current_version()
    version = version or current
    return render(request, "public/policy.html", {
        "documents": PolicyDocument.objects.all(), "document": document, "version": version,
        "current": current, "versions": versions,
        "scheduled": document.versions.filter(status="published", effective_at__gt=timezone.now()).first(),
    })


def _simple_form(request, form_class, template, *, notify_subject, notify_template, initial=None, extra=None):
    form = form_class(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        notify_editors(notify_subject, notify_template, {"obj": obj})
        return render(request, template, {"done": True, "obj": obj, **(extra or {})})
    return render(request, template, {"form": form, **(extra or {})})


def contact(request):
    return _simple_form(request, InterviewForm, "public/contact.html",
                        notify_subject="Yêu cầu ghi hình, phỏng vấn mới", notify_template="staff_new_interview")


def feedback(request):
    topic = request.GET.get("chu-de", "other")
    target = request.GET.get("doi-tuong", "").strip()
    initial = {"topic": topic}
    if target:
        initial["message"] = f"Góp ý về hồ sơ: {target}\nNội dung cần điều chỉnh hoặc bổ sung thông tin:\n- "
    return _simple_form(request, ContactForm, "public/feedback.html", initial=initial,
                        notify_subject="Liên hệ / Góp ý mới", notify_template="staff_new_contact")


def data_request(request):
    return _simple_form(request, DataRequestForm, "public/data_request.html",
                        initial={"profile_url": request.GET.get("ho-so", "")},
                        notify_subject="Yêu cầu về dữ liệu cá nhân", notify_template="staff_new_data_request")


def robots_txt(request):
    from django.conf import settings

    lines = ["User-agent: *", "Disallow: /quan-tri/", "Disallow: /thanh-vien/", "Disallow: /django-admin/",
             "Disallow: /api/", f"Sitemap: {settings.SITE_URL}/sitemap.xml"]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def page_not_found(request, exception=None):
    return render(request, "404.html", status=404)


def server_error(request):
    return HttpResponse(render_to_string("500.html"), status=500)


@require_POST
def toggle_like(request):
    """API thả tim/thích (Heart like) cho Story, Podcast, Event, Person.
    Hỗ trợ cả khách vãng lai (qua session + local storage) và thành viên đăng nhập.
    """
    import json
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        data = request.POST

    item_type = (data.get("type") or "").strip().lower()
    item_id = data.get("id")
    action = data.get("action", "toggle")

    type_model_map = {
        "story": Story,
        "podcast": Podcast,
        "event": Event,
        "person": Person,
    }
    model = type_model_map.get(item_type)
    if not model or not item_id:
        return JsonResponse({"success": False, "error": "Tham số không hợp lệ"}, status=400)

    try:
        obj = model.objects.get(pk=item_id)
    except (model.DoesNotExist, ValueError):
        return JsonResponse({"success": False, "error": "Không tìm thấy nội dung"}, status=404)

    session_key = f"liked_{item_type}_{obj.pk}"
    already_liked = request.session.get(session_key, False)

    if action == "like" or (action == "toggle" and not already_liked):
        model.objects.filter(pk=obj.pk).update(likes_count=F("likes_count") + 1)
        request.session[session_key] = True
        is_liked = True
    else:
        obj.refresh_from_db()
        new_count = max(0, obj.likes_count - 1)
        model.objects.filter(pk=obj.pk).update(likes_count=new_count)
        request.session[session_key] = False
        is_liked = False

    obj.refresh_from_db()
    return JsonResponse({
        "success": True,
        "liked": is_liked,
        "likes_count": obj.likes_count,
        "type": item_type,
        "id": obj.pk,
    })
