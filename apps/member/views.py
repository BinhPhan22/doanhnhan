"""Khu vực thành viên: gửi hồ sơ, đề xuất sửa, theo dõi bản đã gửi, nhận quản lý hồ sơ."""
import mimetypes

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.common.forms import StyledFormMixin
from apps.common.notify import notify_editors
from apps.common.permissions import is_editor, member_required
from apps.common.validators import document_extensions, max_file_size
from apps.directory.models import Company, Person, Status
from apps.moderation import services
from apps.moderation.editor import NEW_COMPANY, NEW_PERSON, editor_context
from apps.moderation.models import ProfileClaim, Revision, log, private_storage

OPEN_STATES = [Revision.State.DRAFT, Revision.State.PENDING, Revision.State.NEEDS_INFO]


@login_required
def dashboard(request):
    user = request.user
    revisions = user.revisions.select_related("person", "company").order_by("-updated_at")
    return render(request, "member/dashboard.html", {
        "application": getattr(user, "application", None),
        "open_revisions": revisions.filter(state__in=OPEN_STATES),
        "closed_revisions": revisions.exclude(state__in=OPEN_STATES)[:30],
        "owned_people": user.owned_people.all(),
        "owned_companies": user.owned_companies.all(),
        "claims": user.claims.select_related("person"),
    })


def _render_editor(request, entity_type, data, *, errors=None, instance=None, revision=None, note=""):
    ctx = editor_context(entity_type, data, errors, staff=False, note=note)
    if instance is not None:
        heading = f"Đề xuất sửa: {instance}"
    else:
        heading = "Gửi hồ sơ doanh nhân" if entity_type == "person" else "Gửi trang doanh nghiệp"
    ctx.update({"instance": instance, "revision": revision, "heading": heading,
                "checks": services.compute_checks(entity_type, data, instance) if data.get("sections") else None})
    return render(request, "member/editor.html", ctx)


def _handle_post(request, entity_type, *, instance=None, revision=None, base=None):
    data, errors = services.parse_post(entity_type, request, base=base or {})
    note = request.POST.get("note", "").strip()
    as_draft = request.POST.get("action") == "draft"
    if errors and not as_draft:
        messages.error(request, "Vui lòng kiểm tra lại các ô được đánh dấu.")
        return _render_editor(request, entity_type, data, errors=errors, instance=instance, revision=revision, note=note)
    if revision:
        services.update_revision(revision, data, note=note, as_draft=as_draft, request=request)
    else:
        revision = services.submit_revision(entity_type=entity_type, data=data, author=request.user, instance=instance,
                                            note=note, as_draft=as_draft, request=request)
    if as_draft:
        messages.success(request, "Đã lưu bản nháp. Bạn có thể quay lại hoàn thiện bất cứ lúc nào.")
        return redirect("member:revision_edit", pk=revision.pk)
    notify_editors(f"Bản gửi mới: {revision.title}", "staff_new_revision", {"revision": revision})
    messages.success(request, "Đã gửi duyệt. Ban biên tập sẽ xem trong vài ngày làm việc; bạn sẽ nhận email khi có kết quả.")
    return redirect("member:dashboard")


@member_required
def person_create(request):
    if request.method == "POST":
        return _handle_post(request, "person")
    return _render_editor(request, "person", dict(NEW_PERSON))


@member_required
def company_create(request):
    if request.method == "POST":
        return _handle_post(request, "company")
    return _render_editor(request, "company", dict(NEW_COMPANY))


def _edit_existing(request, entity_type, instance):
    if instance.status == Status.ARCHIVED and not is_editor(request.user):
        raise Http404
    lookup = {"person": instance} if entity_type == "person" else {"company": instance}
    mine = Revision.objects.filter(author=request.user, state__in=OPEN_STATES, **lookup).first()
    if mine:
        messages.info(request, "Bạn đang có một bản đề xuất chưa xử lý cho trang này — tiếp tục chỉnh bản đó.")
        return redirect("member:revision_edit", pk=mine.pk)
    base = services.serialize(instance)
    if request.method == "POST":
        return _handle_post(request, entity_type, instance=instance, base=base)
    return _render_editor(request, entity_type, base, instance=instance)


