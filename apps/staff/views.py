"""
Bảng quản trị (/quan-tri/).

- Biên tập viên: hàng chờ duyệt, tài khoản thành viên, nhận quản lý hồ sơ, phỏng vấn, liên hệ,
  nhập liệu doanh nhân / doanh nghiệp / ngành / hiệp hội / sự kiện / video.
- Quản trị viên: thêm người dùng & vai trò, trang tài trợ, chính sách, yêu cầu dữ liệu, nhật ký, cài đặt.
"""
from datetime import timedelta

from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Prefetch, Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST

from apps.accounts.models import AccountApplication, RoleChangeRequest, User
from apps.common import video as video_lib
from apps.common.notify import send
from apps.common.permissions import admin_required, editor_required
from apps.common.text import normalize
from apps.directory.models import (
    Association, AwardBadge, Company, Event, EventParticipant, Membership, Milestone, Person, PersonAward,
    PersonCompany, Podcast, Postcard, Province, Sector, SECTOR_ICONS, Status, Story, Video,
)
from apps.moderation import services
from apps.moderation.editor import NEW_COMPANY, NEW_PERSON, editor_context
from apps.moderation.models import AuditLog, ProfileClaim, Revision, log
from apps.sitecontent.models import (
    ContactMessage, DataRequest, DonationAccount, DonationSettings, InterviewRequest, PolicyDocument, PolicyVersion,
    SiteSettings,
)

from . import forms as sf


def _page(request, qs, n=30):
    return Paginator(qs, n).get_page(request.GET.get("trang"))


def _clear_counts():
    cache.delete("staff_counts")


# =========================================================================== tổng quan & hàng chờ
@editor_required
def dashboard(request):
    qs = Revision.objects.filter(state=Revision.State.PENDING).select_related("author", "person", "company")
    kind = request.GET.get("loai", "")
    if kind in ("create", "update"):
        qs = qs.filter(kind=kind)
    if request.GET.get("doi-tuong") in ("person", "company"):
        qs = qs.filter(entity_type=request.GET["doi-tuong"])
    recent = Revision.objects.filter(state="approved", reviewed_at__gte=timezone.now() - timedelta(days=30)) \
        .exclude(author_role="editor")
    avg = recent.annotate(d=ExpressionWrapper(F("reviewed_at") - F("created_at"), output_field=DurationField())) \
        .aggregate(a=Avg("d"))["a"]
    return render(request, "staff/dashboard.html", {
        "queue": qs.order_by("created_at"), "kind": kind,
        "kpi": {
            "pending": Revision.objects.filter(state="pending").count(),
            "needs_info": Revision.objects.filter(state="needs_info").count(),
            "accounts": AccountApplication.objects.filter(status="pending").count(),
            "claims": ProfileClaim.objects.filter(state="pending").count(),
            "interviews": InterviewRequest.objects.filter(state="new").count(),
            "data_requests": DataRequest.objects.filter(state="open").count(),
            "avg_hours": round(avg.total_seconds() / 3600, 1) if avg else None,
            "unavailable_videos": Video.objects.filter(availability="unavailable", status="published").count(),
        },
    })


REASON_TEMPLATES = [
    ("missing_sources", "Thiếu nguồn dẫn chứng cho các thông tin quan trọng"),
    ("unverified_business", "Thông tin hoạt động kinh doanh chưa xác minh được"),
    ("copyright_media", "Ảnh chân dung / tài liệu chưa rõ quyền sử dụng"),
    ("need_neutral_rewrite", "Nội dung mang tính quảng cáo / cần viết lại cho trung thực, khách quan"),
]


