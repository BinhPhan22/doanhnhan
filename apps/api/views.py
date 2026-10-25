"""
API v1 — chỉ ĐỌC dữ liệu công khai (đã công bố), định dạng JSON.

Quy ước: GET, không cần khóa; phân trang ?page=&page_size= (tối đa 100); lỗi {"error": {"code", "message"}};
CORS mở cho mọi nguồn; giới hạn mặc định 120 yêu cầu/phút/IP. Đặc tả đầy đủ: docs/openapi.yaml (/api/v1/openapi.yaml).
Quyền riêng tư: năm sinh, quê quán, email chỉ trả về khi chủ hồ sơ để công khai; không trả dữ liệu nháp/ẩn,
không trả thông tin tài khoản, giấy tờ, liên hệ.
"""
from functools import wraps
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import EmptyPage, Paginator
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from apps.common.permissions import client_ip, is_admin
from apps.common.text import normalize, render_markdown
from apps.directory.models import (
    Association, Company, Event, EventParticipant, Membership, Person, PersonCompany, Province, Sector, Status,
    visible_videos,
)

API_VERSION = "1.0.0"
MAX_PAGE_SIZE = 100
RATE_LIMIT = getattr(settings, "API_RATE_LIMIT_PER_MIN", 120)


# --------------------------------------------------------------------------- hạ tầng
def _json(data, status=200):
    resp = JsonResponse(data, status=status, json_dumps_params={"ensure_ascii": False})
    resp["Access-Control-Allow-Origin"] = "*"
    resp["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    resp["Access-Control-Allow-Headers"] = "Accept, Content-Type"
    if status == 200:
        resp["Cache-Control"] = "public, max-age=300"
    return resp


def error(code, message, status):
    return _json({"error": {"code": code, "message": message}}, status)


def api_view(view):
    """GET/OPTIONS, giới hạn tần suất theo IP, trả lỗi JSON thống nhất."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.method == "OPTIONS":
            return _json({}, 200)
        if request.method not in ("GET", "HEAD"):
            return error("method_not_allowed", "API v1 chỉ hỗ trợ GET.", 405)
        key = f"api-rate:{client_ip(request)}:{timezone.now():%Y%m%d%H%M}"
        hits = cache.get_or_set(key, 0, 70)
        if hits >= RATE_LIMIT:
            resp = error("rate_limited", f"Vượt quá {RATE_LIMIT} yêu cầu/phút. Vui lòng thử lại sau.", 429)
            resp["Retry-After"] = "60"
            return resp
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, 70)
        try:
            return view(request, *args, **kwargs)
        except ApiError as exc:
            return error(exc.code, exc.message, exc.status)
    return wrapper


class ApiError(Exception):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status


def _abs(request, path):
    return request.build_absolute_uri(path)


def _int_param(request, name, default, lo=1, hi=None):
    raw = request.GET.get(name)
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except ValueError:
        raise ApiError("invalid_parameter", f"Tham số '{name}' phải là số nguyên.")
    if value < lo or (hi is not None and value > hi):
        raise ApiError("invalid_parameter", f"Tham số '{name}' phải trong khoảng {lo}–{hi or '∞'}.")
    return value


def paginate(request, qs, serialize):
    page_size = _int_param(request, "page_size", 20, 1, MAX_PAGE_SIZE)
    number = _int_param(request, "page", 1, 1)
    paginator = Paginator(qs, page_size)
    try:
        page = paginator.page(number)
    except EmptyPage:
        page = None

    def link(n):
        params = request.GET.copy()
        params["page"] = n
        return _abs(request, f"{request.path}?{params.urlencode()}")

    return _json({
        "count": paginator.count, "page": number, "page_size": page_size, "num_pages": paginator.num_pages,
        "next": link(number + 1) if page and page.has_next() else None,
        "previous": link(number - 1) if page and page.has_previous() else None,
        "results": [serialize(request, obj) for obj in page] if page else [],
    })


def _get(qs, **lookup):
    obj = qs.filter(**lookup).first()
    if obj is None:
        raise ApiError("not_found", "Không tìm thấy dữ liệu (hoặc chưa được công bố).", 404)
    return obj


def _iso(dt):
    return dt.isoformat() if dt else None


# --------------------------------------------------------------------------- tham chiếu ngắn
def ref_province(p):
    return {"code": p.code, "name": p.name} if p else None


def ref_sector(s):
    return {"slug": s.slug, "name": s.name, "parent": s.parent.slug if s.parent_id else None,
            "vsic_code": s.vsic_code or None} if s else None


def ref_person(request, p):
    return {"slug": p.slug, "full_name": p.full_name, "headline": p.headline,
            "url": _abs(request, p.get_absolute_url()),
            "api_url": _abs(request, f"/api/v1/persons/{p.slug}/")}


def ref_company(request, c):
    published = c.status == Status.PUBLISHED
    return {"slug": c.slug if published else None, "name": c.display_name, "legal_name": c.legal_name,
            "url": _abs(request, c.get_absolute_url()) if published else None,
            "api_url": _abs(request, f"/api/v1/companies/{c.slug}/") if published else None}


def ref_association(request, a):
    return {"slug": a.slug, "name": a.name, "short_name": a.short_name or None,
            "url": _abs(request, a.get_absolute_url())}


def ref_event(request, e):
    return {"slug": e.slug, "title": e.title, "starts_at": _iso(e.starts_at), "url": _abs(request, e.get_absolute_url())}


def _media(request, f):
    return _abs(request, f.url) if f else None


def _sections(items):
    return [{"key": s.key, "title": s.label, "word_count": s.word_count, "body_markdown": s.body_md,
             "body_html": str(render_markdown(s.body_md))} for s in items]


def _milestones(items):
    return [{"year": m.year, "kind": m.kind, "title": m.title, "source_url": m.source_url or None} for m in items]


def _sources(items):
    return [{"number": s.number, "title": s.title, "url": s.url or None, "kind": s.kind} for s in items]


def ser_video(request, v):
    return {
        "id": v.pk, "title": v.title, "kind": v.kind, "platform": v.platform, "url": v.url,
        "embeddable": v.embeddable, "thumbnail_url": v.thumbnail_url or None, "duration_seconds": v.duration_seconds,
        "channel_name": v.channel_name or None, "published_on": v.published_on.isoformat() if v.published_on else None,
        "persons": [ref_person(request, p) for p in v.persons.all() if p.status == Status.PUBLISHED],
        "companies": [ref_company(request, c) for c in v.companies.all() if c.status == Status.PUBLISHED],
        "events": [ref_event(request, e) for e in v.events.all() if e.status != "draft"],
    }


def _last_revision(entity):
    rev = entity.revisions.filter(state="approved").order_by("-reviewed_at").first()
    return {"number": rev.revision_no, "approved_at": _iso(rev.reviewed_at)} if rev else None


# --------------------------------------------------------------------------- gốc, danh mục
@api_view
def index(request):
    base = _abs(request, "/api/v1/")
    return _json({
        "name": "doanhnhan.wiki API", "version": API_VERSION, "documentation": base + "openapi.yaml",
        "endpoints": {k: base + v for k, v in {
            "provinces": "provinces/", "sectors": "sectors/", "persons": "persons/", "companies": "companies/",
            "associations": "associations/", "events": "events/", "videos": "videos/", "search": "search/?q="}.items()},
    })


@api_view
def openapi(request):
    path = Path(settings.BASE_DIR) / "docs" / "openapi.yaml"
    resp = HttpResponse(path.read_text(encoding="utf-8"), content_type="application/yaml; charset=utf-8")
    resp["Access-Control-Allow-Origin"] = "*"
    return resp


@api_view
def provinces(request):
    return _json({"count": Province.objects.count(), "results": [
        {"code": p.code, "name": p.name, "is_city": p.is_city, "merged_from": p.merged_from or None}
        for p in Province.objects.all()]})


def _sector_qs():
    return Sector.objects.filter(is_active=True).annotate(
        company_count=Count("companies", filter=Q(companies__status=Status.PUBLISHED), distinct=True))


def ser_sector(request, s, children=None):
    data = {**ref_sector(s), "description": s.description or None, "icon": s.icon,
            "company_count": getattr(s, "company_count", None), "url": _abs(request, s.get_absolute_url())}
    if children is not None:
        data["children"] = [ser_sector(request, c) for c in children]
    return data


@api_view
def sectors(request):
    allq = list(_sector_qs().select_related("parent"))
    roots = [s for s in allq if not s.parent_id]
    return _json({"count": len(roots), "results": [
        ser_sector(request, r, [c for c in allq if c.parent_id == r.pk]) for r in roots]})


@api_view
def sector_detail(request, slug):
    s = _get(_sector_qs().select_related("parent"), slug=slug)
    ids = s.family_ids()
    people = Person.objects.published().filter(company_links__company__sectors__in=ids,
                                               company_links__company__status=Status.PUBLISHED).distinct()
    data = ser_sector(request, s, list(_sector_qs().filter(parent=s)))
    data.update({
        "person_count": people.count(),
        "persons_api_url": _abs(request, f"/api/v1/persons/?sector={s.slug}"),
        "companies_api_url": _abs(request, f"/api/v1/companies/?sector={s.slug}"),
    })
    return _json(data)


# --------------------------------------------------------------------------- doanh nhân
def _persons_qs():
    return (Person.objects.published().select_related("current_province", "hometown")
            .prefetch_related(Prefetch("company_links", queryset=PersonCompany.objects.select_related(
                "company", "company__primary_sector", "company__primary_sector__parent")), "sections"))


def ser_person_summary(request, p):
    link = p.primary_link
    summary = next((s.body_md for s in p.sections.all() if s.key == "summary"), "")
    from apps.common.text import plain_excerpt

    return {
        **ref_person(request, p), "is_demo": p.is_demo, "verification": p.verification,
        "portrait_url": _media(request, p.portrait), "summary": plain_excerpt(summary, 300) or None,
        "province": ref_province(p.current_province),
        "primary_company": {**ref_company(request, link.company), "role": link.role, "title": link.label}
        if link else None,
        "sector": ref_sector(link.company.primary_sector) if link and link.company.primary_sector_id else None,
        "is_featured": p.is_featured, "published_at": _iso(p.published_at), "updated_at": _iso(p.updated_at),
    }


@api_view
def persons(request):
    qs = _persons_qs()
    if request.GET.get("q"):
        qs = qs.search(request.GET["q"])
    if request.GET.get("sector"):
        s = Sector.objects.filter(slug=request.GET["sector"]).first()
        if not s:
            raise ApiError("invalid_parameter", "Không có ngành với slug này.")
        qs = qs.filter(company_links__company__sectors__in=s.family_ids()).distinct()
    if request.GET.get("province"):
        qs = qs.filter(current_province__code=request.GET["province"])
    if request.GET.get("verified") in ("1", "true"):
        qs = qs.exclude(verification="none")
    if request.GET.get("featured") in ("1", "true"):
        qs = qs.filter(is_featured=True)
    ordering = {"name": "full_name", "-updated": "-updated_at", "updated": "updated_at", "newest": "-published_at"}
    order = request.GET.get("ordering", "-updated")
    if order not in ordering:
        raise ApiError("invalid_parameter", "ordering phải là một trong: " + ", ".join(ordering))
    return paginate(request, qs.order_by(ordering[order], "pk"), ser_person_summary)


@api_view
def person_detail(request, slug):
    qs = _persons_qs().prefetch_related(
        "milestones", "sources",
        Prefetch("memberships", queryset=Membership.objects.filter(state="confirmed").select_related("association")),
        Prefetch("event_participations", queryset=EventParticipant.objects.select_related("event")))
    p = _get(qs, slug=slug)
    data = ser_person_summary(request, p)
    data.update({
        "birth_year": p.birth_year if p.show_birth_year else None,
        "hometown": ref_province(p.hometown) if p.show_hometown else None,
        "email": p.email_public if p.show_email and p.email_public else None,
        "phone": (p.display_phone if is_admin(request.user) else p.masked_phone) if p.display_phone else None,
        "website": p.website or None,
        "verification_note": p.verification_note or None,
        "verified_at": p.verified_at.isoformat() if p.verified_at else None,
        "has_owner": bool(p.owner_id),
        "companies": [{**ref_company(request, l.company), "role": l.role, "title": l.label, "start_year": l.start_year,
                       "end_year": l.end_year, "is_primary": l.is_primary} for l in p.company_links.all()],
        "sections": _sections(p.sections.all()),
        "milestones": _milestones(p.milestones.all()),
        "sources": _sources(p.sources.all()),
        "memberships": [{**ref_association(request, m.association), "position": m.position,
                         "is_leadership": m.is_leadership, "start_year": m.start_year} for m in p.memberships.all()],
        "events": [{**ref_event(request, ep.event), "role": ep.role, "note": ep.note or None}
                   for ep in p.event_participations.all() if ep.event.status != "draft"],
        "videos": [ser_video(request, v) for v in visible_videos().filter(persons=p).prefetch_related(
            "persons", "companies", "events")],
        "revision": _last_revision(p),
    })
    return _json(data)


# --------------------------------------------------------------------------- doanh nghiệp
def _companies_qs():
    return (Company.objects.published().select_related("province", "primary_sector", "primary_sector__parent")
            .prefetch_related(Prefetch("person_links", queryset=PersonCompany.objects.select_related("person")
                                       .filter(person__status=Status.PUBLISHED)), "sections"))


def ser_company_summary(request, c):
    from apps.common.text import plain_excerpt

    overview = next((s.body_md for s in c.sections.all() if s.key == "overview"), "")
    return {
        **ref_company(request, c), "is_demo": c.is_demo, "brand_name": c.brand_name or None,
        "tax_code": c.tax_code, "founded_year": c.founded_year, "province": ref_province(c.province),
        "size_band": c.size_band or None, "primary_sector": ref_sector(c.primary_sector),
        "verification": c.verification, "logo_url": _media(request, c.logo),
        "summary": plain_excerpt(overview, 300) or None,
        "leaders": [{**ref_person(request, l.person), "role": l.role, "title": l.label} for l in c.person_links.all()],
        "updated_at": _iso(c.updated_at),
    }


@api_view
def companies(request):
    qs = _companies_qs()
    if request.GET.get("q"):
        qs = qs.search(request.GET["q"])
    if request.GET.get("sector"):
        s = Sector.objects.filter(slug=request.GET["sector"]).first()
        if not s:
            raise ApiError("invalid_parameter", "Không có ngành với slug này.")
        qs = qs.filter(sectors__in=s.family_ids()).distinct()
    if request.GET.get("province"):
        qs = qs.filter(province__code=request.GET["province"])
    if request.GET.get("size"):
        sizes = request.GET["size"].split(",")
        if any(x not in Company.Size.values for x in sizes):
            raise ApiError("invalid_parameter", "size phải thuộc: " + ", ".join(Company.Size.values))
        qs = qs.filter(size_band__in=sizes)
    if request.GET.get("founded_from"):
        qs = qs.filter(founded_year__gte=_int_param(request, "founded_from", None, 1900, 2100))
    if request.GET.get("founded_to"):
        qs = qs.filter(founded_year__lte=_int_param(request, "founded_to", None, 1900, 2100))
    if request.GET.get("verified") in ("1", "true"):
        qs = qs.exclude(verification="none")
    if request.GET.get("tax_code"):
        qs = qs.filter(tax_code=request.GET["tax_code"].strip())
    ordering = {"name": "legal_name", "-updated": "-updated_at", "founded": "founded_year", "-founded": "-founded_year"}
    order = request.GET.get("ordering", "-updated")
    if order not in ordering:
        raise ApiError("invalid_parameter", "ordering phải là một trong: " + ", ".join(ordering))
    return paginate(request, qs.order_by(ordering[order], "pk"), ser_company_summary)


@api_view
def company_detail(request, slug):
    c = _get(_companies_qs().prefetch_related("milestones", "sources", "products", "sectors__parent"), slug=slug)
    data = ser_company_summary(request, c)
    data.update({
        "address": c.address or None, "website": c.website or None, "cover_url": _media(request, c.cover),
        "sectors": [ref_sector(s) for s in c.sectors.all()],
        "verification_note": c.verification_note or None,
        "verified_at": c.verified_at.isoformat() if c.verified_at else None,
        "leaders": [{**ref_person(request, l.person), "role": l.role, "title": l.label, "start_year": l.start_year}
                    for l in c.person_links.all()],
        "sections": _sections(c.sections.all()),
        "products": [{"name": p.name, "description": p.description or None} for p in c.products.all()],
        "milestones": _milestones(c.milestones.all()),
        "sources": _sources(c.sources.all()),
        "videos": [ser_video(request, v) for v in visible_videos().filter(companies=c).prefetch_related(
            "persons", "companies", "events")],
        "revision": _last_revision(c),
    })
    return _json(data)


# --------------------------------------------------------------------------- hiệp hội
def _assoc_qs():
    return (Association.objects.published().select_related("province", "parent")
            .annotate(member_count=Count("memberships", filter=Q(memberships__state="confirmed",
                                                                 memberships__person__status=Status.PUBLISHED),
                                         distinct=True)))


def ser_association(request, a):
    return {**ref_association(request, a), "level": a.level, "province": ref_province(a.province),
            "parent": ref_association(request, a.parent) if a.parent_id else None, "is_partner": a.is_partner,
            "member_count": a.member_count, "logo_url": _media(request, a.logo), "website": a.website or None,
            "api_url": _abs(request, f"/api/v1/associations/{a.slug}/")}


@api_view
def associations(request):
    qs = _assoc_qs()
    if request.GET.get("q"):
        qs = qs.search(request.GET["q"])
    if request.GET.get("level"):
        if request.GET["level"] not in Association.Level.values:
            raise ApiError("invalid_parameter", "level phải thuộc: " + ", ".join(Association.Level.values))
        qs = qs.filter(level=request.GET["level"])
    return paginate(request, qs.order_by("-is_partner", "name"), ser_association)


@api_view
def association_detail(request, slug):
    a = _get(_assoc_qs().prefetch_related("sectors"), slug=slug)
    members = (a.memberships.filter(state="confirmed", person__status=Status.PUBLISHED).select_related("person")
               .order_by("-is_leadership", "sort_order", "person__full_name"))
    data = ser_association(request, a)
    data.update({
        "description_markdown": a.description or None, "description_html": str(render_markdown(a.description)) or None,
        "partner_since": a.partner_since.isoformat() if a.partner_since else None,
        "sectors": [ref_sector(s) for s in a.sectors.all()],
        "members": [{**ref_person(request, m.person), "position": m.position, "is_leadership": m.is_leadership,
                     "start_year": m.start_year} for m in members[:500]],
        "children": [ref_association(request, c) for c in a.children.filter(status=Status.PUBLISHED)],
        "events": [ref_event(request, e) for e in a.events.exclude(status="draft").order_by("-starts_at")[:50]],
    })
    return _json(data)


# --------------------------------------------------------------------------- sự kiện
def _events_qs():
    return (Event.objects.exclude(status__in=["draft", "archived"]).select_related("organizer", "province")
            .annotate(participant_count=Count("participants", distinct=True)))


def ser_event(request, e):
    return {**ref_event(request, e), "kind": e.kind, "status": e.status, "ends_at": _iso(e.ends_at),
            "venue": e.venue or None, "is_online": e.is_online, "province": ref_province(e.province),
            "organizer": ref_association(request, e.organizer) if e.organizer_id else (
                {"name": e.organizer_text} if e.organizer_text else None),
            "registration_url": e.registration_url or None, "participant_count": e.participant_count,
            "is_featured": e.is_featured, "api_url": _abs(request, f"/api/v1/events/{e.slug}/")}


@api_view
def events(request):
    qs = _events_qs()
    now = timezone.now()
    when = request.GET.get("when", "")
    if when == "upcoming":
        qs = qs.filter(Q(ends_at__gte=now) | Q(ends_at__isnull=True, starts_at__gte=now)).order_by("starts_at")
    elif when == "past":
        qs = qs.filter(Q(ends_at__lt=now) | Q(ends_at__isnull=True, starts_at__lt=now)).order_by("-starts_at")
    elif when:
        raise ApiError("invalid_parameter", "when phải là upcoming hoặc past.")
    else:
        qs = qs.order_by("-starts_at")
    if request.GET.get("kind"):
        qs = qs.filter(kind=request.GET["kind"])
    if request.GET.get("q"):
        qs = qs.search(request.GET["q"])
    if request.GET.get("association"):
        qs = qs.filter(organizer__slug=request.GET["association"])
    return paginate(request, qs, ser_event)


@api_view
def event_detail(request, slug):
    e = _get(_events_qs().prefetch_related("sectors"), slug=slug)
    data = ser_event(request, e)
    parts = e.participants.filter(person__status=Status.PUBLISHED).select_related("person")
    data.update({
        "description_markdown": e.description or None, "description_html": str(render_markdown(e.description)) or None,
        "sectors": [ref_sector(s) for s in e.sectors.all()],
        "participants": [{**ref_person(request, ep.person), "role": ep.role, "note": ep.note or None} for ep in parts],
        "videos": [ser_video(request, v) for v in visible_videos().filter(events=e).prefetch_related(
            "persons", "companies", "events")],
    })
    return _json(data)


# --------------------------------------------------------------------------- video & tìm kiếm
@api_view
def videos(request):
    qs = visible_videos().prefetch_related("persons", "companies", "events")
    if request.GET.get("kind"):
        qs = qs.filter(kind=request.GET["kind"])
    if request.GET.get("platform"):
        qs = qs.filter(platform=request.GET["platform"])
    if request.GET.get("person"):
        qs = qs.filter(persons__slug=request.GET["person"])
    if request.GET.get("company"):
        qs = qs.filter(companies__slug=request.GET["company"])
    if request.GET.get("event"):
        qs = qs.filter(events__slug=request.GET["event"])
    if request.GET.get("q"):
        qs = qs.filter(search_text__contains=normalize(request.GET["q"]))
    return paginate(request, qs.distinct(), ser_video)


@api_view
def search(request):
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        raise ApiError("invalid_parameter", "Tham số 'q' cần ít nhất 2 ký tự.")
    limit = _int_param(request, "limit", 10, 1, 50)
    return _json({
        "query": q,
        "persons": [ser_person_summary(request, p) for p in _persons_qs().search(q)[:limit]],
        "companies": [ser_company_summary(request, c) for c in _companies_qs().search(q)[:limit]],
        "associations": [ser_association(request, a) for a in _assoc_qs().search(q)[:limit]],
        "events": [ser_event(request, e) for e in _events_qs().search(q)[:limit]],
        "sectors": [ser_sector(request, s) for s in _sector_qs().select_related("parent").search(q)[:limit]],
    })


def not_found(request, rest=""):
    return error("not_found", "Không có endpoint này. Xem /api/v1/ để biết danh sách.", 404)