@member_required
def person_edit(request, slug):
    return _edit_existing(request, "person", get_object_or_404(Person, slug=slug))


@member_required
def company_edit(request, slug):
    return _edit_existing(request, "company", get_object_or_404(Company, slug=slug))


def _own_revision(request, pk):
    revision = get_object_or_404(Revision, pk=pk)
    if revision.author_id != request.user.pk:
        raise PermissionDenied
    return revision


@member_required
def revision_edit(request, pk):
    revision = _own_revision(request, pk)
    if revision.state not in OPEN_STATES:
        return redirect("member:revision_view", pk=pk)
    if request.method == "POST":
        return _handle_post(request, revision.entity_type, instance=revision.target, revision=revision,
                            base=revision.data)
    return _render_editor(request, revision.entity_type, revision.data, instance=revision.target,
                          revision=revision, note=revision.note)


@login_required
def revision_view(request, pk):
    revision = _own_revision(request, pk)
    old = revision.previous_data if revision.state == Revision.State.APPROVED else (
        services.serialize(revision.target) if revision.target else {})
    return render(request, "member/revision_view.html", {
        "revision": revision, "diff": services.diff_payload(revision.entity_type, old, revision.data)})


@member_required
@require_POST
def revision_withdraw(request, pk):
    revision = _own_revision(request, pk)
    if revision.state in OPEN_STATES:
        log(request.user, "revision.withdraw", revision, revision.title, request=request)
        revision.delete()
        messages.info(request, "Đã rút bản gửi.")
    return redirect("member:dashboard")


# --------------------------------------------------------------------------- nhận quản lý hồ sơ
class ClaimForm(StyledFormMixin, forms.Form):
    evidence = forms.FileField(label="Giấy tờ chứng minh (PDF/JPG/PNG, tối đa 5 MB)",
                               validators=[document_extensions, max_file_size],
                               help_text="Ví dụ: ảnh CCCD che số, giấy đăng ký kinh doanh có tên bạn, thư xác nhận "
                                         "của hiệp hội. Tệp chỉ ban biên tập xem, không công khai.")
    note = forms.CharField(label="Ghi chú", required=False, widget=forms.Textarea(attrs={"rows": 3}))


@member_required
def claim(request, slug):
    person = get_object_or_404(Person, slug=slug, status=Status.PUBLISHED)
    if person.owner_id:
        messages.info(request, "Hồ sơ này đã có người quản lý. Nếu có nhầm lẫn, vui lòng liên hệ ban vận hành.")
        return redirect(person.get_absolute_url())
    if person.claims.filter(user=request.user, state="pending").exists():
        messages.info(request, "Bạn đã gửi yêu cầu nhận quản lý hồ sơ này, đang chờ duyệt.")
        return redirect("member:dashboard")
    form = ClaimForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        c = ProfileClaim.objects.create(person=person, user=request.user, evidence=form.cleaned_data["evidence"],
                                        note=form.cleaned_data["note"])
        log(request.user, "claim.submit", c, person.full_name, request=request)
        notify_editors(f"Yêu cầu nhận quản lý hồ sơ: {person.full_name}", "staff_new_claim", {"claim": c})
        messages.success(request, "Đã gửi yêu cầu nhận quản lý hồ sơ. Ban biên tập sẽ xác minh và phản hồi qua email.")
        return redirect("member:dashboard")
    return render(request, "member/claim.html", {"person": person, "form": form})


# --------------------------------------------------------------------------- ảnh chờ duyệt (riêng tư)
@login_required
def pending_image(request):
    path = request.GET.get("p", "")
    if not path.startswith("pending/") or ".." in path:
        raise Http404
    allowed = (is_editor(request.user) or path in request.session.get("stashed_uploads", [])
               or Revision.objects.filter(author=request.user).filter(
                   Q(data__portrait=path) | Q(data__logo=path) | Q(data__cover=path)).exists())
    if not allowed or not private_storage.exists(path):
        raise Http404
    content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    return FileResponse(private_storage.open(path, "rb"), content_type=content_type)