@editor_required
def review(request, pk):
    rev = get_object_or_404(Revision.objects.select_related("author", "person", "company", "reviewer"), pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        reason_template = request.POST.get("reason_template", "").strip()
        raw_note = request.POST.get("review_note", "").strip()
        if reason_template and not raw_note:
            note = reason_template
        elif reason_template and raw_note and reason_template not in raw_note:
            note = f"{reason_template}: {raw_note}"
        else:
            note = raw_note

        try:
            if action == "approve":
                services.approve(rev, request.user, note=raw_note, request=request)
                messages.success(request, f"Đã duyệt: {rev.title}")
            elif action in ("needs_info", "reject"):
                if not note:
                    messages.error(request, "Vui lòng chọn hoặc ghi chú lý do khi yêu cầu bổ sung hoặc từ chối.")
                    return redirect("staff:review", pk=pk)
                services.reject(rev, request.user, note, needs_info=(action == "needs_info"), request=request)
                messages.success(request, "Đã gửi yêu cầu bổ sung." if action == "needs_info" else "Đã từ chối.")
        except ValueError as exc:
            messages.error(request, str(exc))
        _clear_counts()
        nxt = Revision.objects.filter(state="pending").order_by("created_at").first()
        return redirect("staff:review", pk=nxt.pk) if nxt else redirect("staff:dashboard")
    current = services.serialize(rev.target) if rev.target and rev.state != "approved" else rev.previous_data
    return render(request, "staff/review.html", {
        "rev": rev, "diff": services.diff_payload(rev.entity_type, current or {}, rev.data),
        "checks": services.compute_checks(rev.entity_type, rev.data, rev.target) if rev.state == "pending" else rev.checks,
        "author_app": getattr(rev.author, "application", None) if rev.author else None,
        "author_stats": Revision.objects.filter(author=rev.author).values("state").annotate(n=Count("pk")) if rev.author else [],
        "reason_templates": REASON_TEMPLATES,
    })


# =========================================================================== tài khoản thành viên
@editor_required
def accounts(request):
    status = request.GET.get("trang-thai", "pending")
    qs = AccountApplication.objects.select_related("user", "reviewed_by")
    if status in AccountApplication.Status.values:
        qs = qs.filter(status=status)
    return render(request, "staff/accounts.html", {"page": _page(request, qs.order_by("-created_at")), "status": status,
                                                   "statuses": AccountApplication.Status.choices})


@editor_required
@require_POST
def account_decide(request, pk):
    app = get_object_or_404(AccountApplication.objects.select_related("user"), pk=pk)
    action, note = request.POST.get("action"), request.POST.get("note", "").strip()
    user = app.user
    if action in ("needs_info", "reject") and not note:
        messages.error(request, "Vui lòng ghi chú lý do.")
        return redirect("staff:accounts")
    app.reviewed_by, app.reviewed_at, app.review_note = request.user, timezone.now(), note
    if action == "approve":
        app.status = AccountApplication.Status.APPROVED
        user.status = User.Status.ACTIVE
        send(user.email, "Tài khoản đã được duyệt", "account_approved", {"user": user})
    elif action == "needs_info":
        app.status = AccountApplication.Status.NEEDS_INFO
        send(user.email, "Cần bổ sung thông tin đăng ký", "account_needs_info", {"user": user, "note": note})
    elif action == "reject":
        app.status = AccountApplication.Status.REJECTED
        user.status = User.Status.REJECTED
        send(user.email, "Kết quả đăng ký tài khoản", "account_rejected", {"user": user, "note": note})
    else:
        return redirect("staff:accounts")
    app.save()
    user.save(update_fields=["status"])
    log(request.user, f"account.{action}", user, user.email, {"note": note}, request=request)
    _clear_counts()
    messages.success(request, f"Đã cập nhật tài khoản {user.email}.")
    return redirect(request.POST.get("next") or "staff:accounts")


# =========================================================================== nhận quản lý hồ sơ
@editor_required
def claims(request):
    qs = ProfileClaim.objects.select_related("person", "user", "reviewed_by")
    state = request.GET.get("trang-thai", "pending")
    if state in ProfileClaim.State.values:
        qs = qs.filter(state=state)
    return render(request, "staff/claims.html", {"claims": qs, "state": state})


@editor_required
@require_POST
def claim_decide(request, pk):
    claim = get_object_or_404(ProfileClaim.objects.select_related("person", "user"), pk=pk)
    action, note = request.POST.get("action"), request.POST.get("note", "").strip()
    if claim.state != "pending":
        return redirect("staff:claims")
    claim.reviewed_by, claim.reviewed_at, claim.review_note = request.user, timezone.now(), note
    if action == "approve":
        if claim.person.owner_id and claim.person.owner_id != claim.user_id:
            messages.error(request, "Hồ sơ đã có người quản lý khác.")
            return redirect("staff:claims")
        claim.state = ProfileClaim.State.APPROVED
        claim.person.owner = claim.user
        claim.person.save(update_fields=["owner"])
        send(claim.user.email, f"Đã xác nhận quản lý hồ sơ {claim.person.full_name}", "claim_approved", {"claim": claim})
    elif action == "reject":
        if not note:
            messages.error(request, "Vui lòng ghi chú lý do.")
            return redirect("staff:claims")
        claim.state = ProfileClaim.State.REJECTED
        send(claim.user.email, "Yêu cầu nhận quản lý hồ sơ chưa được chấp thuận", "claim_rejected", {"claim": claim})
    claim.save()
    log(request.user, f"claim.{action}", claim, claim.person.full_name, {"user": claim.user.email}, request=request)
    _clear_counts()
    return redirect("staff:claims")


@editor_required
def claim_evidence(request, pk):
    claim = get_object_or_404(ProfileClaim, pk=pk)
    if not claim.evidence or not claim.evidence.storage.exists(claim.evidence.name):
        raise Http404("Không tìm thấy tệp giấy tờ trên máy chủ.")
    log(request.user, "claim.view_evidence", claim, claim.person.full_name, request=request)
    return FileResponse(claim.evidence.open("rb"), as_attachment=True, filename=claim.evidence.name.rsplit("/", 1)[-1])


# =========================================================================== doanh nhân & doanh nghiệp
@editor_required
def person_list(request):
    qs = (Person.objects.select_related("owner")
          .prefetch_related(Prefetch("awards", queryset=PersonAward.objects.select_related("badge")))
          .annotate(rev_count=Count("revisions")))
    q = request.GET.get("q", "")
    if q:
        qs = qs.search(q)
    status = request.GET.get("trang-thai", "")
    if status in Status.values:
        qs = qs.filter(status=status)
    return render(request, "staff/person_list.html", {"page": _page(request, qs.order_by("-updated_at")), "q": q,
                                                      "status": status, "statuses": Status.choices})


@editor_required
def company_list(request):
    qs = Company.objects.select_related("province", "primary_sector")
    q = request.GET.get("q", "")
    if q:
        qs = qs.search(q)
    status = request.GET.get("trang-thai", "")
    if status in Status.values:
        qs = qs.filter(status=status)
    return render(request, "staff/company_list.html", {"page": _page(request, qs.order_by("-updated_at")), "q": q,
                                                       "status": status, "statuses": Status.choices})


def _staff_editor(request, entity_type, instance=None):
    base = services.serialize(instance) if instance else dict(NEW_PERSON if entity_type == "person" else NEW_COMPANY)
    errors, note = {}, ""
    if request.method == "POST":
        data, errors = services.parse_post(entity_type, request, base=base, staff=True)
        note = request.POST.get("note", "").strip()
        if not errors:
            rev = services.save_by_staff(entity_type=entity_type, data=data, editor=request.user, instance=instance,
                                         note=note, request=request)
            messages.success(request, f"Đã lưu và công bố bản sửa #{rev.revision_no}: {rev.title}")
            return redirect(rev.target.get_absolute_url() if rev.target.status == Status.PUBLISHED else
                            reverse("staff:person_list" if entity_type == "person" else "staff:company_list"))
        base = data
        messages.error(request, "Vui lòng kiểm tra lại các ô được đánh dấu.")
    ctx = editor_context(entity_type, base, errors, staff=True, note=note)
    ctx["instance"] = instance
    if instance:
        ctx["pending"] = instance.revisions.filter(state="pending")
    return render(request, "staff/editor.html", ctx)


@editor_required
def person_new(request):
    return _staff_editor(request, "person")


@editor_required
def person_edit(request, pk):
    return _staff_editor(request, "person", get_object_or_404(Person, pk=pk))


@editor_required
def company_new(request):
    return _staff_editor(request, "company")


@editor_required
def company_edit(request, pk):
    return _staff_editor(request, "company", get_object_or_404(Company, pk=pk))


@editor_required
@require_POST
def person_toggle_status(request, pk):
    person = get_object_or_404(Person, pk=pk)
    if person.status == Status.ARCHIVED:
        person.status = Status.PUBLISHED
        action = "unarchive"
        msg = f"Đã bỏ ẩn (công bố lại) hồ sơ doanh nhân: {person.full_name}"
    else:
        person.status = Status.ARCHIVED
        action = "archive"
        msg = f"Đã ẩn hồ sơ doanh nhân: {person.full_name}"
    person.save(update_fields=["status", "updated_at"])
    log(request.user, f"person.{action}", person, person.full_name, request=request)
    messages.success(request, msg)
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    return redirect(next_url or "staff:person_list")


@editor_required
@require_POST
def person_delete(request, pk):
    person = get_object_or_404(Person, pk=pk)
    name = person.full_name
    person.delete()
    log(request.user, "person.delete", None, name, request=request)
    messages.success(request, f"Đã xóa vĩnh viễn hồ sơ doanh nhân: {name}")
    return redirect("staff:person_list")


@editor_required
@require_POST
def company_toggle_status(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if company.status == Status.ARCHIVED:
        company.status = Status.PUBLISHED
        action = "unarchive"
        msg = f"Đã bỏ ẩn (công bố lại) doanh nghiệp: {company.display_name}"
    else:
        company.status = Status.ARCHIVED
        action = "archive"
        msg = f"Đã ẩn doanh nghiệp: {company.display_name}"
    company.save(update_fields=["status", "updated_at"])
    log(request.user, f"company.{action}", company, company.display_name, request=request)
    messages.success(request, msg)
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    return redirect(next_url or "staff:company_list")


@editor_required
@require_POST
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    name = company.display_name
    company.delete()
    log(request.user, "company.delete", None, name, request=request)
    messages.success(request, f"Đã xóa vĩnh viễn doanh nghiệp: {name}")
    return redirect("staff:company_list")



# =========================================================================== CRUD đơn giản
def _crud_form(request, form_class, instance, *, title, back, action_name, extra=None, template="staff/form.html",
               after_save=None, initial=None):
    form = form_class(request.POST or None, request.FILES or None, instance=instance, initial=initial)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        if after_save:
            after_save(obj, form)
        log(request.user, f"{action_name}.{'update' if instance else 'create'}", obj, str(obj), request=request)
        messages.success(request, f"Đã lưu: {obj}")
        return redirect(back)
    return render(request, template, {"form": form, "title": title, "back": back, "instance": instance, **(extra or {})})


@editor_required
def sector_list(request):
    roots = Sector.objects.filter(parent__isnull=True).prefetch_related("children").annotate(
        n=Count("companies", distinct=True))
    total_roots = roots.count()
    total_children = Sector.objects.filter(parent__isnull=False).count()
    total_companies = Company.objects.filter(sectors__isnull=False).distinct().count()
    return render(request, "staff/sector_list.html", {
        "roots": roots,
        "total_roots": total_roots,
        "total_children": total_children,
        "total_companies": total_companies,
    })


@editor_required
def sector_form(request, pk=None):
    instance = get_object_or_404(Sector, pk=pk) if pk else None
    extra = {}
    if instance:
        extra["delete_url"] = reverse("staff:sector_delete", args=[instance.pk])
        extra["toggle_url"] = reverse("staff:sector_toggle_status", args=[instance.pk])
        extra["toggle_label"] = "Ẩn (ngừng dùng)" if instance.is_active else "Kích hoạt lại"
    initial = {}
    if not instance and request.GET.get("parent"):
        initial["parent"] = request.GET.get("parent")
    return _crud_form(request, sf.SectorForm, instance, title="Ngành nghề", back=reverse("staff:sector_list"),
                      action_name="sector", extra=extra, initial=initial)


@editor_required
@require_POST
def api_sector_quick_add(request):
    """Thêm nhanh ngành nghề hoặc phân ngành mới bằng AJAX từ giao diện nhập liệu."""
    import json
    try:
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
    except Exception:
        data = request.POST

    name = (data.get("name") or "").strip()
    if not name:
        return JsonResponse({"ok": False, "error": "Vui lòng nhập tên ngành nghề."}, status=400)

    parent_id = data.get("parent_id")
    parent = None
    if parent_id:
        try:
            parent = Sector.objects.filter(pk=int(parent_id), parent__isnull=True).first()
        except (ValueError, TypeError):
            parent = None

    vsic_code = (data.get("vsic_code") or "").strip()
    icon = (data.get("icon") or "tech").strip()
    if icon not in SECTOR_ICONS:
        icon = parent.icon if parent else "tech"

    # Kiểm tra trùng tên dưới cùng một ngành cha (hoặc cùng cấp 1)
    existing = Sector.objects.filter(name__iexact=name, parent=parent).first()
    if existing:
        return JsonResponse({
            "ok": True,
            "created": False,
            "sector": {
                "id": existing.id,
                "name": existing.name,
                "parent_id": existing.parent_id,
                "text": str(existing),
                "is_root": existing.parent_id is None,
            },
            "message": f"Ngành nghề “{existing}” đã có sẵn trong hệ thống.",
        })

    sector = Sector.objects.create(
        name=name,
        parent=parent,
        vsic_code=vsic_code,
        icon=icon,
        is_active=True,
    )
    log(request.user, "sector.quick_add", sector, sector.name, request=request)

    return JsonResponse({
        "ok": True,
        "created": True,
        "sector": {
            "id": sector.id,
            "name": sector.name,
            "parent_id": sector.parent_id,
            "text": str(sector),
            "is_root": sector.parent_id is None,
        },
        "message": f"Đã thêm thành công ngành nghề: {sector}",
    })


# =========================================================================== danh hiệu & giải thưởng
@editor_required
def award_list(request):
    qs = AwardBadge.objects.annotate(
        awardees_count=Count("awardees", distinct=True),
        companies_count=Count("company_awardees", distinct=True),
    ).order_by("sort_order", "name")
    q = request.GET.get("q", "").strip()
    badge_type = request.GET.get("loai", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(issuer__icontains=q) | Q(description__icontains=q))
    if badge_type:
        qs = qs.filter(badge_type=badge_type)
    return render(request, "staff/award_list.html", {
        "page": _page(request, qs, 30),
        "q": q,
        "badge_type": badge_type,
        "badge_types": AwardBadge.BadgeType.choices,
    })


@editor_required
def award_form(request, pk=None):
    instance = get_object_or_404(AwardBadge, pk=pk) if pk else None
    extra = {}
    if instance:
        extra["delete_url"] = reverse("staff:award_delete", args=[instance.pk])
    return _crud_form(
        request, sf.AwardBadgeForm, instance,
        title="Danh hiệu / Giải thưởng",
        back=reverse("staff:award_list"),
        action_name="award",
        extra=extra,
    )


@editor_required
@require_POST
def award_delete(request, pk):
    badge = get_object_or_404(AwardBadge, pk=pk)
    name = badge.name
    count = badge.awardees.count() + badge.company_awardees.count()
    badge.delete()
    log(request.user, "award.delete", None, name, request=request)
    messages.success(request, f"Đã xóa danh hiệu “{name}” (thu hồi khỏi {count} hồ sơ đã gán).")
    return redirect("staff:award_list")


@editor_required
def award_honors(request, pk):
    badge = get_object_or_404(AwardBadge, pk=pk)
    awardees_qs = badge.awardees.select_related("person").order_by("-year", "-created_at")
    company_awardees_qs = badge.company_awardees.select_related("company").order_by("-year", "-created_at")

    form_type = request.POST.get("form_type", "person")
    person_form = sf.PersonAwardAssignForm(request.POST if form_type == "person" else None)
    company_form = sf.CompanyAwardAssignForm(request.POST if form_type == "company" else None)

    if request.method == "POST":
        if form_type == "person" and person_form.is_valid():
            award = person_form.save(commit=False)
            award.badge = badge
            award.save()
            log(request.user, "award.assign", award.person, f"Vinh danh: {badge.name} cho {award.person.full_name}", request=request)
            messages.success(request, f"Đã gán danh hiệu “{badge.name}” cho doanh nhân {award.person.full_name}!")
            return redirect("staff:award_honors", pk=badge.pk)
        elif form_type == "company" and company_form.is_valid():
            award = company_form.save(commit=False)
            award.badge = badge
            award.save()
            log(request.user, "award.assign_company", award.company, f"Vinh danh: {badge.name} cho {award.company.display_name}", request=request)
            messages.success(request, f"Đã gán danh hiệu “{badge.name}” cho doanh nghiệp {award.company.display_name}!")
            return redirect("staff:award_honors", pk=badge.pk)

    return render(request, "staff/award_honors.html", {
        "badge": badge,
        "awardees": awardees_qs,
        "company_awardees": company_awardees_qs,
        "person_form": person_form,
        "company_form": company_form,
    })


@editor_required
@require_POST
def award_honor_delete(request, pk, award_pk):
    badge = get_object_or_404(AwardBadge, pk=pk)
    award = get_object_or_404(PersonAward, pk=award_pk, badge=badge)
    person_name = award.person.full_name
    award.delete()
    log(request.user, "award.unassign", None, f"Gỡ danh hiệu {badge.name} khỏi {person_name}", request=request)
    messages.success(request, f"Đã thu hồi danh hiệu “{badge.name}” khỏi doanh nhân {person_name}.")
    return redirect("staff:award_honors", pk=badge.pk)


@editor_required
@require_POST
def award_company_honor_delete(request, pk, award_pk):
    from apps.directory.models import CompanyAward
    badge = get_object_or_404(AwardBadge, pk=pk)
    award = get_object_or_404(CompanyAward, pk=award_pk, badge=badge)
    company_name = award.company.display_name
    award.delete()
    log(request.user, "award.unassign_company", None, f"Gỡ danh hiệu {badge.name} khỏi {company_name}", request=request)
    messages.success(request, f"Đã thu hồi danh hiệu “{badge.name}” khỏi doanh nghiệp {company_name}.")
    return redirect("staff:award_honors", pk=badge.pk)


@editor_required
def association_list(request):
    qs = Association.objects.select_related("province", "parent").annotate(
        members=Count("memberships", filter=Q(memberships__state="confirmed")),
        pending=Count("memberships", filter=Q(memberships__state="pending")))
    q = request.GET.get("q", "")
    if q:
        qs = qs.search(q)
    status = request.GET.get("trang-thai", "")
    if status in Status.values:
        qs = qs.filter(status=status)
    return render(request, "staff/association_list.html", {
        "associations": qs.order_by("name"), "q": q, "status": status, "statuses": Status.choices,
    })


@editor_required
def association_form(request, pk=None):
    instance = get_object_or_404(Association, pk=pk) if pk else None
    extra = {}
    if instance:
        extra["delete_url"] = reverse("staff:association_delete", args=[instance.pk])
        extra["toggle_url"] = reverse("staff:association_toggle_status", args=[instance.pk])
        extra["toggle_label"] = "Bỏ ẩn hiệp hội" if instance.status == Status.ARCHIVED else "Ẩn hiệp hội"
    return _crud_form(request, sf.AssociationForm, instance, title="Hiệp hội",
                      back=reverse("staff:association_list"), action_name="association", extra=extra)


@editor_required
def association_members(request, pk):
    association = get_object_or_404(Association, pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add":
            person = services.find_person(request.POST.get("person", ""))
            if not person:
                messages.error(request, "Không tìm thấy doanh nhân. Hãy chọn tên trong danh sách gợi ý.")
            else:
                m, created = Membership.objects.update_or_create(person=person, association=association, defaults={
                    "position": request.POST.get("position", "").strip() or "Hội viên",
                    "is_leadership": request.POST.get("is_leadership") == "on",
                    "sort_order": int(request.POST.get("sort_order") or 100),
                    "start_year": services._int(request.POST.get("start_year")),
                    "state": Membership.State.CONFIRMED, "confirmed_at": timezone.now()})
                log(request.user, "membership.add", m, f"{person.full_name} · {association.name}", request=request)
                messages.success(request, f"Đã cập nhật hội viên {person.full_name}.")
        elif action in ("confirm", "reject", "delete"):
            m = get_object_or_404(Membership, pk=request.POST.get("membership"), association=association)
            if action == "delete":
                m.delete()
            else:
                m.state = Membership.State.CONFIRMED if action == "confirm" else Membership.State.REJECTED
                m.confirmed_at = timezone.now()
                m.save()
            log(request.user, f"membership.{action}", m, f"{m.person.full_name} · {association.name}", request=request)
        return redirect("staff:association_members", pk=pk)
    return render(request, "staff/association_members.html", {
        "association": association,
        "memberships": association.memberships.select_related("person").order_by("state", "-is_leadership", "sort_order")})


@editor_required
def event_list(request):
    qs = Event.objects.select_related("organizer").annotate(n=Count("participants"))
    q = request.GET.get("q", "")
    if q:
        qs = qs.search(q)
    status = request.GET.get("trang-thai", "")
    if status in Event.EventStatus.values:
        qs = qs.filter(status=status)
    return render(request, "staff/event_list.html", {
        "page": _page(request, qs.order_by("-starts_at")), "q": q,
        "status": status, "statuses": Event.EventStatus.choices,
    })


@editor_required
def event_form(request, pk=None):
    instance = get_object_or_404(Event, pk=pk) if pk else None

    def save_participants(event, form):
        rows = services._rows(request.POST, "participant", ["name", "role", "note", "milestone"])
        keep = []
        for row in rows:
            person = services.find_person(row["name"])
            if not person:
                messages.warning(request, f"Bỏ qua “{row['name']}”: chưa có hồ sơ doanh nhân.")
                continue
            role = row["role"] if row["role"] in EventParticipant.Role.values else "attendee"
            ep, _ = EventParticipant.objects.update_or_create(event=event, person=person, role=role,
                                                              defaults={"note": row["note"][:200]})
            if row["milestone"] == "1" and not ep.milestone_id:
                kind = {"awardee": "award", "speaker": "community", "sponsor": "community"}.get(role, "other")
                title = f"{ep.get_role_display()}{' – ' + ep.note if ep.note else ''} tại {event.title}"
                ep.milestone = Milestone.objects.create(person=person, year=event.starts_at.year, kind=kind,
                                                        title=title[:255], event=event)
                ep.save(update_fields=["milestone"])
            keep.append(ep.pk)
        event.participants.exclude(pk__in=keep).delete()

    participants = list(instance.participants.select_related("person")) if instance else []
    extra = {"participants": participants or [None], "roles": EventParticipant.Role.choices}
    if instance:
        extra["delete_url"] = reverse("staff:event_delete", args=[instance.pk])
        extra["toggle_url"] = reverse("staff:event_toggle_status", args=[instance.pk])
        extra["toggle_label"] = "Bỏ ẩn sự kiện" if instance.status == Event.EventStatus.ARCHIVED else "Ẩn sự kiện"
    return _crud_form(request, sf.EventForm, instance, title="Sự kiện", back=reverse("staff:event_list"),
                      action_name="event", template="staff/event_form.html", after_save=save_participants,
                      extra=extra)


# =========================================================================== story (câu chuyện doanh nhân & phóng sự)
@editor_required
def story_list(request):
    qs = Story.objects.select_related("featured_person", "featured_company")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.search(q)
    story_type = request.GET.get("loai", "").strip()
    if story_type in Story.StoryType.values:
        qs = qs.filter(story_type=story_type)
    status = request.GET.get("trang-thai", "").strip()
    if status in Status.values:
        qs = qs.filter(status=status)

    total_stories = qs.count()
    return render(request, "staff/story_list.html", {
        "stories": qs[:100],
        "q": q,
        "story_type": story_type,
        "story_types": Story.StoryType.choices,
        "status": status,
        "statuses": Status.choices,
        "total_stories": total_stories,
    })


@editor_required
def story_form(request, pk=None):
    instance = get_object_or_404(Story, pk=pk) if pk else None
    extra = {}
    if instance:
        extra["delete_url"] = reverse("staff:story_delete", args=[instance.pk])
        extra["toggle_url"] = reverse("staff:story_toggle_status", args=[instance.pk])
        extra["toggle_label"] = "Bỏ ẩn bài viết" if instance.status == Status.ARCHIVED else "Ẩn bài viết"
        extra["revisions"] = instance.revisions.all()[:10]

    old_data = {}
    if instance:
        old_data = {
            "title": instance.title,
            "summary": instance.summary,
            "content_md": instance.content_md,
            "status": instance.status,
            "story_type": instance.story_type,
            "published_at": instance.published_at.isoformat() if instance.published_at else None,
        }

    def after(obj, form):
        is_new = not bool(instance and instance.pk)
        if is_new and not obj.author_id:
            obj.author = request.user

        # Quy tắc duyệt hai người (Two-editor rule) cho Story
        if obj.status == Status.PUBLISHED:
            is_admin_or_super = request.user.is_superuser or request.user.role == "admin"
            if obj.author_id == request.user.pk and not is_admin_or_super:
                obj.status = Status.PENDING
                obj.save(update_fields=["status", "author"])
                messages.warning(request, "Quy tắc duyệt hai người (Two-editor rule): Bài viết đã được lưu và chuyển sang trạng thái 'Chờ duyệt xuất bản'. Cần một biên tập viên khác hoặc Quản trị viên duyệt xuất bản.")
            else:
                obj.reviewer = request.user
                if not obj.published_at:
                    obj.published_at = timezone.now()
                obj.save(update_fields=["reviewer", "published_at", "author"])
        else:
            obj.save(update_fields=["author"])

        # Lưu lịch sử phiên bản (Revision snapshot)
        Revision.objects.create(
            entity_type="story",
            kind=Revision.Kind.CREATE if is_new else Revision.Kind.UPDATE,
            story=obj,
            title=obj.title,
            data={
                "title": obj.title,
                "summary": obj.summary,
                "content_md": obj.content_md,
                "status": obj.status,
                "story_type": obj.story_type,
                "published_at": obj.published_at.isoformat() if obj.published_at else None,
            },
            previous_data=old_data,
            state=Revision.State.APPROVED if obj.status == Status.PUBLISHED else Revision.State.PENDING,
            author=request.user,
            author_role="editor",
            reviewer=request.user if obj.status == Status.PUBLISHED else None,
            reviewed_at=timezone.now() if obj.status == Status.PUBLISHED else None,
        )

    return _crud_form(
        request, sf.StoryForm, instance,
        title="Câu chuyện (Story)",
        back=reverse("staff:story_list"),
        action_name="story",
        extra=extra,
        after_save=after,
    )


@editor_required
def video_list(request):
    qs = Video.objects.prefetch_related("persons", "companies")
    q = request.GET.get("q", "")
    if q:
        qs = qs.filter(search_text__contains=normalize(q))
    if request.GET.get("loi"):
        qs = qs.filter(availability="unavailable")
    return render(request, "staff/video_list.html", {"page": _page(request, qs.order_by("-created_at")), "q": q})


def _fill_metadata(video, force=False):
    info = video_lib.parse_video_url(video.url)
    if not info:
        return "unknown"
    meta, status = video_lib.fetch_oembed(video.url, info.platform)
    if meta:
        if force or not video.title or video.title == "Video":
            video.title = meta["title"] or video.title
        if not video.channel_name:
            video.channel_name = meta["channel_name"]
        if meta.get("thumbnail_url") and (force or not video.thumbnail_url or video.thumbnail_url == info.thumbnail_url):
            video.thumbnail_url = meta["thumbnail_url"][:500]
        if meta.get("duration_seconds") and not video.duration_seconds:
            video.duration_seconds = meta["duration_seconds"]
    video.availability = status
    video.last_checked_at = timezone.now()
    return status


@editor_required
def video_form(request, pk=None):
    instance = get_object_or_404(Video, pk=pk) if pk else None

    def after(video, form):
        video.duration_seconds = form.cleaned_data.get("duration") or video.duration_seconds
        if not video.title or not video.thumbnail_url or not instance:
            _fill_metadata(video)
        if not video.title:
            video.title = "Video"
        video.save()
        people = [services.find_person(n) for n in request.POST.getlist("person_name") if n.strip()]
        companies = [services.find_company(n) for n in request.POST.getlist("company_name") if n.strip()]
        video.persons.set([p for p in people if p])
        video.companies.set([c for c in companies if c])

    extra = {
        "linked_people": [services.person_label(p) for p in instance.persons.all()] if instance else [],
        "linked_companies": [services.company_label(c) for c in instance.companies.all()] if instance else [],
    }
    if instance:
        extra["delete_url"] = reverse("staff:video_delete", args=[instance.pk])
        extra["toggle_url"] = reverse("staff:video_toggle_status", args=[instance.pk])
        extra["toggle_label"] = "Hiện video" if instance.status == Video.VStatus.HIDDEN else "Ẩn video"
    return _crud_form(request, sf.VideoForm, instance, title="Video", back=reverse("staff:video_list"),
                      action_name="video", template="staff/video_form.html", after_save=after, extra=extra)


@editor_required
@require_POST
def video_check(request, pk):
    video = get_object_or_404(Video, pk=pk)
    status = _fill_metadata(video, force=request.POST.get("force") == "1")
    video.save()
    messages.info(request, {"ok": "Link hoạt động, đã cập nhật thông tin.",
                            "unavailable": "Link không còn xem được — video sẽ tự ẩn khỏi trang công khai.",
                            "unknown": "Không kiểm tra được (nền tảng không hỗ trợ hoặc lỗi mạng)."}[status])
    return redirect("staff:video_list")


@editor_required
@require_POST
def sector_toggle_status(request, pk):
    sector = get_object_or_404(Sector, pk=pk)
    sector.is_active = not sector.is_active
    sector.save(update_fields=["is_active", "updated_at"])
    action = "activate" if sector.is_active else "deactivate"
    msg = f"Đã kích hoạt ngành nghề: {sector.name}" if sector.is_active else f"Đã ẩn (ngừng dùng) ngành nghề: {sector.name}"
    log(request.user, f"sector.{action}", sector, sector.name, request=request)
    messages.success(request, msg)
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    return redirect(next_url or "staff:sector_list")


@editor_required
@require_POST
def sector_delete(request, pk):
    sector = get_object_or_404(Sector, pk=pk)
    name = sector.name
    if sector.children.exists():
        messages.error(request, f"Không thể xóa ngành “{name}” vì còn {sector.children.count()} phân ngành trực thuộc. Hãy xóa hoặc chuyển các phân ngành này trước.")
        return redirect("staff:sector_list")
    sector.delete()
    log(request.user, "sector.delete", None, name, request=request)
    messages.success(request, f"Đã xóa ngành nghề: {name}")
    return redirect("staff:sector_list")


@editor_required
@require_POST
def association_toggle_status(request, pk):
    association = get_object_or_404(Association, pk=pk)
    if association.status == Status.ARCHIVED:
        association.status = Status.PUBLISHED
        action = "unarchive"
        msg = f"Đã bỏ ẩn (công bố lại) hiệp hội: {association.name}"
    else:
        association.status = Status.ARCHIVED
        action = "archive"
        msg = f"Đã ẩn hiệp hội: {association.name}"
    association.save(update_fields=["status", "updated_at"])
    log(request.user, f"association.{action}", association, association.name, request=request)
    messages.success(request, msg)
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    return redirect(next_url or "staff:association_list")


@editor_required
@require_POST
def association_delete(request, pk):
    association = get_object_or_404(Association, pk=pk)
    name = association.name
    association.delete()
    log(request.user, "association.delete", None, name, request=request)
    messages.success(request, f"Đã xóa vĩnh viễn hiệp hội: {name}")
    return redirect("staff:association_list")


@editor_required
@require_POST
def event_toggle_status(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.status == Event.EventStatus.ARCHIVED:
        event.status = Event.EventStatus.PUBLISHED
        action = "unarchive"
        msg = f"Đã bỏ ẩn (công bố lại) sự kiện: {event.title}"
    else:
        event.status = Event.EventStatus.ARCHIVED
        action = "archive"
        msg = f"Đã ẩn sự kiện: {event.title}"
    event.save(update_fields=["status", "updated_at"])
    log(request.user, f"event.{action}", event, event.title, request=request)
    messages.success(request, msg)
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    return redirect(next_url or "staff:event_list")


@editor_required
@require_POST
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    title = event.title
    event.delete()
    log(request.user, "event.delete", None, title, request=request)
    messages.success(request, f"Đã xóa sự kiện: {title}")
    return redirect("staff:event_list")


@editor_required
@require_POST
def video_toggle_status(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if video.status == Video.VStatus.HIDDEN:
        video.status = Video.VStatus.PUBLISHED
        action = "unhide"
        msg = f"Đã hiện lại video: {video.title}"
    else:
        video.status = Video.VStatus.HIDDEN
        action = "hide"
        msg = f"Đã ẩn video: {video.title}"
    video.save(update_fields=["status"])
    log(request.user, f"video.{action}", video, video.title, request=request)
    messages.success(request, msg)
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    return redirect(next_url or "staff:video_list")


@editor_required
@require_POST
def video_delete(request, pk):
    video = get_object_or_404(Video, pk=pk)
    title = video.title
    video.delete()
    log(request.user, "video.delete", None, title, request=request)
    messages.success(request, f"Đã xóa video: {title}")
    return redirect("staff:video_list")


@editor_required
@require_POST
def story_toggle_status(request, pk):
    story = get_object_or_404(Story, pk=pk)
    if story.status == Status.ARCHIVED:
        story.status = Status.PUBLISHED
        action = "unarchive"
        msg = f"Đã công bố lại câu chuyện: {story.title}"
    else:
        story.status = Status.ARCHIVED
        action = "archive"
        msg = f"Đã ẩn câu chuyện: {story.title}"
    story.save(update_fields=["status", "updated_at"])
    log(request.user, f"story.{action}", story, str(story), request=request)
    messages.success(request, msg)
    next_url = request.POST.get("next")
    return redirect(next_url or "staff:story_list")


@editor_required
@require_POST
def story_delete(request, pk):
    story = get_object_or_404(Story, pk=pk)
    title = story.title
    story.delete()
    log(request.user, "story.delete", None, title, request=request)
    messages.success(request, f"Đã xóa bài viết: {title}")
    return redirect("staff:story_list")


# =========================================================================== postcard (bưu thiếp danh ngôn & triết lý)
@editor_required
def postcard_list(request):
    qs = Postcard.objects.select_related("person", "company")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.search(q)
    topic = request.GET.get("chu-de", "").strip()
    if topic in Postcard.Topic.values:
        qs = qs.filter(topic=topic)
    status = request.GET.get("trang-thai", "").strip()
    if status in Status.values:
        qs = qs.filter(status=status)

    total_postcards = qs.count()
    return render(request, "staff/postcard_list.html", {
        "page": _page(request, qs),
        "q": q,
        "topic": topic,
        "topics": Postcard.Topic.choices,
        "status": status,
        "statuses": Status.choices,
        "total_postcards": total_postcards,
    })


@editor_required
def postcard_form(request, pk=None):
    instance = get_object_or_404(Postcard, pk=pk) if pk else None
    extra = {}
    if instance:
        extra["delete_url"] = reverse("staff:postcard_delete", args=[instance.pk])
        extra["toggle_url"] = reverse("staff:postcard_toggle_status", args=[instance.pk])
        extra["toggle_label"] = "Bỏ ẩn bưu thiếp" if instance.status == Status.ARCHIVED else "Ẩn bưu thiếp"
    return _crud_form(
        request, sf.PostcardForm, instance,
        title="Bưu thiếp danh ngôn (Postcard)",
        back=reverse("staff:postcard_list"),
        action_name="postcard",
        extra=extra,
    )


@editor_required
@require_POST
def postcard_toggle_status(request, pk):
    postcard = get_object_or_404(Postcard, pk=pk)
    if postcard.status == Status.ARCHIVED:
        postcard.status = Status.PUBLISHED
        action = "unarchive"
        msg = f"Đã hiển thị lại bưu thiếp: {postcard.title}"
    else:
        postcard.status = Status.ARCHIVED
        action = "archive"
        msg = f"Đã ẩn bưu thiếp: {postcard.title}"
    postcard.save(update_fields=["status", "updated_at"])
    log(request.user, f"postcard.{action}", postcard, str(postcard), request=request)
    messages.success(request, msg)
    next_url = request.POST.get("next")
    return redirect(next_url or "staff:postcard_list")


@editor_required
@require_POST
def postcard_delete(request, pk):
    postcard = get_object_or_404(Postcard, pk=pk)
    title = postcard.title
    postcard.delete()
    log(request.user, "postcard.delete", None, title, request=request)
    messages.success(request, f"Đã xóa bưu thiếp: {title}")
    return redirect("staff:postcard_list")


# =========================================================================== podcast (chương trình phát thanh doanh nhân)
@editor_required
def podcast_list(request):
    qs = Podcast.objects.select_related("guest_person", "company")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.search(q)
    series = request.GET.get("chu-de", "").strip()
    if series in Podcast.SeriesType.values:
        qs = qs.filter(series_type=series)
    status = request.GET.get("trang-thai", "").strip()
    if status in Status.values:
        qs = qs.filter(status=status)

    total_podcasts = qs.count()
    return render(request, "staff/podcast_list.html", {
        "page": _page(request, qs),
        "q": q,
        "series": series,
        "series_types": Podcast.SeriesType.choices,
        "status": status,
        "statuses": Status.choices,
        "total_podcasts": total_podcasts,
    })


@editor_required
def podcast_form(request, pk=None):
    instance = get_object_or_404(Podcast, pk=pk) if pk else None
    extra = {}
    if instance:
        extra["delete_url"] = reverse("staff:podcast_delete", args=[instance.pk])
        extra["toggle_url"] = reverse("staff:podcast_toggle_status", args=[instance.pk])
        extra["toggle_label"] = "Bỏ ẩn tập podcast" if instance.status == Status.ARCHIVED else "Ẩn tập podcast"
    return _crud_form(
        request, sf.PodcastForm, instance,
        title="Tập Podcast Doanh nhân",
        back=reverse("staff:podcast_list"),
        action_name="podcast",
        extra=extra,
    )


@editor_required
@require_POST
def podcast_toggle_status(request, pk):
    podcast = get_object_or_404(Podcast, pk=pk)
    if podcast.status == Status.ARCHIVED:
        podcast.status = Status.PUBLISHED
        action = "unarchive"
        msg = f"Đã hiển thị lại tập podcast: {podcast.title}"
    else:
        podcast.status = Status.ARCHIVED
        action = "archive"
        msg = f"Đã ẩn tập podcast: {podcast.title}"
    podcast.save(update_fields=["status", "updated_at"])
    log(request.user, f"podcast.{action}", podcast, str(podcast), request=request)
    messages.success(request, msg)
    next_url = request.POST.get("next")
    return redirect(next_url or "staff:podcast_list")


@editor_required
@require_POST
def podcast_delete(request, pk):
    podcast = get_object_or_404(Podcast, pk=pk)
    title = podcast.title
    podcast.delete()
    log(request.user, "podcast.delete", None, title, request=request)
    messages.success(request, f"Đã xóa tập podcast: {title}")
    return redirect("staff:podcast_list")






# =========================================================================== phỏng vấn, liên hệ, yêu cầu dữ liệu
@editor_required
def interviews(request):
    state = request.GET.get("trang-thai", "")
    qs = InterviewRequest.objects.select_related("assignee", "video")
    if state in InterviewRequest.State.values:
        qs = qs.filter(state=state)
    return render(request, "staff/interviews.html", {"page": _page(request, qs), "state": state,
                                                     "states": InterviewRequest.State.choices})


@editor_required
def interview_detail(request, pk):
    obj = get_object_or_404(InterviewRequest, pk=pk)
    actions = []
    if obj.related_story_id:
        actions.append({"label": f"📄 Xem Story: {obj.related_story.title}", "url": reverse("staff:story_edit", args=[obj.related_story_id]), "class": "btn-outline"})
    else:
        actions.append({"label": "✨ Khởi tạo bài viết Story từ yêu cầu này →", "url": reverse("staff:interview_create_story", args=[obj.pk]), "class": "btn-gold"})

    if obj.person_id:
        actions.append({"label": f"👤 Xem hồ sơ Doanh nhân: {obj.person.full_name}", "url": reverse("staff:person_edit", args=[obj.person_id]), "class": "btn-outline"})
    else:
        actions.append({"label": "👤 Khởi tạo hồ sơ Doanh nhân từ yêu cầu này →", "url": reverse("staff:interview_create_person", args=[obj.pk]), "class": "btn-outline"})

    return _crud_form(request, sf.InterviewStaffForm, obj, title=f"Yêu cầu phỏng vấn: {obj.full_name}",
                      back=reverse("staff:interviews"), action_name="interview", template="staff/record_form.html",
                      extra={"record": obj, "record_fields": [
                          ("Họ và tên", obj.full_name), ("Chức vụ", obj.title), ("Doanh nghiệp", obj.company),
                          ("Điện thoại", obj.phone), ("Email", obj.email), ("Nội dung", obj.get_kind_display()),
                          ("Hình thức", obj.get_format_display()),
                          ("Địa chỉ ghi hình", obj.address or "Trực tuyến / Không yêu cầu"),
                          ("Thời gian thuận tiện", timezone.localtime(obj.preferred_time).strftime("%H:%M ngày %d/%m/%Y") if obj.preferred_time else "Chưa chọn"),
                          ("Tư liệu", obj.reference_url), ("Câu chuyện", obj.story),
                          ("Gửi lúc", timezone.localtime(obj.created_at).strftime("%d/%m/%Y %H:%M"))],
                          "record_actions": actions})


@editor_required
def interview_create_story(request, pk):
    obj = get_object_or_404(InterviewRequest, pk=pk)
    if obj.related_story_id:
        messages.info(request, "Yêu cầu phỏng vấn này đã có bài viết Story liên kết.")
        return redirect("staff:story_edit", pk=obj.related_story_id)

    title = f"Hành trình kinh doanh của {obj.full_name} ({obj.company})"
    summary = (obj.story[:200] + "...") if len(obj.story) > 200 else (obj.story or f"Câu chuyện khởi nghiệp và phát triển của doanh nhân {obj.full_name} tại {obj.company}.")
    content = (
        f"### Khởi đầu & Cơ duyên\n\n{obj.story or 'Đang cập nhật nội dung phỏng vấn...'}\n\n"
        f"### Doanh nghiệp & Hoạt động hiện tại\n\n- **Doanh nghiệp:** {obj.company}\n- **Chức vụ:** {obj.title or 'Lãnh đạo doanh nghiệp'}\n\n"
        f"*Tư liệu phỏng vấn ghi nhận lúc {timezone.localtime(obj.created_at).strftime('%d/%m/%Y')} từ cổng liên hệ ghi hình doanhnhan.wiki.*"
    )

    story = Story.objects.create(
        title=title,
        story_type=Story.StoryType.JOURNEY if obj.kind == InterviewRequest.Kind.COMPANY else Story.StoryType.INTERVIEW,
        summary=summary,
        content_md=content,
        author_name=request.user.full_name or "Ban Biên tập",
        author=request.user,
        source_name="Tòa soạn doanhnhan.wiki",
        source_url=obj.reference_url,
        status=Status.DRAFT,
    )
    obj.related_story = story
    if obj.state == InterviewRequest.State.NEW:
        obj.state = InterviewRequest.State.SCHEDULED
    obj.save(update_fields=["related_story", "state"])

    log(request.user, "interview.create_story", story, f"Khởi tạo Story từ yêu cầu #{obj.pk}", request=request)
    messages.success(request, f"Đã khởi tạo bản nháp Story từ yêu cầu của {obj.full_name}. Bạn có thể tiếp tục biên tập tại đây.")
    return redirect("staff:story_edit", pk=story.pk)


@editor_required
def interview_create_person(request, pk):
    obj = get_object_or_404(InterviewRequest, pk=pk)
    if obj.person_id:
        messages.info(request, "Yêu cầu phỏng vấn này đã có hồ sơ doanh nhân liên kết.")
        return redirect("staff:person_edit", pk=obj.person_id)

    person = Person.objects.create(
        full_name=obj.full_name,
        headline=f"{obj.title} tại {obj.company}" if obj.title else f"Đại diện {obj.company}",
        phone=obj.phone,
        email_public=obj.email,
        website=obj.reference_url,
        status=Status.DRAFT,
    )
    if obj.story:
        person.sections.create(key="khoi_dau", body_md=obj.story, sort_order=1)

    obj.person = person
    obj.save(update_fields=["person"])

    log(request.user, "interview.create_person", person, f"Khởi tạo Doanh nhân từ yêu cầu #{obj.pk}", request=request)
    messages.success(request, f"Đã khởi tạo bản nháp hồ sơ doanh nhân {person.full_name}. Bạn có thể hoàn thiện 7 phần mục tại đây.")
    return redirect("staff:person_edit", pk=person.pk)


@editor_required
def contacts(request):
    qs = ContactMessage.objects.all()
    if not request.GET.get("tat-ca"):
        qs = qs.filter(handled=False)
    return render(request, "staff/contacts.html", {"page": _page(request, qs)})


@editor_required
def contact_detail(request, pk):
    obj = get_object_or_404(ContactMessage, pk=pk)
    fields = [
        ("Chủ đề", obj.get_topic_display()),
        ("Họ và tên", obj.full_name),
        ("Tổ chức", obj.organization or "—"),
        ("Email", obj.email),
        ("Điện thoại", obj.phone),
    ]
    if obj.source_url:
        fields.append(("Nguồn đối chiếu / kiểm chứng", obj.source_url))
    fields.extend([
        ("Nội dung", obj.message),
        ("Gửi lúc", timezone.localtime(obj.created_at).strftime("%d/%m/%Y %H:%M")),
    ])
    return _crud_form(request, sf.ContactStaffForm, obj, title=f"Liên hệ: {obj.get_topic_display()}",
                      back=reverse("staff:contacts"), action_name="contact", template="staff/record_form.html",
                      extra={"record": obj, "record_fields": fields})


@admin_required
def data_requests(request):
    return render(request, "staff/data_requests.html", {"page": _page(request, DataRequest.objects.all())})


@admin_required
def data_request_detail(request, pk):
    obj = get_object_or_404(DataRequest, pk=pk)

    def after(o, form):
        if o.state in ("done", "rejected") and not o.resolved_at:
            o.resolved_at, o.handled_by = timezone.now(), request.user
            o.save(update_fields=["resolved_at", "handled_by"])

    return _crud_form(request, sf.DataRequestStaffForm, obj, title=f"Yêu cầu dữ liệu #{obj.pk}",
                      back=reverse("staff:data_requests"), action_name="data_request", template="staff/record_form.html",
                      after_save=after, extra={"record": obj, "record_fields": [
                          ("Yêu cầu", obj.get_kind_display()), ("Họ và tên", obj.full_name), ("Email", obj.email),
                          ("Hồ sơ liên quan", obj.profile_url), ("Chi tiết", obj.detail),
                          ("Gửi lúc", timezone.localtime(obj.created_at).strftime("%d/%m/%Y %H:%M"))]})


# =========================================================================== người dùng & vai trò
@admin_required
def users(request):
    qs = User.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(email__icontains=q) | Q(full_name__icontains=q))
    role = request.GET.get("vai-tro", "")
    if role in User.Role.values:
        qs = qs.filter(role=role)
    return render(request, "staff/users.html", {
        "page": _page(request, qs), "q": q, "role": role, "roles": User.Role.choices,
        "requests": RoleChangeRequest.objects.filter(status="pending").select_related("target", "requested_by")})


@admin_required
@require_POST
def user_update(request, pk):
    target = get_object_or_404(User, pk=pk)
    action = request.POST.get("action")
    if target == request.user and action in ("role", "suspend"):
        messages.error(request, "Không thể tự đổi vai trò hoặc tự khóa tài khoản của mình.")
        return redirect("staff:users")
    if action == "role":
        new_role = request.POST.get("role")
        if new_role not in User.Role.values or new_role == target.role:
            return redirect("staff:users")
        if new_role == User.Role.ADMIN or target.role == User.Role.ADMIN:
            RoleChangeRequest.objects.create(target=target, new_role=new_role, requested_by=request.user)
            log(request.user, "role.request", target, target.email, {"new_role": new_role}, request=request)
            messages.info(request, "Thay đổi liên quan quyền Quản trị viên cần một quản trị viên khác xác nhận.")
        else:
            old = target.role
            target.role = new_role
            target.save(update_fields=["role"])
            log(request.user, "role.change", target, target.email, {"from": old, "to": new_role}, request=request)
            messages.success(request, f"Đã đổi vai trò của {target.email}.")
    elif action == "suspend":
        target.status = User.Status.SUSPENDED
        target.save(update_fields=["status"])
        log(request.user, "account.suspend", target, target.email, request=request)
        messages.success(request, f"Đã khóa {target.email}.")
    elif action == "activate":
        target.status = User.Status.ACTIVE
        target.failed_logins, target.locked_until = 0, None
        target.save(update_fields=["status", "failed_logins", "locked_until"])
        log(request.user, "account.activate", target, target.email, request=request)
        messages.success(request, f"Đã mở khóa {target.email}.")
    return redirect("staff:users")


@admin_required
@require_POST
def role_request_decide(request, pk):
    rq = get_object_or_404(RoleChangeRequest, pk=pk, status="pending")
    if request.POST.get("action") == "cancel":
        rq.status, rq.resolved_at = "cancelled", timezone.now()
        rq.save()
        log(request.user, "role.cancel", rq.target, rq.target.email, request=request)
        return redirect("staff:users")
    if rq.requested_by_id == request.user.pk:
        messages.error(request, "Cần một quản trị viên khác (không phải người đề nghị) xác nhận.")
        return redirect("staff:users")
    with transaction.atomic():
        target = rq.target
        old = target.role
        target.role = rq.new_role
        target.is_staff = rq.new_role == User.Role.ADMIN or target.is_superuser
        target.save(update_fields=["role", "is_staff"])
        rq.status, rq.confirmed_by, rq.resolved_at = "done", request.user, timezone.now()
        rq.save()
    log(request.user, "role.confirm", target, target.email, {"from": old, "to": rq.new_role,
                                                            "requested_by": rq.requested_by.email}, request=request)
    messages.success(request, f"Đã xác nhận vai trò mới cho {target.email}.")
    return redirect("staff:users")


# =========================================================================== trang tài trợ
@admin_required
def donation(request):
    settings_obj = DonationSettings.load()
    form = sf.DonationSettingsForm(request.POST or None, instance=settings_obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.updated_by = request.user
        obj.save()
        log(request.user, "donation.update_text", obj, "Trang tài trợ", request=request)
        messages.success(request, "Đã lưu nội dung trang tài trợ.")
        return redirect("staff:donation")
    return render(request, "staff/donation.html", {
        "form": form, "accounts": DonationAccount.objects.select_related("created_by", "approved_by").order_by("-created_at"),
        "account_form": sf.DonationAccountForm()})


@admin_required
@require_POST
def donation_account_new(request):
    form = sf.DonationAccountForm(request.POST, request.FILES)
    if form.is_valid():
        acc = form.save(commit=False)
        acc.created_by = request.user
        acc.state = DonationAccount.State.PENDING
        replaces = DonationAccount.objects.filter(pk=request.POST.get("replaces"), state="active").first()
        acc.replaces = replaces
        acc.save()
        log(request.user, "donation.account_create", acc, str(acc), request=request)
        messages.info(request, "Đã tạo tài khoản nhận tài trợ. Cần một quản trị viên khác duyệt trước khi hiển thị.")
    else:
        messages.error(request, "Thông tin tài khoản chưa hợp lệ: " + "; ".join(
            f"{form.fields[k].label}: {' '.join(v)}" for k, v in form.errors.items()))
    return redirect("staff:donation")


@admin_required
@require_POST
def donation_account_decide(request, pk):
    acc = get_object_or_404(DonationAccount, pk=pk)
    action = request.POST.get("action")
    if action == "approve" and acc.state == DonationAccount.State.PENDING:
        if acc.created_by_id == request.user.pk:
            messages.error(request, "Người tạo không thể tự duyệt. Cần một quản trị viên khác.")
            return redirect("staff:donation")
        with transaction.atomic():
            acc.state, acc.approved_by, acc.approved_at = DonationAccount.State.ACTIVE, request.user, timezone.now()
            acc.save()
            if acc.replaces_id:
                DonationAccount.objects.filter(pk=acc.replaces_id).update(state=DonationAccount.State.RETIRED)
        log(request.user, "donation.account_approve", acc, str(acc), request=request)
        messages.success(request, "Đã duyệt — tài khoản hiển thị trên trang Donate.")
    elif action == "retire" and acc.state != DonationAccount.State.RETIRED:
        acc.state = DonationAccount.State.RETIRED
        acc.save()
        log(request.user, "donation.account_retire", acc, str(acc), request=request)
        messages.success(request, "Đã ngừng hiển thị tài khoản.")
    return redirect("staff:donation")


# =========================================================================== chính sách
@admin_required
def policies(request):
    docs = PolicyDocument.objects.prefetch_related("versions")
    return render(request, "staff/policies.html", {"documents": docs, "now": timezone.now()})


@admin_required
def policy_document_form(request, pk=None):
    instance = get_object_or_404(PolicyDocument, pk=pk) if pk else None
    return _crud_form(request, sf.PolicyDocumentForm, instance, title="Văn bản chính sách",
                      back=reverse("staff:policies"), action_name="policy_document")


@admin_required
def policy_version_form(request, doc_pk, pk=None):
    document = get_object_or_404(PolicyDocument, pk=doc_pk)
    instance = get_object_or_404(PolicyVersion, pk=pk, document=document) if pk else None
    if instance and instance.status == "published" and instance.effective_at <= timezone.now():
        messages.info(request, "Phiên bản đã có hiệu lực không sửa được — hãy tạo phiên bản mới.")
        return redirect("staff:policies")
    if instance is None and request.method == "GET":
        latest = document.versions.first()
        instance_initial = PolicyVersion(document=document, body_md=latest.body_md if latest else "",
                                         summary_points=latest.summary_points if latest else "")
    else:
        instance_initial = instance or PolicyVersion(document=document)

    def after(obj, form):
        if not obj.created_by_id:
            obj.created_by = request.user
            obj.save(update_fields=["created_by"])
        cache.delete("required_policy_versions")

    return _crud_form(request, sf.PolicyVersionForm, instance_initial, title=f"{document.title} – phiên bản",
                      back=reverse("staff:policies"), action_name="policy_version", after_save=after)


# =========================================================================== cài đặt, nhật ký
@admin_required
def site_settings(request):
    return _crud_form(request, sf.SiteSettingsForm, SiteSettings.load(), title="Cài đặt chung",
                      back=reverse("staff:site_settings"), action_name="site_settings")


@admin_required
def audit_log(request):
    qs = AuditLog.objects.select_related("actor")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(action__icontains=q) | Q(target_label__icontains=q) | Q(actor__email__icontains=q))
    return render(request, "staff/audit_log.html", {"page": _page(request, qs, 50), "q": q})


# =========================================================================== trợ lý AI viết bài (Hội thoại Chat)
@editor_required
@require_POST
def ai_assistant(request):
    """Trợ lý hội thoại AI hỗ trợ ban biên tập viết bài nhanh hơn (chỉ chạy khi admin yêu cầu)."""
    import json
    from apps.common.ai import chat

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        body = request.POST

    messages = body.get("messages", [])
    context_info = body.get("context", {})

    # Tương thích nếu client gửi prompt/notes/action/target_name đơn lẻ
    if not messages:
        action = body.get("action", "")
        notes = body.get("notes", "")
        prompt = body.get("prompt", "")
        target_name = body.get("target_name", "")
        target_type = body.get("target_type", "")

        parts = []
        if action:
            parts.append(f"Yêu cầu: {action}")
        if notes:
            parts.append(f"Ghi chú: {notes}")
        if prompt:
            parts.append(prompt)

        user_text = " - ".join(parts) if parts else "Xin chào"
        if target_name:
            user_text = f"Biên soạn cho {target_name}: {user_text}"
            if not context_info:
                context_info = {"title": target_name, "type": target_type}
        messages = [{"role": "user", "content": user_text}]

    result = chat(messages=messages, context_info=context_info)
    result["content"] = result.get("reply", "")
    return JsonResponse(result)


@editor_required
def ai_config_api(request):
    """API xem và cập nhật cấu hình Google Gemini AI trực tiếp từ giao diện quản trị (không cần sửa file .env)."""
    import json
    from apps.common.ai import get_ai_config
    from apps.sitecontent.models import SiteSettings
    from apps.moderation.models import AuditLog

    if request.method == "POST":
        if not request.user.is_admin_role:
            return JsonResponse({"ok": False, "error": "Chỉ Quản trị viên (Admin) mới có quyền thay đổi mã API Key."}, status=403)
        try:
            body = json.loads(request.body.decode("utf-8")) if request.body else {}
        except Exception:
            body = request.POST

        site = SiteSettings.load()
        if "gemini_api_key" in body:
            site.gemini_api_key = str(body.get("gemini_api_key", "")).strip()
        if "gemini_model" in body and body.get("gemini_model"):
            site.gemini_model = str(body.get("gemini_model", "")).strip()
        site.save()

        AuditLog.objects.create(
            actor=request.user,
            action="ai_config_update",
            target_label="Cấu hình Google Gemini AI",
            detail={"model": site.gemini_model, "has_key": bool(site.gemini_api_key)},
        )

        return JsonResponse({
            "ok": True,
            "message": "Đã lưu cấu hình Google Gemini API Key thành công!",
            "config": get_ai_config(),
        })

    # GET
    cfg = get_ai_config()
    cfg["is_admin"] = request.user.is_admin_role
    return JsonResponse({"ok": True, "config": cfg})


# =========================================================================== Thu thập dữ liệu Doanh nhân & Doanh nghiệp bằng AI
@editor_required
def ai_crawler(request):
    """Giao diện công cụ cào và trích xuất dữ liệu AI."""
    from apps.common.ai import get_ai_config
    provinces = Province.objects.all().order_by("name")
    sectors = Sector.objects.filter(is_active=True).order_by("name")
    roles = PersonCompany.Role.choices
    size_choices = Company.Size.choices
    recent_logs = AuditLog.objects.filter(action="ai.crawler_import").select_related("actor").order_by("-created_at")[:10]
    return render(request, "staff/ai_crawler.html", {
        "provinces": provinces,
        "sectors": sectors,
        "roles": roles,
        "size_choices": size_choices,
        "recent_logs": recent_logs,
        "ai_config": get_ai_config(),
    })


@editor_required
@require_POST
def ai_crawler_analyze(request):
    """API cào bài viết và gọi AI bóc tách dữ liệu có cấu trúc."""
    import json
    import logging
    from apps.common.crawler import fetch_article, extract_entities_with_ai, save_crawled_data
    from django.http import QueryDict

    crawler_logger = logging.getLogger(__name__)

    try:
        body = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        body = request.POST

    url_or_text = (body.get("url_or_text") or "").strip()
    hints = (body.get("hints") or "").strip()
    auto_publish = body.get("auto_publish") in (True, "true", "1", 1)

    if not url_or_text:
        return JsonResponse({"ok": False, "error": "Vui lòng nhập đường dẫn URL bài báo hoặc dán văn bản bài viết."}, status=400)

    try:
        article_data = fetch_article(url_or_text)
    except Exception as exc:
        return JsonResponse({"ok": False, "error": f"Không thể tải nội dung từ đường dẫn này: {exc}"}, status=400)

    if not article_data.get("text"):
        return JsonResponse({"ok": False, "error": "Không trích xuất được văn bản từ bài viết. Vui lòng kiểm tra lại đường dẫn hoặc dán trực tiếp nội dung."}, status=400)

    try:
        result = extract_entities_with_ai(article_data, hints=hints)

        # Chế độ tự động xuất bản 1-Click
        if auto_publish:
            p_data = result.get("person") or {}
            c_data = result.get("company") or {}
            rel = result.get("relationship") or {}
            src = result.get("source") or {}

            p_name = str(p_data.get("full_name") or "").strip()
            c_legal = str(c_data.get("legal_name") or "").strip()
            c_brand = str(c_data.get("brand_name") or "").strip()
            c_name = c_legal or c_brand

            qd = QueryDict(mutable=True)
            qd["save_person"] = "1" if (result.get("has_person") and p_name) else "0"
            qd["person_full_name"] = p_name
            qd["person_headline"] = str(p_data.get("headline") or "").strip()
            qd["person_gender"] = str(p_data.get("gender") or "male").strip()
            qd["person_birth_year"] = str(p_data.get("birth_year") or "").strip()
            qd["person_hometown_id"] = str(p_data.get("hometown_id") or "").strip()
            qd["person_current_province_id"] = str(p_data.get("current_province_id") or "").strip()
            qd["person_summary"] = str(p_data.get("summary") or "").strip()
            qd["person_biography"] = str(p_data.get("biography") or "").strip()
            qd["person_journey"] = str(p_data.get("journey") or "").strip()
            qd["person_philosophy"] = str(p_data.get("philosophy") or "").strip()

            qd["save_company"] = "1" if (result.get("has_company") and c_name) else "0"
            qd["company_legal_name"] = c_name
            qd["company_brand_name"] = c_brand
            qd["company_tax_code"] = str(c_data.get("tax_code") or "").strip()
            qd["company_founded_year"] = str(c_data.get("founded_year") or "").strip()
            qd["company_province_id"] = str(c_data.get("province_id") or "").strip()
            qd["company_primary_sector_id"] = str(c_data.get("primary_sector_id") or "").strip()
            qd["company_size_band"] = str(c_data.get("size_band") or "").strip()
            qd["company_website"] = str(c_data.get("website") or "").strip()
            qd["company_address"] = str(c_data.get("address") or "").strip()
            qd["company_overview"] = str(c_data.get("overview") or "").strip()

            qd["relationship_role"] = str(rel.get("role") or "founder_ceo").strip()
            qd["relationship_title"] = str(rel.get("title") or "").strip()
            qd["relationship_start_year"] = str(rel.get("start_year") or "").strip()
            qd["status"] = "published"

            qd["source_url"] = str(article_data.get("url") or src.get("url") or "").strip()
            qd["source_title"] = str(article_data.get("title") or src.get("title") or "").strip()
            qd["source_publisher"] = str(article_data.get("publisher") or src.get("publisher") or "").strip()
            qd["image_url"] = str(article_data.get("image_url") or "").strip()

            # Tự động xuất bản bài viết Story
            qd["save_story"] = "1"
            st_data = result.get("story") or {}
            qd["story_title"] = str(st_data.get("title") or article_data.get("title") or "").strip()
            qd["story_summary"] = str(st_data.get("summary") or p_data.get("summary") or c_data.get("overview") or "").strip()
            qd["story_content_md"] = str(st_data.get("content_md") or "").strip()
            qd["story_type"] = str(st_data.get("story_type") or "portrait").strip()
            qd["cover_caption"] = str(article_data.get("title") or "").strip()

            m_list = p_data.get("milestones") or []
            if m_list:
                qd.setlist("milestone_year", [str(m.get("year", "")) for m in m_list if m.get("title")])
                qd.setlist("milestone_title", [str(m.get("title", "")).strip() for m in m_list if m.get("title")])
                qd.setlist("milestone_kind", [str(m.get("kind", "other")).strip() for m in m_list if m.get("title")])

            saved = save_crawled_data(qd, request.user)
            p_obj = saved.get("person")
            c_obj = saved.get("company")
            st_obj = saved.get("story")

            redirect_url = (
                st_obj.get_absolute_url() if st_obj else (
                    p_obj.get_absolute_url() if p_obj else (
                        c_obj.get_absolute_url() if c_obj else reverse("staff:story_list")
                    )
                )
            )
            title_display = st_obj.title if st_obj else (p_obj.full_name if p_obj else (c_obj.display_name if c_obj else ""))

            return JsonResponse({
                "ok": True,
                "auto_published": True,
                "story": {
                    "id": st_obj.pk if st_obj else None,
                    "title": st_obj.title if st_obj else "",
                    "url": st_obj.get_absolute_url() if st_obj else None,
                    "summary": st_obj.summary if st_obj else "",
                    "type_display": st_obj.get_story_type_display() if st_obj else "",
                    "cover_url": st_obj.cover_image.url if (st_obj and st_obj.cover_image) else (article_data.get("image_url") or ""),
                } if st_obj else None,
                "person": {
                    "id": p_obj.pk if p_obj else None,
                    "name": p_obj.full_name if p_obj else "",
                    "url": p_obj.get_absolute_url() if p_obj else None,
                } if p_obj else None,
                "company": {
                    "id": c_obj.pk if c_obj else None,
                    "name": c_obj.display_name if c_obj else "",
                    "url": c_obj.get_absolute_url() if c_obj else None,
                } if c_obj else None,
                "source": {
                    "title": article_data.get("title", ""),
                    "publisher": article_data.get("publisher", ""),
                    "url": article_data.get("url", ""),
                },
                "redirect_url": redirect_url,
                "message": f"🎉 Đã lên bài và xuất bản thành công: {title_display}!",
            })

        return JsonResponse({
            "ok": True,
            "data": result,
            "article": {
                "title": article_data.get("title", ""),
                "publisher": article_data.get("publisher", ""),
                "url": article_data.get("url", ""),
                "published_on": article_data.get("published_on", ""),
                "image_url": article_data.get("image_url", ""),
                "word_count": len(article_data.get("text", "").split()),
                "snippet": article_data.get("text", "")[:350] + ("..." if len(article_data.get("text", "")) > 350 else ""),
            }
        })
    except Exception as exc:
        crawler_logger.exception("Lỗi khi AI bóc tách dữ liệu")
        return JsonResponse({"ok": False, "error": f"Lỗi trong quá trình AI phân tích: {exc}"}, status=500)


@editor_required
@require_POST
def ai_crawler_save(request):
    """Lưu dữ liệu Doanh nhân & Doanh nghiệp đã được AI bóc tách và Admin phê duyệt."""
    from apps.common.crawler import save_crawled_data

    try:
        res = save_crawled_data(request.POST, request.user)
        person = res.get("person")
        company = res.get("company")
        story = res.get("story")

        msg_parts = []
        if story:
            msg_parts.append(f"Bài viết Story: <b>{story.title}</b>")
        if person:
            msg_parts.append(f"Doanh nhân: <b>{person.full_name}</b>")
        if company:
            msg_parts.append(f"Doanh nghiệp: <b>{company.display_name}</b>")

        summary = " và ".join(msg_parts) or "thành công"
        messages.success(request, mark_safe(f"🎉 Đã lưu thành công hồ sơ vào hệ thống: {summary}."))

        if story and story.status == Status.PUBLISHED:
            return redirect(story.get_absolute_url())
        elif person and person.status == Status.PUBLISHED:
            return redirect(person.get_absolute_url())
        elif company and company.status == Status.PUBLISHED:
            return redirect(company.get_absolute_url())
        elif person:
            return redirect("staff:person_edit", pk=person.pk)
        elif company:
            return redirect("staff:company_edit", pk=company.pk)
        elif story:
            return redirect("staff:story_edit", pk=story.pk)
        return redirect("staff:ai_crawler")
    except Exception as exc:
        messages.error(request, f"Lỗi khi lưu dữ liệu: {exc}")
        return redirect("staff:ai_crawler")




