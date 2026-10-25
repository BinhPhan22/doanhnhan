"""
Kiểm thử luồng chính của doanhnhan.wiki. Chạy: python manage.py test
"""
from datetime import timedelta
from unittest import mock

from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

import io
import json
import os
import time
from pathlib import Path

from apps.accounts.models import AccountApplication, RoleChangeRequest, User
from apps.common.text import normalize, render_markdown, slugify_vi
from apps.common.video import parse_video_url
from apps.directory.models import (
    Association, AwardBadge, Company, CompanyAward, Event, Membership, Person, PersonAward, PersonCompany, Podcast, Postcard, Province,
    Sector, Status, Story, Video,
)
from apps.moderation.models import AuditLog, ProfileClaim, Revision
from apps.sitecontent.models import DonationAccount, PolicyAcceptance, PolicyDocument, PolicyVersion

PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4"
       b"\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82")


def make_user(email, role="member", status="active", password="Matkhau-an-toan-123"):
    u = User.objects.create_user(email=email, password=password, full_name=email.split("@")[0].title(), role=role,
                                 status=status)
    return u


@override_settings(VIDEO_FETCH_METADATA=False, EDITORIAL_NOTIFY_EMAILS=["bbt@example.com"])
class BaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_base", stdout=open("/dev/null", "w"))

    def setUp(self):
        cache.clear()

    def login(self, user, password="Matkhau-an-toan-123"):
        ok = self.client.login(email=user.email, password=password)
        self.assertTrue(ok)
        # đã đồng ý điều khoản hiện hành
        for doc in PolicyDocument.objects.filter(requires_acceptance=True):
            PolicyAcceptance.objects.get_or_create(user=user, version=doc.current_version())


class TextUtilsTest(TestCase):
    def test_normalize_and_slug(self):
        self.assertEqual(normalize("Nguyễn Đức  Anh"), "nguyen duc anh")
        self.assertEqual(slugify_vi("Công nghệ & Phần mềm"), "cong-nghe-phan-mem")

    def test_markdown_sanitized_and_citations(self):
        html = render_markdown("Xin chào[^2] <script>alert(1)</script>\n\n## Mục")
        self.assertIn('href="#nguon-2"', html)
        self.assertNotIn("<script>", html)
        self.assertIn("<h3>", html)

    def test_video_parse(self):
        self.assertEqual(parse_video_url("https://youtu.be/dQw4w9WgXcQ").platform, "youtube")
        self.assertEqual(parse_video_url("https://vimeo.com/123456789").external_id, "123456789")
        self.assertEqual(parse_video_url("https://example.com/x").platform, "other")
        self.assertIsNone(parse_video_url("javascript:alert(1)"))


class SeedTest(BaseTest):
    def test_base_data(self):
        self.assertEqual(Province.objects.count(), 34)
        self.assertEqual(Sector.objects.filter(parent__isnull=True).count(), 8)
        self.assertTrue(PolicyDocument.objects.get(code="dieu-khoan").current_version())


class SignupFlowTest(BaseTest):
    def test_signup_creates_pending_account_and_acceptances(self):
        r = self.client.post(reverse("accounts:signup"), {
            "full_name": "Phạm Văn Thử", "email": "thu@example.com", "phone": "0900000000",
            "password1": "Matkhau-an-toan-123", "password2": "Matkhau-an-toan-123",
            "applicant_type": "entrepreneur", "accept_terms": "on", "accept_data": "on"})
        self.assertRedirects(r, reverse("member:dashboard"))
        user = User.objects.get(email="thu@example.com")
        self.assertEqual(user.status, "pending")
        self.assertEqual(user.policy_acceptances.count(), 2)
        self.assertTrue(AccountApplication.objects.filter(user=user, status="pending").exists())
        # Tài khoản chờ duyệt chưa gửi hồ sơ được
        r = self.client.get(reverse("member:person_create"))
        self.assertRedirects(r, reverse("member:dashboard"))

    def test_signup_requires_consents(self):
        r = self.client.post(reverse("accounts:signup"), {
            "full_name": "A", "email": "a@example.com", "phone": "1", "password1": "Matkhau-an-toan-123",
            "password2": "Matkhau-an-toan-123", "applicant_type": "entrepreneur"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(email="a@example.com").exists())

    def test_editor_approves_account(self):
        pending = make_user("cho@example.com", status="pending")
        app = AccountApplication.objects.create(user=pending, applicant_type="entrepreneur")
        editor = make_user("bt@example.com", role="editor")
        self.login(editor)
        self.client.post(reverse("staff:account_decide", args=[app.pk]), {"action": "approve"})
        pending.refresh_from_db()
        self.assertEqual(pending.status, "active")
        self.assertTrue(any("được duyệt" in m.subject for m in mail.outbox))


class LoginTest(BaseTest):
    def test_lockout_after_failures(self):
        user = make_user("khoa@example.com")
        for _ in range(5):
            self.client.post(reverse("accounts:login"), {"email": user.email, "password": "sai"})
        user.refresh_from_db()
        self.assertTrue(user.is_locked)
        r = self.client.post(reverse("accounts:login"), {"email": user.email, "password": "Matkhau-an-toan-123"})
        self.assertContains(r, "tạm khóa")

    def test_logout_requires_post(self):
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)


class RevisionFlowTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.member = make_user("tv@example.com")
        self.member.full_name = "Đỗ Thử Nghiệm"
        self.member.save()
        AccountApplication.objects.create(user=self.member, applicant_type="entrepreneur")
        self.editor = make_user("bt@example.com", role="editor")
        self.hcm = Province.objects.get(code="tp-ho-chi-minh")
        self.tech = Sector.objects.get(name="Fintech")

    def person_post(self, **extra):
        data = {
            "full_name": "Đỗ Thử Nghiệm", "birth_year": "1991", "current_province": self.hcm.pk,
            "headline": "Nhà sáng lập", "show_birth_year": "on",
            "company_name": ["Công ty Thử Nghiệm Mới"], "company_role": ["founder_ceo"], "company_title": [""],
            "company_start": ["2019"], "company_end": [""], "company_primary": ["1"],
            "section_summary": "Tóm tắt có chú thích[^1].", "section_journey": "Hành trình " * 20,
            "milestone_year": ["2019", "2021"], "milestone_kind": ["founding", "award"],
            "milestone_title": ["Thành lập công ty", "Nhận giải"], "milestone_source": ["", ""],
            "source_title": ["Bài báo A"], "source_url": ["https://example.com/a"], "source_kind": ["press"],
            "video_url": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"], "video_title": ["Phỏng vấn thử"],
            "action": "submit",
        }
        data.update(extra)
        return data

    def test_member_submit_then_editor_approve(self):
        self.login(self.member)
        r = self.client.post(reverse("member:person_create"), self.person_post())
        self.assertRedirects(r, reverse("member:dashboard"))
        rev = Revision.objects.get()
        self.assertEqual(rev.state, "pending")
        self.assertTrue(any(c["level"] == "warn" for c in rev.checks))  # hành trình < 500 từ
        self.assertFalse(Person.objects.filter(full_name="Đỗ Thử Nghiệm").exists())

        self.client.logout()
        self.login(self.editor)
        r = self.client.get(reverse("staff:review", args=[rev.pk]))
        self.assertContains(r, "Đỗ Thử Nghiệm")
        self.client.post(reverse("staff:review", args=[rev.pk]), {"action": "approve"})
        rev.refresh_from_db()
        self.assertEqual(rev.state, "approved")
        self.assertEqual(rev.revision_no, 1)
        person = Person.objects.get(full_name="Đỗ Thử Nghiệm")
        self.assertEqual(person.status, "published")
        self.assertEqual(person.owner, self.member)  # tự gửi hồ sơ của chính mình
        self.assertEqual(person.milestones.count(), 2)
        self.assertEqual(person.sources.count(), 1)
        company = Company.objects.get(legal_name="Công ty Thử Nghiệm Mới")
        self.assertEqual(company.status, "draft")  # doanh nghiệp mới tạo bản nháp
        video = Video.objects.get()
        self.assertEqual(video.platform, "youtube")
        self.assertIn(person, video.persons.all())

        page = self.client.get(person.get_absolute_url())
        self.assertContains(page, "Đỗ Thử Nghiệm")
        self.assertContains(page, 'href="#nguon-1"')
        self.assertContains(page, "Phỏng vấn thử")
        self.assertTrue(AuditLog.objects.filter(action="revision.approve").exists())

    def test_person_submit_with_new_company_tax_code(self):
        self.login(self.editor)
        post_data = self.person_post(
            full_name="Nguyễn Văn Doanh",
            company_name=["Công ty Công Nghệ Tương Lai Mới"],
            company_tax=["0109988776"],
        )
        res = self.client.post(reverse("staff:person_new"), post_data)
        self.assertEqual(res.status_code, 302)
        person = Person.objects.get(full_name="Nguyễn Văn Doanh")
        company = Company.objects.get(tax_code="0109988776")
        self.assertEqual(company.legal_name, "Công ty Công Nghệ Tương Lai Mới")
        self.assertEqual(company.status, Status.DRAFT)
        self.assertTrue(person.company_links.filter(company=company).exists())


    def test_needs_info_and_resubmit(self):
        self.login(self.member)
        self.client.post(reverse("member:person_create"), self.person_post())
        rev = Revision.objects.get()
        self.client.logout()
        self.login(self.editor)
        r = self.client.post(reverse("staff:review", args=[rev.pk]), {"action": "needs_info"})
        rev.refresh_from_db()
        self.assertEqual(rev.state, "pending")  # thiếu ghi chú → không đổi
        self.client.post(reverse("staff:review", args=[rev.pk]), {"action": "needs_info", "review_note": "Thêm nguồn"})
        rev.refresh_from_db()
        self.assertEqual(rev.state, "needs_info")
        self.client.logout()
        self.login(self.member)
        self.client.post(reverse("member:revision_edit", args=[rev.pk]), self.person_post(
            source_title=["Bài báo A", "Bài báo B"], source_url=["https://example.com/a", "https://example.com/b"],
            source_kind=["press", "press"]))
        rev.refresh_from_db()
        self.assertEqual(rev.state, "pending")
        self.assertEqual(len(rev.data["sources"]), 2)

    def test_edit_proposal_shows_diff(self):
        person = Person.objects.create(full_name="Hồ Sơ Có Sẵn", headline="Cũ")
        self.login(self.member)
        r = self.client.get(reverse("member:person_edit", args=[person.slug]))
        self.assertContains(r, "Hồ Sơ Có Sẵn")
        self.client.post(reverse("member:person_edit", args=[person.slug]),
                         {"full_name": "Hồ Sơ Có Sẵn", "headline": "Mới", "action": "submit"})
        rev = Revision.objects.get(person=person)
        self.assertEqual(rev.kind, "update")
        self.client.logout()
        self.login(self.editor)
        r = self.client.get(reverse("staff:review", args=[rev.pk]))
        self.assertContains(r, "Mới")
        person.refresh_from_db()
        self.assertEqual(person.headline, "Cũ")  # chưa duyệt thì chưa đổi

    def test_invalid_input_rerenders(self):
        self.login(self.member)
        r = self.client.post(reverse("member:company_create"), {"legal_name": "", "tax_code": "123", "action": "submit"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Mã số thuế gồm 10 chữ số")
        self.assertFalse(Revision.objects.exists())

    def test_company_duplicate_tax_code_warning(self):
        Company.objects.create(legal_name="Công ty Đã Có", tax_code="0312345678")
        self.login(self.member)
        self.client.post(reverse("member:company_create"), {
            "legal_name": "Công ty Khác", "tax_code": "0312345678", "primary_sector": self.tech.pk, "action": "submit"})
        rev = Revision.objects.get()
        self.assertTrue(any("0312345678" in c["text"] and c["level"] == "warn" for c in rev.checks))

    def test_company_requires_tax_code(self):
        self.login(self.member)
        r = self.client.post(reverse("member:company_create"), {
            "legal_name": "Công ty Thiếu Thuế", "tax_code": "", "action": "submit"})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Vui lòng nhập mã số thuế doanh nghiệp (bắt buộc).")
        self.assertFalse(Revision.objects.filter(data__legal_name="Công ty Thiếu Thuế").exists())

    def test_company_tax_code_is_immutable_on_edit(self):
        company = Company.objects.create(
            legal_name="Công ty Gốc", brand_name="Gốc", tax_code="0199999999", status=Status.PUBLISHED)
        self.login(self.editor)
        # Biên tập viên cập nhật hồ sơ công ty nhưng gửi tax_code khác
        self.client.post(reverse("staff:company_edit", args=[company.pk]), {
            "legal_name": "Công ty Gốc Đã Đổi Tên",
            "brand_name": "Gốc Mới",
            "tax_code": "0188888888",
            "address": "Số 99 Phố Mới",
            "status": "published",
        })
        company.refresh_from_db()
        self.assertEqual(company.legal_name, "Công ty Gốc Đã Đổi Tên")
        self.assertEqual(company.brand_name, "Gốc Mới")
        self.assertEqual(company.address, "Số 99 Phố Mới")
        # Mã số thuế bắt buộc giữ nguyên giá trị ban đầu
        self.assertEqual(company.tax_code, "0199999999")

    def test_staff_direct_edit_creates_history(self):
        self.login(self.editor)
        r = self.client.post(reverse("staff:company_new"), {
            "legal_name": "Công ty Biên Tập", "tax_code": "0101010101", "primary_sector": self.tech.pk,
            "status": "published", "verification": "verified", "section_overview": "Giới thiệu.",
            "leader_name": ["Người Điều Hành"], "leader_role": ["ceo"], "leader_title": [""], "leader_start": [""],
            "leader_primary": ["1"], "product_name": ["Ứng dụng"], "product_description": ["Mô tả"]})
        company = Company.objects.get(legal_name="Công ty Biên Tập")
        self.assertRedirects(r, company.get_absolute_url())
        self.assertEqual(company.verification, "verified")
        self.assertEqual(company.revisions.get().revision_no, 1)
        self.assertEqual(company.products.count(), 1)
        self.assertTrue(company.person_links.filter(person__full_name="Người Điều Hành").exists())
        r = self.client.get(reverse("public:company_history", args=[company.slug]))
        self.assertContains(r, "#1")

    def test_image_upload_stays_private_until_approved(self):
        self.login(self.member)
        data = self.person_post()
        data["portrait"] = SimpleUploadedFile("anh.png", PNG, content_type="image/png")
        self.client.post(reverse("member:person_create"), data)
        rev = Revision.objects.get()
        self.assertTrue(rev.data["portrait"].startswith("pending/"))
        self.client.logout()
        r = self.client.get(reverse("member:pending_image") + f"?p={rev.data['portrait']}")
        self.assertNotEqual(r.status_code, 200)
        self.login(self.editor)
        self.client.post(reverse("staff:review", args=[rev.pk]), {"action": "approve"})
        person = Person.objects.get(full_name="Đỗ Thử Nghiệm")
        self.assertTrue(person.portrait.name.startswith("portraits/"))


class VisibilityTest(BaseTest):
    def test_draft_hidden_and_video_block_hidden(self):
        p = Person.objects.create(full_name="Bản Nháp", status="draft")
        self.assertEqual(self.client.get(p.get_absolute_url()).status_code, 404)
        p.status = "published"
        p.save()
        page = self.client.get(p.get_absolute_url())
        self.assertNotContains(page, '<h2 style="margin:0">Video</h2>')
        v = Video.objects.create(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", title="Video A")
        v.persons.add(p)
        self.assertContains(self.client.get(p.get_absolute_url()), "Video A")
        r = self.client.get(reverse("public:video_list"))
        self.assertContains(r, 'data-video-url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"')
        self.assertContains(self.client.get(reverse("public:home")), "Video A")
        v.availability = "unavailable"
        v.save()
        self.assertNotContains(self.client.get(reverse("public:video_list")), "Video A")
        self.assertNotContains(self.client.get(p.get_absolute_url()), "Video A")

    def test_search_without_diacritics(self):
        Person.objects.create(full_name="Nguyễn Văn Đạt")
        r = self.client.get(reverse("public:search") + "?q=nguyen van dat")
        self.assertContains(r, "Nguyễn Văn Đạt")


class ClaimTest(BaseTest):
    def test_claim_flow(self):
        person = Person.objects.create(full_name="Chính Chủ")
        member = make_user("cc@example.com")
        self.login(member)
        r = self.client.post(reverse("member:claim", args=[person.slug]), {
            "evidence": SimpleUploadedFile("giay.pdf", b"%PDF-1.4 test", content_type="application/pdf")})
        self.assertRedirects(r, reverse("member:dashboard"))
        claim = ProfileClaim.objects.get()
        self.client.logout()
        editor = make_user("bt@example.com", role="editor")
        self.login(editor)
        self.assertEqual(self.client.get(reverse("staff:claim_evidence", args=[claim.pk])).status_code, 200)
        self.client.post(reverse("staff:claim_decide", args=[claim.pk]), {"action": "approve"})
        person.refresh_from_db()
        self.assertEqual(person.owner, member)


class AdminSafeguardTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.a1 = make_user("qt1@example.com", role="admin")
        self.a2 = make_user("qt2@example.com", role="admin")

    def test_donation_account_needs_second_admin(self):
        self.login(self.a1)
        self.client.post(reverse("staff:donation_account_new"), {
            "bank_name": "Ngân hàng A", "account_number": "0123 456 789", "account_holder": "Công ty X", "sort_order": 0})
        acc = DonationAccount.objects.get()
        self.assertEqual(acc.account_number, "0123456789")
        self.client.post(reverse("staff:donation_account_decide", args=[acc.pk]), {"action": "approve"})
        acc.refresh_from_db()
        self.assertEqual(acc.state, "pending")
        self.assertNotContains(self.client.get(reverse("public:donate")), "0123456789")
        self.client.logout()
        self.login(self.a2)
        self.client.post(reverse("staff:donation_account_decide", args=[acc.pk]), {"action": "approve"})
        acc.refresh_from_db()
        self.assertEqual(acc.state, "active")
        r = self.client.get(reverse("public:donate"))
        self.assertContains(r, "0123456789")
        self.assertContains(r, "Tài trợ website doanhnhan.wiki")

    def test_admin_role_needs_second_admin(self):
        target = make_user("bt@example.com", role="editor")
        self.login(self.a1)
        self.client.post(reverse("staff:user_update", args=[target.pk]), {"action": "role", "role": "admin"})
        target.refresh_from_db()
        self.assertEqual(target.role, "editor")
        rq = RoleChangeRequest.objects.get()
        self.client.post(reverse("staff:role_request_decide", args=[rq.pk]), {"action": "confirm"})
        target.refresh_from_db()
        self.assertEqual(target.role, "editor")
        self.client.logout()
        self.login(self.a2)
        self.client.post(reverse("staff:role_request_decide", args=[rq.pk]), {"action": "confirm"})
        target.refresh_from_db()
        self.assertEqual(target.role, "admin")

    def test_editor_cannot_open_admin_pages(self):
        editor = make_user("bt2@example.com", role="editor")
        self.login(editor)
        self.assertEqual(self.client.get(reverse("staff:donation")).status_code, 403)
        self.assertEqual(self.client.get(reverse("staff:users")).status_code, 403)
        self.assertEqual(self.client.get(reverse("staff:dashboard")).status_code, 200)

    def test_member_cannot_open_staff(self):
        m = make_user("tv2@example.com")
        self.login(m)
        self.assertEqual(self.client.get(reverse("staff:dashboard")).status_code, 403)


class PolicyReacceptTest(BaseTest):
    def test_new_version_requires_reaccept(self):
        user = make_user("dk@example.com")
        self.login(user)
        self.assertEqual(self.client.get(reverse("public:home")).status_code, 200)
        doc = PolicyDocument.objects.get(code="dieu-khoan")
        v2 = PolicyVersion.objects.create(document=doc, version="2.0", body_md="Mới", status="published",
                                          require_reaccept=True, effective_at=timezone.now())
        cache.clear()
        r = self.client.get(reverse("public:home"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("accounts:accept_policies"), r["Location"])
        self.client.post(reverse("accounts:accept_policies"), {f"v{v2.pk}": "on"})
        self.assertEqual(self.client.get(reverse("public:home")).status_code, 200)


class StaffPagesTest(BaseTest):
    def test_all_staff_pages_render(self):
        call_command("seed_demo", stdout=open("/dev/null", "w"))
        admin = make_user("root@example.com", role="admin")
        self.login(admin)
        p, c = Person.objects.first(), Company.objects.first()
        a = Association.objects.first()
        names = ["dashboard", "accounts", "claims", "person_list", "person_new", "company_list", "company_new",
                 "sector_list", "sector_new", "association_list", "association_new", "event_list", "event_new",
                 "video_list", "video_new", "interviews", "contacts", "data_requests", "users", "donation", "policies",
                 "policy_document_new", "site_settings", "audit_log"]
        for name in names:
            self.assertEqual(self.client.get(reverse(f"staff:{name}")).status_code, 200, name)
        for url in [reverse("staff:person_edit", args=[p.pk]), reverse("staff:company_edit", args=[c.pk]),
                    reverse("staff:association_members", args=[a.pk]),
                    reverse("staff:policy_version_new", args=[PolicyDocument.objects.first().pk])]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_membership_and_event_participant(self):
        editor = make_user("bt@example.com", role="editor")
        self.login(editor)
        person = Person.objects.create(full_name="Hội Viên Một")
        assoc = Association.objects.create(name="Hội Thử")
        self.client.post(reverse("staff:association_members", args=[assoc.pk]),
                         {"action": "add", "person": f"Hội Viên Một (#{person.pk})", "position": "Phó Chủ tịch",
                          "is_leadership": "on"})
        m = Membership.objects.get()
        self.assertTrue(m.is_leadership)
        self.assertContains(self.client.get(assoc.get_absolute_url()), "Phó Chủ tịch")
        start = timezone.localtime() + timedelta(days=3)
        self.client.post(reverse("staff:event_new"), {
            "title": "Hội thảo thử", "kind": "conference", "starts_at": start.strftime("%Y-%m-%dT%H:%M"),
            "status": "published", "participant_name": [f"Hội Viên Một (#{person.pk})"],
            "participant_role": ["awardee"], "participant_note": ["Giải A"], "participant_milestone": ["1"]})
        self.assertTrue(person.milestones.filter(kind="award").exists())


class ApiTest(BaseTest):
    def test_public_only_and_privacy(self):
        hidden = Person.objects.create(full_name="Bản Nháp API", status="draft")
        p = Person.objects.create(full_name="Công Khai API", birth_year=1990, show_birth_year=False,
                                  email_public="a@example.com", show_email=True)
        r = self.client.get("/api/v1/persons/")
        self.assertEqual(r["Access-Control-Allow-Origin"], "*")
        slugs = [x["slug"] for x in r.json()["results"]]
        self.assertIn(p.slug, slugs)
        self.assertNotIn(hidden.slug, slugs)
        self.assertEqual(self.client.get(f"/api/v1/persons/{hidden.slug}/").status_code, 404)
        d = self.client.get(f"/api/v1/persons/{p.slug}/").json()
        self.assertIsNone(d["birth_year"])
        self.assertEqual(d["email"], "a@example.com")

    def test_search_filters_errors(self):
        Company.objects.create(legal_name="Công ty Tìm Kiếm", tax_code="0101234567", size_band="10_50")
        self.assertEqual(self.client.get("/api/v1/companies/?tax_code=0101234567").json()["count"], 1)
        self.assertEqual(self.client.get("/api/v1/companies/?size=10_50").json()["count"], 1)
        self.assertEqual(self.client.get("/api/v1/search/?q=tim kiem").json()["companies"][0]["tax_code"], "0101234567")
        self.assertEqual(self.client.get("/api/v1/provinces/").json()["count"], 34)
        self.assertEqual(self.client.get("/api/v1/sectors/fintech/").json()["vsic_code"], "66")
        self.assertEqual(self.client.get("/api/v1/persons/?page_size=500").status_code, 400)
        self.assertEqual(self.client.get("/api/v1/khong-co").json()["error"]["code"], "not_found")
        self.assertEqual(self.client.post("/api/v1/persons/").status_code, 405)

    @override_settings(VIDEO_FETCH_METADATA=False)
    def test_rate_limit(self):
        from apps.api import views
        old = views.RATE_LIMIT
        views.RATE_LIMIT = 3
        try:
            codes = [self.client.get("/api/v1/").status_code for _ in range(4)]
        finally:
            views.RATE_LIMIT = old
        self.assertEqual(codes[-1], 429)


class SeedTestCommandTest(BaseTest):
    def test_create_and_remove(self):
        call_command("seed_test", "--xac-nhan", stdout=open("/dev/null", "w"))
        self.assertEqual(User.objects.filter(email__endswith="@example.com").count(), 11)
        self.assertEqual(Revision.objects.filter(state="pending").count(), 3)
        self.assertTrue(self.client.login(email="bientap@example.com", password="Demo@2026!"))
        self.assertEqual(self.client.get(reverse("staff:dashboard")).status_code, 200)
        call_command("seed_test", "--xoa", "--xac-nhan", stdout=open("/dev/null", "w"))
        self.assertFalse(User.objects.exists())
        self.assertFalse(Person.objects.exists())
        self.assertEqual(Province.objects.count(), 34)


class StaffDeleteAndArchiveTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.editor = make_user("editor_test@example.com", role="editor")
        self.login(self.editor)
        self.prov = Province.objects.first()

    def test_person_toggle_and_delete(self):
        p = Person.objects.create(full_name="Nguyễn Văn A", current_province=self.prov, status=Status.PUBLISHED)
        res = self.client.post(reverse("staff:person_toggle_status", args=[p.pk]))
        self.assertEqual(res.status_code, 302)
        p.refresh_from_db()
        self.assertEqual(p.status, Status.ARCHIVED)
        res = self.client.post(reverse("staff:person_toggle_status", args=[p.pk]))
        p.refresh_from_db()
        self.assertEqual(p.status, Status.PUBLISHED)
        res = self.client.post(reverse("staff:person_delete", args=[p.pk]))
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Person.objects.filter(pk=p.pk).exists())

    def test_company_toggle_and_delete(self):
        c = Company.objects.create(legal_name="Công ty ABC", status=Status.PUBLISHED)
        res = self.client.post(reverse("staff:company_toggle_status", args=[c.pk]))
        c.refresh_from_db()
        self.assertEqual(c.status, Status.ARCHIVED)
        res = self.client.post(reverse("staff:company_toggle_status", args=[c.pk]))
        c.refresh_from_db()
        self.assertEqual(c.status, Status.PUBLISHED)
        res = self.client.post(reverse("staff:company_delete", args=[c.pk]))
        self.assertFalse(Company.objects.filter(pk=c.pk).exists())

    def test_sector_toggle_and_delete(self):
        parent = Sector.objects.create(name="Ngành Cha", is_active=True)
        child = Sector.objects.create(name="Ngành Con", parent=parent, is_active=True)
        self.client.post(reverse("staff:sector_toggle_status", args=[parent.pk]))
        parent.refresh_from_db()
        self.assertFalse(parent.is_active)
        res = self.client.post(reverse("staff:sector_delete", args=[parent.pk]))
        self.assertTrue(Sector.objects.filter(pk=parent.pk).exists())
        self.client.post(reverse("staff:sector_delete", args=[child.pk]))
        self.assertFalse(Sector.objects.filter(pk=child.pk).exists())
        self.client.post(reverse("staff:sector_delete", args=[parent.pk]))
        self.assertFalse(Sector.objects.filter(pk=parent.pk).exists())

    def test_sector_quick_add_api(self):
        # 1. Quick add root sector
        res = self.client.post(
            reverse("staff:api_sector_quick_add"),
            data=json.dumps({"name": "Bán dẫn & Vi mạch", "icon": "tech"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["ok"])
        self.assertTrue(data["created"])
        root_id = data["sector"]["id"]
        self.assertTrue(data["sector"]["is_root"])

        # 2. Quick add child subsector under the root
        res = self.client.post(
            reverse("staff:api_sector_quick_add"),
            data=json.dumps({"name": "Thiết kế chip", "parent_id": root_id, "vsic_code": "261"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["ok"])
        self.assertTrue(data["created"])
        child_id = data["sector"]["id"]
        self.assertFalse(data["sector"]["is_root"])
        self.assertEqual(data["sector"]["parent_id"], root_id)

        # 3. Duplicate sector returns existing
        res = self.client.post(
            reverse("staff:api_sector_quick_add"),
            data=json.dumps({"name": "Thiết kế chip", "parent_id": root_id}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["ok"])
        self.assertFalse(data["created"])
        self.assertEqual(data["sector"]["id"], child_id)

        # 4. Empty name returns 400
        res = self.client.post(
            reverse("staff:api_sector_quick_add"),
            data=json.dumps({"name": "   "}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json()["ok"])

        # 5. Check appearance in sector_options()
        from apps.moderation.editor import sector_options
        options = sector_options()
        opt_ids = [s.pk for s in options]
        self.assertIn(root_id, opt_ids)
        self.assertIn(child_id, opt_ids)

        # 6. Assign to company and verify entrepreneur acquires it
        root_sector = Sector.objects.get(pk=root_id)
        child_sector = Sector.objects.get(pk=child_id)
        comp = Company.objects.create(legal_name="Tập đoàn Bán dẫn VN", primary_sector=root_sector, status=Status.PUBLISHED)
        comp.sectors.add(child_sector)

        person = Person.objects.create(full_name="Nguyễn Văn Vi Mạch", status=Status.PUBLISHED)
        PersonCompany.objects.create(person=person, company=comp, role="founder_ceo", is_primary=True)

        self.assertIn(child_sector, person.sectors())

        # 7. Sector list page loads and includes root and child
        res = self.client.get(reverse("staff:sector_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Bán dẫn &amp; Vi mạch")
        self.assertContains(res, "Thiết kế chip")

    def test_association_toggle_and_delete(self):
        a = Association.objects.create(name="Hiệp hội XYZ", status=Status.PUBLISHED)
        self.client.post(reverse("staff:association_toggle_status", args=[a.pk]))
        a.refresh_from_db()
        self.assertEqual(a.status, Status.ARCHIVED)
        self.client.post(reverse("staff:association_delete", args=[a.pk]))
        self.assertFalse(Association.objects.filter(pk=a.pk).exists())

    def test_event_toggle_and_delete(self):
        e = Event.objects.create(title="Sự kiện 2026", starts_at=timezone.now(), status=Event.EventStatus.PUBLISHED)
        self.client.post(reverse("staff:event_toggle_status", args=[e.pk]))
        e.refresh_from_db()
        self.assertEqual(e.status, Event.EventStatus.ARCHIVED)
        self.client.post(reverse("staff:event_delete", args=[e.pk]))
        self.assertFalse(Event.objects.filter(pk=e.pk).exists())


class NewFeaturesTest(TestCase):
    def setUp(self):
        self.person = Person.objects.create(full_name="Lê Hoàng Nam", status=Status.PUBLISHED)
        self.company = Company.objects.create(legal_name="Tập đoàn Công nghệ Nam Việt", brand_name="Nam Việt Tech", status=Status.PUBLISHED)
        from apps.directory.models import AwardBadge, PersonAward
        self.badge = AwardBadge.objects.create(code="sao-do-test", name="Giải thưởng Sao Đỏ", color="gold")
        self.award = PersonAward.objects.create(person=self.person, badge=self.badge, year=2024, title="Top 10")

    def test_award_badge_and_primary_badge(self):
        self.assertEqual(self.person.primary_badge.badge.name, "Giải thưởng Sao Đỏ")
        self.assertEqual(self.person.primary_badge.year, 2024)

    def test_og_image_endpoint(self):
        res = self.client.get(reverse("public:person_og_image", args=[self.person.slug]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "image/png")
        self.assertTrue(len(res.content) > 1000)

    def test_print_profile_endpoint(self):
        res = self.client.get(reverse("public:person_print", args=[self.person.slug]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "TRÍCH LỤC HỒ SƠ DOANH NHÂN")
        self.assertContains(res, self.person.full_name)
        self.assertContains(res, "Giải thưởng Sao Đỏ")

    def test_person_detail_has_badge_and_pdf_links(self):
        res = self.client.get(reverse("public:person_detail", args=[self.person.slug]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "badge-award")
        self.assertContains(res, "Giải thưởng Sao Đỏ")
        self.assertContains(res, reverse("public:person_print", args=[self.person.slug]))
        self.assertContains(res, reverse("public:person_og_image", args=[self.person.slug]))

    def test_company_og_image_endpoint(self):
        res = self.client.get(reverse("public:company_og_image", args=[self.company.slug]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "image/png")
        self.assertTrue(len(res.content) > 1000)

    def test_default_og_image_endpoint(self):
        res = self.client.get(reverse("public:default_og_image"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "image/png")
        self.assertTrue(len(res.content) > 1000)

    def test_company_detail_has_og_image(self):
        res = self.client.get(reverse("public:company_detail", args=[self.company.slug]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, reverse("public:company_og_image", args=[self.company.slug]))


    def test_suggest_omnisearch(self):
        Company.objects.create(legal_name="Công ty Hoàng Kim", brand_name="Hoàng Kim Group", status=Status.PUBLISHED)
        res = self.client.get("/api/goi-y/?q=Hoàng")
        self.assertEqual(res.status_code, 200)
        data = res.json()["results"]
        titles = [item["title"] for item in data]
        self.assertIn("Lê Hoàng Nam", titles)
        self.assertTrue(any("Hoàng Kim" in t for t in titles))

    def test_company_detail_opengraph(self):
        c = Company.objects.create(legal_name="Tập đoàn Mặt Trời Mới", brand_name="Sun New", status=Status.PUBLISHED)
        res = self.client.get(c.get_absolute_url())
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'property="og:title"')
        self.assertContains(res, 'property="og:url"')
        self.assertContains(res, 'name="twitter:card"')

    def test_favicon_in_base(self):
        res = self.client.get(reverse("public:home"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'rel="icon" type="image/svg+xml"')

    def test_ai_assistant_permissions(self):
        url = reverse("staff:ai_assistant")
        # Khách vãng lai: chuyển hướng đăng nhập
        res = self.client.post(url, {"action": "summary"}, content_type="application/json")
        self.assertEqual(res.status_code, 302)

    def test_ai_assistant_generation(self):
        from apps.accounts.models import User
        editor = User.objects.create_user(email="btv_ai@example.com", password="password123", role="editor", status="active")
        self.client.force_login(editor)

        url = reverse("staff:ai_assistant")
        res = self.client.post(url, {
            "action": "summary",
            "target_name": "Trần Văn An",
            "target_type": "person",
            "notes": "Sáng lập công ty nông nghiệp sạch từ năm 2018.",
        }, content_type="application/json")

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["ok"])
        self.assertIn("Trần Văn An", data["content"])

        # Kiểm tra hiển thị Drawer khi editor login
        page_res = self.client.get(reverse("public:home"))
        self.assertEqual(page_res.status_code, 200)
        self.assertContains(page_res, "ai-launcher-btn")
        self.assertContains(page_res, "ai-assistant-drawer")

        # Kiểm tra không hiện Drawer khi chưa đăng nhập
        self.client.logout()
        anon_res = self.client.get(reverse("public:home"))
        self.assertNotContains(anon_res, "ai-launcher-btn")

    def test_ai_admin_configuration(self):
        from apps.sitecontent.models import SiteSettings
        admin = User.objects.create_user(email="admin_ai@example.com", password="password123", role="admin", status="active")
        editor = User.objects.create_user(email="editor_ai@example.com", password="password123", role="editor", status="active")

        # 1. Editor xem config: ok nhưng không thể sửa
        self.client.force_login(editor)
        cfg_url = reverse("staff:ai_config_api")
        res = self.client.get(cfg_url)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()["config"]["is_admin"])

        res_forbidden = self.client.post(cfg_url, {"gemini_api_key": "AIzaSyTestKey"}, content_type="application/json")
        self.assertEqual(res_forbidden.status_code, 403)

        # 2. Admin cập nhật API Key và Model qua API
        self.client.force_login(admin)
        res_admin = self.client.post(cfg_url, {
            "gemini_api_key": "AIzaSySecretAdminKey12345",
            "gemini_model": "gemini-1.5-pro",
        }, content_type="application/json")
        self.assertEqual(res_admin.status_code, 200)
        self.assertTrue(res_admin.json()["ok"])

        site = SiteSettings.load()
        self.assertEqual(site.gemini_api_key, "AIzaSySecretAdminKey12345")
        self.assertEqual(site.gemini_model, "gemini-1.5-pro")

        # 3. Kiểm tra trang Cài đặt chung (/quan-tri/cai-dat/) có hiển thị các trường này
        settings_page = self.client.get(reverse("staff:site_settings"))
        self.assertEqual(settings_page.status_code, 200)
        self.assertContains(settings_page, "gemini_api_key")
        self.assertContains(settings_page, "gemini_model")
        self.assertContains(settings_page, "AIzaSySecretAdminKey12345")

    def test_award_management_and_assignment(self):
        from apps.directory.models import AwardBadge, Person, PersonAward
        editor = User.objects.create_user(email="editor_award@example.com", password="password123", role="editor", status="active")
        self.client.force_login(editor)

        # 1. Tạo mới danh hiệu
        res_create = self.client.post(reverse("staff:award_new"), {
            "name": "Giải thưởng Sao Đỏ 2026",
            "code": "sao-do-2026",
            "badge_type": "sao_do",
            "issuer": "TW Hội DNT VN",
            "color": "gold",
            "icon": "star",
            "description": "Giải thưởng danh giá nhất cho doanh nhân trẻ.",
            "sort_order": 1,
        })
        self.assertEqual(res_create.status_code, 302)
        badge = AwardBadge.objects.get(code="sao-do-2026")
        self.assertEqual(badge.name, "Giải thưởng Sao Đỏ 2026")

        # 2. Xem danh sách danh hiệu
        res_list = self.client.get(reverse("staff:award_list"))
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, "Giải thưởng Sao Đỏ 2026")

        # 3. Sửa danh hiệu
        res_edit = self.client.post(reverse("staff:award_edit", args=[badge.pk]), {
            "name": "Giải thưởng Sao Đỏ Danh Giá",
            "code": "sao-do-2026",
            "badge_type": "sao_do",
            "issuer": "TW Hội DNT VN",
            "color": "red",
            "icon": "trophy",
            "description": "Đã cập nhật mô tả.",
            "sort_order": 2,
        })
        self.assertEqual(res_edit.status_code, 302)
        badge.refresh_from_db()
        self.assertEqual(badge.name, "Giải thưởng Sao Đỏ Danh Giá")
        self.assertEqual(badge.color, "red")

        # 4. Gán danh hiệu cho Doanh nhân qua award_honors
        person = Person.objects.create(full_name="Nguyễn Văn Doanh", status="published")
        res_honors_get = self.client.get(reverse("staff:award_honors", args=[badge.pk]))
        self.assertEqual(res_honors_get.status_code, 200)

        res_assign = self.client.post(reverse("staff:award_honors", args=[badge.pk]), {
            "form_type": "person",
            "person": person.pk,
            "year": 2026,
            "title": "Top 10 Sao Đỏ",
            "citation": "Quyết định khen thưởng số 88",
        })
        self.assertEqual(res_assign.status_code, 302)
        award = PersonAward.objects.get(badge=badge, person=person)
        self.assertEqual(award.year, 2026)
        self.assertEqual(award.title, "Top 10 Sao Đỏ")

        # 5. Gỡ danh hiệu khỏi Doanh nhân qua award_honors
        res_revoke = self.client.post(reverse("staff:award_honor_delete", args=[badge.pk, award.pk]))
        self.assertEqual(res_revoke.status_code, 302)
        self.assertFalse(PersonAward.objects.filter(pk=award.pk).exists())

        # 6. Gán danh hiệu trực tiếp trong hồ sơ Doanh nhân (Person Editor)
        res_person_award = self.client.post(reverse("staff:person_edit", args=[person.pk]), {
            "full_name": person.full_name,
            "status": "published",
            "verification": "none",
            "award_badge_id": [str(badge.pk)],
            "award_year": ["2025"],
            "award_title": ["Top 100 Sao Đỏ"],
            "award_citation": ["Quyết định số 100/QĐ-DNT"],
        })
        self.assertEqual(res_person_award.status_code, 302)
        p_award = PersonAward.objects.get(person=person, badge=badge)
        self.assertEqual(p_award.year, 2025)
        self.assertEqual(p_award.title, "Top 100 Sao Đỏ")

        # Kiểm tra hiển thị huy hiệu trên trang chi tiết công khai của Doanh nhân
        res_p_detail = self.client.get(person.get_absolute_url())
        self.assertContains(res_p_detail, "Giải thưởng Sao Đỏ Danh Giá")
        self.assertContains(res_p_detail, "Top 100 Sao Đỏ")

        # 7. Gán danh hiệu trực tiếp trong hồ sơ Doanh nghiệp (Company Editor)
        company = Company.objects.create(legal_name="Tập đoàn Công nghệ Sao Đỏ", status="published")
        res_company_award = self.client.post(reverse("staff:company_edit", args=[company.pk]), {
            "legal_name": company.legal_name,
            "status": "published",
            "verification": "none",
            "award_badge_id": [str(badge.pk)],
            "award_year": ["2026"],
            "award_title": ["Sao Vàng Đất Việt"],
            "award_citation": ["Quyết định số 200/QĐ-DNT"],
        })
        self.assertEqual(res_company_award.status_code, 302)
        c_award = CompanyAward.objects.get(company=company, badge=badge)
        self.assertEqual(c_award.year, 2026)
        self.assertEqual(c_award.title, "Sao Vàng Đất Việt")

        # Kiểm tra hiển thị huy hiệu trên trang chi tiết công khai của Doanh nghiệp
        res_c_detail = self.client.get(company.get_absolute_url())
        self.assertContains(res_c_detail, "Giải thưởng Sao Đỏ Danh Giá")
        self.assertContains(res_c_detail, "Sao Vàng Đất Việt")

        # 8. Gán danh hiệu cho Doanh nghiệp từ trang Vinh danh (award_honors)
        company2 = Company.objects.create(legal_name="Công ty Cổ phần Alpha", status="published")
        res_assign_c2 = self.client.post(reverse("staff:award_honors", args=[badge.pk]), {
            "form_type": "company",
            "company": company2.pk,
            "year": 2024,
            "title": "Doanh nghiệp tiêu biểu",
            "citation": "Khen thưởng năm 2024",
        })
        self.assertEqual(res_assign_c2.status_code, 302)
        c2_award = CompanyAward.objects.get(company=company2, badge=badge)
        self.assertEqual(c2_award.year, 2024)

        # Gỡ danh hiệu khỏi Doanh nghiệp
        res_revoke_c = self.client.post(reverse("staff:award_company_honor_delete", args=[badge.pk, c2_award.pk]))
        self.assertEqual(res_revoke_c.status_code, 302)
        self.assertFalse(CompanyAward.objects.filter(pk=c2_award.pk).exists())

        # 9. Xóa danh hiệu (kiểm tra cascade)
        res_delete = self.client.post(reverse("staff:award_delete", args=[badge.pk]))
        self.assertEqual(res_delete.status_code, 302)
        self.assertFalse(AwardBadge.objects.filter(pk=badge.pk).exists())
        self.assertFalse(PersonAward.objects.filter(badge_id=badge.pk).exists())
        self.assertFalse(CompanyAward.objects.filter(badge_id=badge.pk).exists())

    def test_feedback_correction_requires_phone_and_source(self):
        from apps.sitecontent.models import ContactMessage
        # 1. Missing phone fails
        res = self.client.post(reverse("public:feedback"), {
            "topic": "correction",
            "full_name": "Nguyễn Văn Test",
            "email": "test@example.com",
            "phone": "",
            "source_url": "https://baochinhphu.vn/bai-viet-123",
            "message": "Cần sửa năm sinh từ 1985 thành 1986",
            "consent": "on",
        })
        self.assertEqual(res.status_code, 200)
        self.assertFormError(res.context["form"], "phone", "Trường này là bắt buộc.")

        # 2. Missing source_url when topic is correction fails
        res = self.client.post(reverse("public:feedback"), {
            "topic": "correction",
            "full_name": "Nguyễn Văn Test",
            "email": "test@example.com",
            "phone": "0912345678",
            "source_url": "",
            "message": "Cần sửa năm sinh",
            "consent": "on",
        })
        self.assertEqual(res.status_code, 200)
        self.assertFormError(res.context["form"], "source_url", "Vui lòng cung cấp đường link nguồn (bài báo, cổng ĐKKD, quyết định...) để Ban biên tập đối chiếu và xác nhận thông tin.")

        # 3. Valid submission succeeds
        res = self.client.post(reverse("public:feedback"), {
            "topic": "correction",
            "full_name": "Nguyễn Văn Test",
            "email": "test@example.com",
            "phone": "0912345678",
            "source_url": "https://dangkykinhdoanh.gov.vn/dn/123",
            "message": "Cần sửa thông tin doanh nghiệp",
            "consent": "on",
        })
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.context["done"])
        msg = ContactMessage.objects.get(email="test@example.com")
        self.assertEqual(msg.phone, "0912345678")
        self.assertEqual(msg.source_url, "https://dangkykinhdoanh.gov.vn/dn/123")

        # 4. Admin views contact detail with source_url
        editor = make_user("editor_fb@example.com", role="editor")
        self.client.force_login(editor)
        res_admin = self.client.get(reverse("staff:contact_detail", args=[msg.pk]))
        self.assertEqual(res_admin.status_code, 200)
        self.assertContains(res_admin, "Nguồn đối chiếu / kiểm chứng")
        self.assertContains(res_admin, "https://dangkykinhdoanh.gov.vn/dn/123")


class BackupDbCommandTest(TestCase):
    def test_backup_db_creates_compressed_file(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            out = io.StringIO()
            call_command("backup_db", output_dir=tmpdir, keep_days=7, stdout=out)
            output = out.getvalue()
            self.assertIn("Sao lưu thành công", output)
            files = list(Path(tmpdir).glob("backup_doanhnhan_*"))
            self.assertEqual(len(files), 1)
            self.assertTrue(files[0].stat().st_size > 0)

    def test_backup_db_prunes_old_files(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "backup_doanhnhan_20200101_000000.sqlite3.gz"
            old_file.write_text("old dummy")
            old_time = time.time() - (30 * 86400)
            os.utime(old_file, (old_time, old_time))

            out = io.StringIO()
            call_command("backup_db", output_dir=tmpdir, keep_days=7, stdout=out)
            output = out.getvalue()
            self.assertIn("Đã dọn dẹp 1 bản sao lưu cũ", output)
            self.assertFalse(old_file.exists())


class PersonPhonePrivacyTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.member = make_user("member_phone@example.com")
        self.admin = make_user("admin_phone@example.com", role="admin")
        self.editor = make_user("editor_phone@example.com", role="editor")
        self.person = Person.objects.create(
            full_name="Doanh Nhân Bảo Mật",
            headline="Chủ tịch",
            phone="0912345678",
            status=Status.PUBLISHED,
        )

    def test_mask_phone_utility(self):
        from apps.common.text import mask_phone
        self.assertEqual(mask_phone("0912345678"), "0912****78")
        self.assertEqual(mask_phone("0912 345 678"), "0912 *** *78")
        self.assertEqual(mask_phone("+84912345678"), "+8491*****78")
        self.assertEqual(mask_phone(""), "")

    def test_public_view_masks_phone_and_hides_reveal_button(self):
        # Khách vãng lai
        res = self.client.get(self.person.get_absolute_url())
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "0912****78")
        self.assertNotIn("0912345678", res.content.decode("utf-8"))
        self.assertNotContains(res, "btn-reveal-phone")

        # Thành viên thường đã đăng nhập
        self.login(self.member)
        res_member = self.client.get(self.person.get_absolute_url())
        self.assertContains(res_member, "0912****78")
        self.assertNotIn("0912345678", res_member.content.decode("utf-8"))
        self.assertNotContains(res_member, "btn-reveal-phone")

    def test_admin_sees_reveal_button_and_can_unmask_phone(self):
        self.login(self.admin)
        res = self.client.get(self.person.get_absolute_url())
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "0912****78")
        self.assertContains(res, "btn-reveal-phone")

        # Gọi endpoint mở xem số điện thoại
        res_reveal = self.client.get(reverse("public:person_reveal_phone", args=[self.person.pk]))
        self.assertEqual(res_reveal.status_code, 200)
        data = res_reveal.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["phone"], "0912345678")
        self.assertEqual(data["masked"], "0912****78")

        # Kiểm tra ghi log kiểm toán (AuditLog)
        self.assertTrue(AuditLog.objects.filter(actor=self.admin, action="person.reveal_phone").exists())

    def test_non_admin_cannot_call_reveal_endpoint(self):
        # Thành viên thường bị 403 Forbidden
        self.login(self.member)
        res_member = self.client.get(reverse("public:person_reveal_phone", args=[self.person.pk]))
        self.assertEqual(res_member.status_code, 403)

        # Biên tập viên (chưa phải Admin) cũng bị 403 Forbidden
        self.login(self.editor)
        res_editor = self.client.get(reverse("public:person_reveal_phone", args=[self.person.pk]))
        self.assertEqual(res_editor.status_code, 403)

    def test_person_submission_with_phone_and_masked_protection(self):
        self.login(self.member)
        r = self.client.post(reverse("member:person_create"), {
            "full_name": "Doanh Nhân Mới",
            "headline": "Giám đốc",
            "phone": "0988776655",
            "action": "draft",
        })
        rev = Revision.objects.filter(data__full_name="Doanh Nhân Mới").first()
        self.assertIsNotNone(rev)
        self.assertEqual(rev.data.get("phone"), "0988776655")

        # Khi chỉnh sửa với chuỗi đã bị mask, không bị ghi đè thành dấu *
        self.person.refresh_from_db()
        self.assertEqual(self.person.phone, "0912345678")
        self.client.post(reverse("member:person_edit", args=[self.person.slug]), {
            "full_name": self.person.full_name,
            "headline": "Chủ tịch mới",
            "phone": "0912****78",  # Gửi lại chuỗi mask
            "action": "draft",
        })
        rev2 = Revision.objects.filter(person=self.person).first()
        self.assertEqual(rev2.data.get("phone"), "0912345678")


class StoryFeatureTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.editor = make_user("editor_story@example.com", role="editor")
        self.person = Person.objects.create(full_name="Nguyễn Văn Doanh Nhân", headline="Chủ tịch HĐQT", status=Status.PUBLISHED)
        self.company = Company.objects.create(legal_name="Tập đoàn Công nghệ Mới", brand_name="NewTech", status=Status.PUBLISHED)
        self.story = Story.objects.create(
            title="Hành trình khởi nghiệp từ hai bàn tay trắng",
            story_type=Story.StoryType.PORTRAIT,
            summary="Câu chuyện vượt khó và hành trình xây dựng thương hiệu công nghệ.",
            content_md="## Khởi nguồn đam mê\n\nTừ những năm tháng đầu tiên...",
            featured_person=self.person,
            featured_company=self.company,
            is_featured=True,
            status=Status.PUBLISHED,
            published_at=timezone.now(),
        )
        self.draft_story = Story.objects.create(
            title="Bài viết nháp chưa xuất bản",
            summary="Tóm tắt nháp",
            content_md="Nội dung nháp",
            status=Status.DRAFT,
        )

    def test_navbar_contains_story_and_not_sectors(self):
        res = self.client.get(reverse("public:home"))
        self.assertEqual(res.status_code, 200)
        nav_keys = [item[0] for item in res.context["NAV"]]
        self.assertIn("stories", nav_keys)
        self.assertNotIn("sectors", nav_keys)
        # Kiểm tra thẻ header trên giao diện
        html = res.content.decode("utf-8")
        header_part = html[html.find("<header"):html.find("</header>")]
        self.assertIn("/story/", header_part)
        self.assertIn("Story", header_part)
        self.assertNotIn("/nganh-nghe/", header_part)

    def test_public_story_list_and_detail(self):
        # List
        res = self.client.get(reverse("public:story_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Hành trình khởi nghiệp từ hai bàn tay trắng")
        self.assertNotContains(res, "Bài viết nháp chưa xuất bản")

        # Detail
        res_detail = self.client.get(reverse("public:story_detail", args=[self.story.slug]))
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, "Hành trình khởi nghiệp từ hai bàn tay trắng")
        self.assertContains(res_detail, "Khởi nguồn đam mê")
        self.assertContains(res_detail, "Nguyễn Văn Doanh Nhân")

        # Filter by category
        res_filter = self.client.get(reverse("public:story_list") + "?loai=portrait")
        self.assertEqual(res_filter.status_code, 200)
        self.assertContains(res_filter, "Hành trình khởi nghiệp từ hai bàn tay trắng")

        # Filter by mismatching category
        res_empty = self.client.get(reverse("public:story_list") + "?loai=event")
        self.assertEqual(res_empty.status_code, 200)
        self.assertContains(res_empty, "0</b> bài viết phù hợp")

        # Search by keyword
        res_search = self.client.get(reverse("public:story_list") + "?q=khởi+nghiệp")
        self.assertEqual(res_search.status_code, 200)
        self.assertContains(res_search, "Hành trình khởi nghiệp từ hai bàn tay trắng")

        # Draft detail 404 for anonymous
        res_draft = self.client.get(reverse("public:story_detail", args=[self.draft_story.slug]))
        self.assertEqual(res_draft.status_code, 404)

    def test_staff_story_crud(self):
        self.login(self.editor)

        # 1. Staff list
        res_list = self.client.get(reverse("staff:story_list"))
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, "Hành trình khởi nghiệp từ hai bàn tay trắng")
        self.assertContains(res_list, "Bài viết nháp chưa xuất bản")

        # 2. Staff create new story
        res_create = self.client.post(reverse("staff:story_new"), {
            "title": "Phóng sự về thế hệ lãnh đạo trẻ",
            "story_type": "event",
            "summary": "Tóm tắt về diễn đàn doanh nhân trẻ 2026",
            "content_md": "Diễn đàn quy tụ hơn 500 lãnh đạo trẻ tiêu biểu...",
            "status": "published",
            "published_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        })
        self.assertEqual(res_create.status_code, 302)
        new_story = Story.objects.filter(title="Phóng sự về thế hệ lãnh đạo trẻ").first()
        self.assertIsNotNone(new_story)

        # 3. Staff edit story
        res_edit = self.client.post(reverse("staff:story_edit", args=[new_story.pk]), {
            "title": "Phóng sự về thế hệ lãnh đạo trẻ (Đã cập nhật)",
            "story_type": "event",
            "summary": "Tóm tắt đã cập nhật",
            "content_md": "Nội dung cập nhật...",
            "status": "published",
            "published_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
        })
        self.assertEqual(res_edit.status_code, 302)
        new_story.refresh_from_db()
        self.assertEqual(new_story.title, "Phóng sự về thế hệ lãnh đạo trẻ (Đã cập nhật)")

        # 4. Toggle status
        self.client.post(reverse("staff:story_toggle_status", args=[new_story.pk]))
        new_story.refresh_from_db()
        self.assertEqual(new_story.status, Status.ARCHIVED)

        # 5. Delete story
        self.client.post(reverse("staff:story_delete", args=[new_story.pk]))
        self.assertFalse(Story.objects.filter(pk=new_story.pk).exists())


class AICrawlerTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.editor = make_user("editor_crawler@example.com", role="editor")
        self.member = make_user("member_crawler@example.com", role="member")

    def test_permissions(self):
        url = reverse("staff:ai_crawler")
        # Khách vãng lai: chuyển hướng đăng nhập
        self.assertEqual(self.client.get(url).status_code, 302)
        # Thành viên thường: 403 Forbidden
        self.login(self.member)
        self.assertEqual(self.client.get(url).status_code, 403)
        # Biên tập viên: 200 OK
        self.login(self.editor)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_crawler_analyze_api(self):
        self.login(self.editor)
        url = reverse("staff:ai_crawler_analyze")

        # Empty input -> 400
        res_empty = self.client.post(url, {"url_or_text": "   "}, content_type="application/json")
        self.assertEqual(res_empty.status_code, 400)
        self.assertFalse(res_empty.json()["ok"])

        # Valid text
        sample_text = (
            "Doanh nhân Phạm Nhật Vượng sáng lập Tập đoàn Vingroup (MST: 0101245486). "
            "Ông sinh năm 1968 tại Hà Nội, khởi nghiệp từ năm 1993."
        )
        res_valid = self.client.post(url, {"url_or_text": sample_text}, content_type="application/json")
        self.assertEqual(res_valid.status_code, 200)
        data = res_valid.json()
        self.assertTrue(data["ok"])
        self.assertTrue(data["data"]["has_person"])
        self.assertTrue(data["data"]["has_company"])
        self.assertEqual(data["data"]["company"]["tax_code"], "0101245486")

    def test_crawler_save_flow(self):
        self.login(self.editor)
        url = reverse("staff:ai_crawler_save")

        res = self.client.post(url, {
            "save_person": "1",
            "person_full_name": "Doanh Nhân Khởi Nghiệp",
            "person_headline": "Tổng Giám đốc NewTech",
            "person_gender": "female",
            "person_birth_year": "1992",
            "person_summary": "Tóm tắt về doanh nhân trẻ",
            "save_company": "1",
            "company_legal_name": "Công ty TNHH Đổi Mới Sáng Tạo NewTech",
            "company_brand_name": "NewTech VN",
            "company_tax_code": "0109988776",
            "relationship_role": "founder_ceo",
            "relationship_title": "Nhà sáng lập & CEO",
            "source_title": "Bài viết giới thiệu Doanh nhân trẻ tiêu biểu",
            "source_url": "https://tuoitre.vn/bai-viet-gioi-thieu",
            "source_publisher": "Báo Tuổi Trẻ",
            "milestone_year": ["2018", "2024"],
            "milestone_title": ["Thành lập NewTech", "Đạt doanh thu 100 tỷ"],
            "milestone_kind": ["founding", "award"],
            "status": "published",
        })
        self.assertEqual(res.status_code, 302)

        person = Person.objects.filter(full_name="Doanh Nhân Khởi Nghiệp").first()
        self.assertIsNotNone(person)
        self.assertEqual(person.birth_year, 1992)
        self.assertEqual(person.milestones.count(), 2)
        self.assertEqual(person.sources.count(), 1)

        company = Company.objects.filter(tax_code="0109988776").first()
        self.assertIsNotNone(company)
        self.assertEqual(company.brand_name, "NewTech VN")

        # Quan hệ PersonCompany
        link = PersonCompany.objects.filter(person=person, company=company).first()
        self.assertIsNotNone(link)
        self.assertEqual(link.role, "founder_ceo")

        # Log kiểm toán
        self.assertTrue(AuditLog.objects.filter(actor=self.editor, action="ai.crawler_import").exists())


class PodcastFeatureTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.editor = make_user("editor_podcast@example.com", role="editor")
        self.person = Person.objects.filter(status=Status.PUBLISHED).first()
        self.podcast = Podcast.objects.create(
            title="Tập 1: Bản lĩnh người tiên phong",
            episode_number=1,
            series_type=Podcast.SeriesType.STARTUP,
            series_name="Đối thoại Doanh nhân",
            host_name="Ban Biên tập",
            guest_person=self.person,
            summary="Câu chuyện về những ngày đầu khởi nghiệp và bài học thương trường đắt giá.",
            content_md="### Nội dung\n- [00:00] Khởi nghiệp\n- [15:00] Thử thách",
            audio_url="https://example.com/audio1.mp3",
            duration_minutes=45,
            is_featured=True,
            status=Status.PUBLISHED,
        )

    def test_navigation_menu_order_and_items(self):
        """Kiểm tra thứ tự thanh menu: Doanh nhân, Story, Sự kiện, Podcast, Video, Hiệp hội."""
        from apps.common.context_processors import NAV
        labels = [item[1] for item in NAV]
        self.assertEqual(labels, ["Doanh nhân", "Story", "Sự kiện", "Podcast", "Video", "Hiệp hội"])
        self.assertNotIn("Doanh nghiệp", labels)

        # Kiểm tra hiển thị trên trang chủ
        res = self.client.get(reverse("public:home"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Podcast")
        self.assertContains(res, "/podcast/")

    def test_podcast_public_list_and_aliases(self):
        """Kiểm tra trang danh sách podcast công khai và alias /postcast/."""
        res = self.client.get(reverse("public:podcast_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Bản lĩnh người tiên phong")

        # Alias /postcast/
        res_alias = self.client.get("/postcast/")
        self.assertEqual(res_alias.status_code, 200)
        self.assertContains(res_alias, "Bản lĩnh người tiên phong")

        # Lọc theo series
        res_series = self.client.get(reverse("public:podcast_list"), {"chu-de": "startup"})
        self.assertEqual(res_series.status_code, 200)
        self.assertContains(res_series, "Bản lĩnh người tiên phong")

        # Tìm kiếm từ khóa
        res_search = self.client.get(reverse("public:podcast_list"), {"q": "tiên phong"})
        self.assertEqual(res_search.status_code, 200)
        self.assertContains(res_search, "Bản lĩnh người tiên phong")

    def test_podcast_public_detail_and_tracking(self):
        """Kiểm tra trang chi tiết và endpoint ghi nhận lượt nghe."""
        initial_views = self.podcast.views_count
        res = self.client.get(reverse("public:podcast_detail", kwargs={"slug": self.podcast.slug}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.podcast.title)

        self.podcast.refresh_from_db()
        self.assertEqual(self.podcast.views_count, initial_views + 1)

        # Track play
        initial_listeners = self.podcast.listeners_count
        res_play = self.client.get(reverse("public:podcast_track_play", kwargs={"slug": self.podcast.slug}))
        self.assertEqual(res_play.status_code, 200)
        self.podcast.refresh_from_db()
        self.assertEqual(self.podcast.listeners_count, initial_listeners + 1)

    def test_podcast_staff_crud(self):
        """Kiểm tra quy trình quản trị podcast: danh sách, tạo mới, sửa, đổi trạng thái, xóa."""
        self.login(self.editor)

        # 1. Staff list
        res = self.client.get(reverse("staff:podcast_list"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.podcast.title)

        # 2. Tạo mới tập podcast
        res_create = self.client.post(reverse("staff:podcast_new"), {
            "title": "Tập 2: Đổi mới sáng tạo trong kỷ nguyên AI",
            "episode_number": 2,
            "series_type": Podcast.SeriesType.INNOVATION,
            "series_name": "Công nghệ & Tương lai",
            "host_name": "Ban Biên tập",
            "guest_custom": "Chuyên gia Công nghệ",
            "summary": "Tầm quan trọng của trí tuệ nhân tạo đối với doanh nghiệp.",
            "duration_minutes": 50,
            "status": "published",
        })
        self.assertEqual(res_create.status_code, 302)
        new_pod = Podcast.objects.filter(title="Tập 2: Đổi mới sáng tạo trong kỷ nguyên AI").first()
        self.assertIsNotNone(new_pod)
        self.assertEqual(new_pod.series_type, Podcast.SeriesType.INNOVATION)

        # 3. Sửa tập podcast
        res_edit = self.client.post(reverse("staff:podcast_edit", args=[new_pod.pk]), {
            "title": "Tập 2: Đổi mới sáng tạo trong kỷ nguyên AI - Cập nhật",
            "episode_number": 2,
            "series_type": Podcast.SeriesType.INNOVATION,
            "series_name": "Công nghệ & Tương lai",
            "host_name": "Ban Biên tập",
            "guest_custom": "Chuyên gia Công nghệ Hàng Đầu",
            "summary": "Tầm quan trọng của trí tuệ nhân tạo đối với doanh nghiệp.",
            "duration_minutes": 55,
            "status": "published",
        })
        self.assertEqual(res_edit.status_code, 302)
        new_pod.refresh_from_db()
        self.assertEqual(new_pod.title, "Tập 2: Đổi mới sáng tạo trong kỷ nguyên AI - Cập nhật")
        self.assertEqual(new_pod.duration_minutes, 55)

        # 4. Toggle ẩn / hiện
        res_toggle = self.client.post(reverse("staff:podcast_toggle_status", args=[new_pod.pk]))
        self.assertEqual(res_toggle.status_code, 302)
        new_pod.refresh_from_db()
        self.assertEqual(new_pod.status, Status.ARCHIVED)

        # 5. Xóa tập podcast
        res_del = self.client.post(reverse("staff:podcast_delete", args=[new_pod.pk]))
        self.assertEqual(res_del.status_code, 302)
        self.assertFalse(Podcast.objects.filter(pk=new_pod.pk).exists())











