-- doanhnhan.wiki · 03 – Dữ liệu THỬ NGHIỆM HƯ CẤU
-- Sinh tự động từ PostgreSQL ngày 20/10/2026 bằng sql/xuat_sql.sh. Mã hóa UTF-8.
-- 24 doanh nhân, 24 doanh nghiệp, 4 hiệp hội, 6 sự kiện, 11 tài khoản @example.com (mật khẩu Demo@2026!), bài gửi chờ duyệt, phỏng vấn, liên hệ, tài khoản tài trợ, video link example.com. Không phải người hay doanh nghiệp thật. Xóa trước khi chạy thật: python manage.py seed_test --xoa --xac-nhan

BEGIN;
SET CONSTRAINTS ALL DEFERRED;
--
-- PostgreSQL database dump
--

\restrict LKmpzhC1CZdSRxA7QH6LZ3S7VFFkZh7fqmcXTEV2DpXpE4yDvyUfErFLBg8jcmJ

-- Dumped from database version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: accounts_user; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.accounts_user (id, password, last_login, is_superuser, email, full_name, phone, role, status, auth_provider, google_sub, newsletter, failed_logins, locked_until, is_active, is_staff, date_joined) VALUES (1, 'pbkdf2_sha256$1000000$MxAdY8asbqFnawbSlxUNIf$Q2KM1ExpQT3B8RfnRK/VNPn5D+m2aynScrZY1mqCJaM=', NULL, false, 'quantri1@example.com', 'Quản trị Một (thử)', '0900000000', 'admin', 'active', 'email', NULL, false, 0, NULL, true, true, '2026-10-20 00:49:41.032646+00');
INSERT INTO public.accounts_user (id, password, last_login, is_superuser, email, full_name, phone, role, status, auth_provider, google_sub, newsletter, failed_logins, locked_until, is_active, is_staff, date_joined) VALUES (2, 'pbkdf2_sha256$1000000$6gjGq7t0TOGtP8cjtBhJLM$z1uzisMqKVrSlmAQA2OXReV91azEYiVnZlEtOaUdXJg=', NULL, false, 'quantri2@example.com', 'Quản trị Hai (thử)', '0900000000', 'admin', 'active', 'email', NULL, false, 0, NULL, true, true, '2026-10-20 00:49:41.975432+00');
INSERT INTO public.accounts_user (id, password, last_login, is_superuser, email, full_name, phone, role, status, auth_provider, google_sub, newsletter, failed_logins, locked_until, is_active, is_staff, date_joined) VALUES (3, 'pbkdf2_sha256$1000000$Cv3c3yIXYiMSIJTFpfRzKd$brBsVeV+R+r36iI/uBje0HaiR2FXlZqN5MNgSbCqoHY=', NULL, false, 'bientap@example.com', 'Biên tập Viên (thử)', '0900000000', 'editor', 'active', 'email', NULL, false, 0, NULL, true, false, '2026-10-20 00:49:42.79793+00');
INSERT INTO public.accounts_user (id, password, last_login, is_superuser, email, full_name, phone, role, status, auth_provider, google_sub, newsletter, failed_logins, locked_until, is_active, is_staff, date_joined) VALUES (4, 'pbkdf2_sha256$1000000$D2VKk71jL6aplLNmBLYw3C$0ioSU+qxt6mDrqiF5LKE3v1szv/174HWq6VW4OqZqls=', NULL, false, 'doanhnhan@example.com', 'Nguyễn Minh An (hồ sơ mẫu)', '0900000000', 'member', 'active', 'email', NULL, false, 0, NULL, true, false, '2026-10-20 00:49:43.546679+00');
INSERT INTO public.accounts_user (id, password, last_login, is_superuser, email, full_name, phone, role, status, auth_provider, google_sub, newsletter, failed_logins, locked_until, is_active, is_staff, date_joined) VALUES (5, 'pbkdf2_sha256$1000000$II59B0jfFFYOin0SVlaW0b$iNyUQX8ESUMrG30bq9r5mfGSETZXSp8x3RDX77ytK1M=', NULL, false, 'doanhnghiep@example.com', 'Đại Diện Doanh Nghiệp (thử)', '0900000000', 'member', 'active', 'email', NULL, false, 0, NULL, true, false, '2026-10-20 00:49:44.560586+00');
INSERT INTO public.accounts_user (id, password, last_login, is_superuser, email, full_name, phone, role, status, auth_provider, google_sub, newsletter, failed_logins, locked_until, is_active, is_staff, date_joined) VALUES (6, 'pbkdf2_sha256$1000000$6KyX9INUvmw4icQS9Ij4Tr$EtDtHTCBkw5rq31dZSHY8h95vw2w7QS1WS2QqZgBGgI=', NULL, false, 'hiephoi@example.com', 'Đại Diện Hiệp Hội (thử)', '0900000000', 'member', 'active', 'email', NULL, false, 0, NULL, true, false, '2026-10-20 00:49:45.451945+00');
INSERT INTO public.accounts_user (id, password, last_login, is_superuser, email, full_name, phone, role, status, auth_provider, google_sub, newsletter, failed_logins, locked_until, is_active, is_staff, date_joined) VALUES (7, 'pbkdf2_sha256$1000000$EvXQjWv36FDBsAvrlS0W5C$JBVFrsOiaJTRYLjo5QU19PDbF0xBvPtmDMh5hwK/AJ0=', NULL, false, 'congtacvien@example.com', 'Cộng Tác Viên (thử)', '0900000000', 'member', 'active', 'email', NULL, false, 0, NULL, true, false, '2026-10-20 00:49:46.113928+00');
INSERT INTO public.accounts_user (id, password, last_login, is_superuser, email, full_name, phone, role, status, auth_provider, google_sub, newsletter, failed_logins, locked_until, is_active, is_staff, date_joined) VALUES (8, 'pbkdf2_sha256$1000000$ph8IUX4ptRhHUjMkEQVp6B$mtPWmcAkdgVef0fvzWBXSJB8GPTC8WrlvfQemDkuY44=', NULL, false, 'choduyet@example.com', 'Người Chờ Duyệt (thử)', '0900000000', 'member', 'pending', 'email', NULL, false, 0, NULL, true, false, '2026-10-20 00:49:46.957435+00');
INSERT INTO public.accounts_user (id, password, last_login, is_superuser, email, full_name, phone, role, status, auth_provider, google_sub, newsletter, failed_logins, locked_until, is_active, is_staff, date_joined) VALUES (9, 'pbkdf2_sha256$1000000$wx8NFiiCJbdBwXi9dhYEbx$g9CcSfwgiivGw+u1U1fbeEceFm2T9LSm65shFK5kf8c=', NULL, false, 'canbosung@example.com', 'Người Cần Bổ Sung (thử)', '0900000000', 'member', 'pending', 'email', NULL, false, 0, NULL, true, false, '2026-10-20 00:49:47.59615+00');
INSERT INTO public.accounts_user (id, password, last_login, is_superuser, email, full_name, phone, role, status, auth_provider, google_sub, newsletter, failed_logins, locked_until, is_active, is_staff, date_joined) VALUES (10, 'pbkdf2_sha256$1000000$jMcrYqZchn2zbl9ihiPVtv$bUvaDY4LLumCVZ9rTVW6TD0zilLHQHsp3ase/IRgZIM=', NULL, false, 'tuchoi@example.com', 'Người Bị Từ Chối (thử)', '0900000000', 'member', 'rejected', 'email', NULL, false, 0, NULL, true, false, '2026-10-20 00:49:48.363349+00');
INSERT INTO public.accounts_user (id, password, last_login, is_superuser, email, full_name, phone, role, status, auth_provider, google_sub, newsletter, failed_logins, locked_until, is_active, is_staff, date_joined) VALUES (11, 'pbkdf2_sha256$1000000$NBeTgquhBQhNoq23D8YdqB$9X0QWRiaZdcXh+VKxCU1PwOaaWeQY8gTmVGRdjTnZN8=', NULL, false, 'bikhoa@example.com', 'Người Bị Khóa (thử)', '0900000000', 'member', 'suspended', 'email', NULL, false, 0, NULL, true, false, '2026-10-20 00:49:49.148646+00');


--
-- Data for Name: accounts_accountapplication; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.accounts_accountapplication (id, applicant_type, organization, intro, reference_url, status, reviewed_at, review_note, created_at, reviewed_by_id, user_id) VALUES (1, 'contributor', '', 'Hồ sơ đăng ký thử nghiệm: Biên tập Viên (thử).', 'https://example.com/gioi-thieu', 'approved', '2026-10-20 00:49:41.025181+00', '', '2026-10-20 00:49:43.545537+00', 3, 3);
INSERT INTO public.accounts_accountapplication (id, applicant_type, organization, intro, reference_url, status, reviewed_at, review_note, created_at, reviewed_by_id, user_id) VALUES (2, 'entrepreneur', 'An Phát (mẫu)', 'Hồ sơ đăng ký thử nghiệm: Nguyễn Minh An (hồ sơ mẫu).', 'https://example.com/gioi-thieu', 'approved', '2026-10-20 00:49:41.025181+00', '', '2026-10-20 00:49:44.559858+00', 3, 4);
INSERT INTO public.accounts_accountapplication (id, applicant_type, organization, intro, reference_url, status, reviewed_at, review_note, created_at, reviewed_by_id, user_id) VALUES (3, 'company_rep', 'Lá Xanh (mẫu)', 'Hồ sơ đăng ký thử nghiệm: Đại Diện Doanh Nghiệp (thử).', 'https://example.com/gioi-thieu', 'approved', '2026-10-20 00:49:41.025181+00', '', '2026-10-20 00:49:45.451225+00', 3, 5);
INSERT INTO public.accounts_accountapplication (id, applicant_type, organization, intro, reference_url, status, reviewed_at, review_note, created_at, reviewed_by_id, user_id) VALUES (4, 'association_rep', 'Hội Doanh nhân trẻ mẫu', 'Hồ sơ đăng ký thử nghiệm: Đại Diện Hiệp Hội (thử).', 'https://example.com/gioi-thieu', 'approved', '2026-10-20 00:49:41.025181+00', '', '2026-10-20 00:49:46.113511+00', 3, 6);
INSERT INTO public.accounts_accountapplication (id, applicant_type, organization, intro, reference_url, status, reviewed_at, review_note, created_at, reviewed_by_id, user_id) VALUES (5, 'contributor', '', 'Hồ sơ đăng ký thử nghiệm: Cộng Tác Viên (thử).', 'https://example.com/gioi-thieu', 'approved', '2026-10-20 00:49:41.025181+00', '', '2026-10-20 00:49:46.956979+00', 3, 7);
INSERT INTO public.accounts_accountapplication (id, applicant_type, organization, intro, reference_url, status, reviewed_at, review_note, created_at, reviewed_by_id, user_id) VALUES (6, 'entrepreneur', 'Công ty Chờ Duyệt (mẫu)', 'Hồ sơ đăng ký thử nghiệm: Người Chờ Duyệt (thử).', 'https://example.com/gioi-thieu', 'pending', NULL, '', '2026-10-20 00:49:47.595483+00', NULL, 8);
INSERT INTO public.accounts_accountapplication (id, applicant_type, organization, intro, reference_url, status, reviewed_at, review_note, created_at, reviewed_by_id, user_id) VALUES (8, 'contributor', '', 'Hồ sơ đăng ký thử nghiệm: Người Bị Từ Chối (thử).', 'https://example.com/gioi-thieu', 'rejected', '2026-10-20 00:49:41.025181+00', 'Thông tin chưa đủ để xác minh (dữ liệu thử).', '2026-10-20 00:49:49.148121+00', 3, 10);
INSERT INTO public.accounts_accountapplication (id, applicant_type, organization, intro, reference_url, status, reviewed_at, review_note, created_at, reviewed_by_id, user_id) VALUES (9, 'contributor', '', 'Hồ sơ đăng ký thử nghiệm: Người Bị Khóa (thử).', 'https://example.com/gioi-thieu', 'approved', '2026-10-20 00:49:41.025181+00', '', '2026-10-20 00:49:50.118697+00', 3, 11);
INSERT INTO public.accounts_accountapplication (id, applicant_type, organization, intro, reference_url, status, reviewed_at, review_note, created_at, reviewed_by_id, user_id) VALUES (7, 'company_rep', 'Công ty Bổ Sung (mẫu)', 'Hồ sơ đăng ký thử nghiệm: Người Cần Bổ Sung (thử).', 'https://example.com/gioi-thieu', 'needs_info', '2026-10-20 00:49:41.025181+00', 'Vui lòng gửi link website hoặc giấy đăng ký kinh doanh (dữ liệu thử).', '2026-10-20 00:49:48.362709+00', 3, 9);


--
-- Data for Name: accounts_rolechangerequest; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.accounts_rolechangerequest (id, new_role, status, created_at, resolved_at, confirmed_by_id, requested_by_id, target_id) VALUES (1, 'admin', 'pending', '2026-10-20 00:49:50.244804+00', NULL, NULL, 1, 3);


--
-- Data for Name: directory_company; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (1, 'an-phat-mau', 'cong ty tnhh an phat (mau) an phat (mau)', '2026-10-20 00:49:40.342307+00', '2026-10-20 00:49:40.34232+00', 'Công ty TNHH An Phát (mẫu)', 'An Phát (mẫu)', NULL, 2009, 'Số 1 đường Mẫu, TP. Hồ Chí Minh', 'lt10', '', '', '', 'published', 'verified', '', NULL, true, '2026-10-20 00:00:00+00', true, NULL, 2, 2);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (3, 'bao-long-mau', 'cong ty tnhh bao long (mau) bao long (mau)', '2026-10-20 00:49:40.389387+00', '2026-10-20 00:49:40.389401+00', 'Công ty TNHH Bảo Long (mẫu)', 'Bảo Long (mẫu)', NULL, 2018, 'Số 3 đường Mẫu, Đà Nẵng', '10_50', '', '', '', 'published', 'none', '', NULL, true, '2026-10-18 00:00:00+00', true, NULL, 4, 4);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (4, 'sao-mai-mau', 'cong ty tnhh sao mai (mau) sao mai (mau)', '2026-10-20 00:49:40.410016+00', '2026-10-20 00:49:40.41003+00', 'Công ty TNHH Sao Mai (mẫu)', 'Sao Mai (mẫu)', NULL, 2009, 'Số 4 đường Mẫu, Cần Thơ', '50_200', '', '', '', 'published', 'association', '', NULL, true, '2026-10-17 00:00:00+00', true, NULL, 5, 5);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (5, 'hung-thinh-mau', 'cong ty tnhh hung thinh (mau) hung thinh (mau)', '2026-10-20 00:49:40.436052+00', '2026-10-20 00:49:40.436076+00', 'Công ty TNHH Hưng Thịnh (mẫu)', 'Hưng Thịnh (mẫu)', NULL, 2011, 'Số 5 đường Mẫu, Hải Phòng', 'gt200', '', '', '', 'published', 'verified', '', NULL, false, '2026-10-16 00:00:00+00', true, NULL, 3, 6);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (6, 'moc-lan-mau', 'cong ty tnhh moc lan (mau) moc lan (mau)', '2026-10-20 00:49:40.459664+00', '2026-10-20 00:49:40.459687+00', 'Công ty TNHH Mộc Lan (mẫu)', 'Mộc Lan (mẫu)', NULL, 2017, 'Số 6 đường Mẫu, Đồng Nai', 'lt10', '', '', '', 'published', 'basic', '', NULL, false, '2026-10-15 00:00:00+00', true, NULL, 13, 7);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (7, 'viet-tin-mau', 'cong ty tnhh viet tin (mau) viet tin (mau)', '2026-10-20 00:49:40.481031+00', '2026-10-20 00:49:40.481047+00', 'Công ty TNHH Việt Tín (mẫu)', 'Việt Tín (mẫu)', NULL, 2016, 'Số 7 đường Mẫu, Bắc Ninh', '10_50', '', '', '', 'published', 'none', '', NULL, false, '2026-10-14 00:00:00+00', true, NULL, 8, 9);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (8, 'phuong-nam-mau', 'cong ty tnhh phuong nam (mau) phuong nam (mau)', '2026-10-20 00:49:40.509975+00', '2026-10-20 00:49:40.509997+00', 'Công ty TNHH Phương Nam (mẫu)', 'Phương Nam (mẫu)', NULL, 2020, 'Số 8 đường Mẫu, Khánh Hòa', '10_50', '', '', '', 'published', 'association', '', NULL, false, '2026-10-13 00:00:00+00', true, NULL, 18, 10);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (9, 'dai-duong-mau', 'cong ty tnhh dai duong (mau) dai duong (mau)', '2026-10-20 00:49:40.532752+00', '2026-10-20 00:49:40.532767+00', 'Công ty TNHH Đại Dương (mẫu)', 'Đại Dương (mẫu)', NULL, 2016, 'Số 9 đường Mẫu, Lâm Đồng', '50_200', '', '', '', 'published', 'verified', '', NULL, false, '2026-10-12 00:00:00+00', true, NULL, 20, 11);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (10, 'hoa-binh-mau', 'cong ty tnhh hoa binh (mau) hoa binh (mau)', '2026-10-20 00:49:40.557523+00', '2026-10-20 00:49:40.557541+00', 'Công ty TNHH Hòa Bình (mẫu)', 'Hòa Bình (mẫu)', NULL, 2019, 'Số 10 đường Mẫu, An Giang', 'gt200', '', '', '', 'published', 'basic', '', NULL, false, '2026-10-11 00:00:00+00', true, NULL, 7, 12);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (11, 'tan-tien-mau', 'cong ty tnhh tan tien (mau) tan tien (mau)', '2026-10-20 00:49:40.579455+00', '2026-10-20 00:49:40.579472+00', 'Công ty TNHH Tân Tiến (mẫu)', 'Tân Tiến (mẫu)', NULL, 2020, 'Số 11 đường Mẫu, Nghệ An', 'lt10', '', '', '', 'published', 'none', '', NULL, false, '2026-10-10 00:00:00+00', true, NULL, 23, 14);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (12, 'anh-duong-mau', 'cong ty tnhh anh duong (mau) anh duong (mau)', '2026-10-20 00:49:40.603081+00', '2026-10-20 00:49:40.603095+00', 'Công ty TNHH Ánh Dương (mẫu)', 'Ánh Dương (mẫu)', NULL, 2020, 'Số 12 đường Mẫu, Huế', '10_50', '', '', '', 'published', 'association', '', NULL, false, '2026-10-09 00:00:00+00', true, NULL, 6, 15);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (13, 'truong-son-mau', 'cong ty tnhh truong son (mau) truong son (mau)', '2026-10-20 00:49:40.624425+00', '2026-10-20 00:49:40.624442+00', 'Công ty TNHH Trường Sơn (mẫu)', 'Trường Sơn (mẫu)', NULL, 2017, 'Số 13 đường Mẫu, TP. Hồ Chí Minh', '10_50', '', '', '', 'published', 'verified', '', NULL, false, '2026-10-08 00:00:00+00', true, NULL, 2, 16);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (14, 'kim-ngan-mau', 'cong ty tnhh kim ngan (mau) kim ngan (mau)', '2026-10-20 00:49:40.650102+00', '2026-10-20 00:49:40.650165+00', 'Công ty TNHH Kim Ngân (mẫu)', 'Kim Ngân (mẫu)', NULL, 2011, 'Số 14 đường Mẫu, Hà Nội', '50_200', '', '', '', 'published', 'basic', '', NULL, false, '2026-10-07 00:00:00+00', true, NULL, 1, 18);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (15, 'binh-minh-mau', 'cong ty tnhh binh minh (mau) binh minh (mau)', '2026-10-20 00:49:40.678007+00', '2026-10-20 00:49:40.678037+00', 'Công ty TNHH Bình Minh (mẫu)', 'Bình Minh (mẫu)', NULL, 2017, 'Số 15 đường Mẫu, Đà Nẵng', 'gt200', '', '', '', 'published', 'none', '', NULL, false, '2026-10-06 00:00:00+00', true, NULL, 4, 19);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (16, 'thien-phu-mau', 'cong ty tnhh thien phu (mau) thien phu (mau)', '2026-10-20 00:49:40.701481+00', '2026-10-20 00:49:40.701497+00', 'Công ty TNHH Thiên Phú (mẫu)', 'Thiên Phú (mẫu)', NULL, 2009, 'Số 16 đường Mẫu, Cần Thơ', 'lt10', '', '', '', 'published', 'association', '', NULL, false, '2026-10-05 00:00:00+00', true, NULL, 5, 20);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (17, 'hong-ha-mau', 'cong ty tnhh hong ha (mau) hong ha (mau)', '2026-10-20 00:49:40.722905+00', '2026-10-20 00:49:40.722933+00', 'Công ty TNHH Hồng Hà (mẫu)', 'Hồng Hà (mẫu)', NULL, 2021, 'Số 17 đường Mẫu, Hải Phòng', '10_50', '', '', '', 'published', 'verified', '', NULL, false, '2026-10-04 00:00:00+00', true, NULL, 3, 22);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (18, 'cuu-long-mau', 'cong ty tnhh cuu long (mau) cuu long (mau)', '2026-10-20 00:49:40.749507+00', '2026-10-20 00:49:40.749528+00', 'Công ty TNHH Cửu Long (mẫu)', 'Cửu Long (mẫu)', NULL, 2015, 'Số 18 đường Mẫu, Đồng Nai', '10_50', '', '', '', 'published', 'basic', '', NULL, false, '2026-10-03 00:00:00+00', true, NULL, 13, 24);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (19, 'nhat-quang-mau', 'cong ty tnhh nhat quang (mau) nhat quang (mau)', '2026-10-20 00:49:40.780524+00', '2026-10-20 00:49:40.780544+00', 'Công ty TNHH Nhật Quang (mẫu)', 'Nhật Quang (mẫu)', NULL, 2021, 'Số 19 đường Mẫu, Bắc Ninh', '50_200', '', '', '', 'published', 'none', '', NULL, false, '2026-10-02 00:00:00+00', true, NULL, 8, 27);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (20, 'minh-khang-mau', 'cong ty tnhh minh khang (mau) minh khang (mau)', '2026-10-20 00:49:40.806516+00', '2026-10-20 00:49:40.806537+00', 'Công ty TNHH Minh Khang (mẫu)', 'Minh Khang (mẫu)', NULL, 2018, 'Số 20 đường Mẫu, Khánh Hòa', 'gt200', '', '', '', 'published', 'association', '', NULL, false, '2026-10-01 00:00:00+00', true, NULL, 18, 28);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (21, 'gia-hung-mau', 'cong ty tnhh gia hung (mau) gia hung (mau)', '2026-10-20 00:49:40.828743+00', '2026-10-20 00:49:40.82876+00', 'Công ty TNHH Gia Hưng (mẫu)', 'Gia Hưng (mẫu)', NULL, 2018, 'Số 21 đường Mẫu, Lâm Đồng', 'lt10', '', '', '', 'published', 'verified', '', NULL, false, '2026-09-30 00:00:00+00', true, NULL, 20, 30);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (22, 'phu-quy-mau', 'cong ty tnhh phu quy (mau) phu quy (mau)', '2026-10-20 00:49:40.850609+00', '2026-10-20 00:49:40.850628+00', 'Công ty TNHH Phú Quý (mẫu)', 'Phú Quý (mẫu)', NULL, 2011, 'Số 22 đường Mẫu, An Giang', '10_50', '', '', '', 'published', 'basic', '', NULL, false, '2026-09-29 00:00:00+00', true, NULL, 7, 32);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (23, 'thanh-dat-mau', 'cong ty tnhh thanh dat (mau) thanh dat (mau)', '2026-10-20 00:49:40.872249+00', '2026-10-20 00:49:40.872272+00', 'Công ty TNHH Thành Đạt (mẫu)', 'Thành Đạt (mẫu)', NULL, 2012, 'Số 23 đường Mẫu, Nghệ An', '10_50', '', '', '', 'published', 'none', '', NULL, false, '2026-09-28 00:00:00+00', true, NULL, 23, 34);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (24, 'van-xuan-mau', 'cong ty tnhh van xuan (mau) van xuan (mau)', '2026-10-20 00:49:40.896389+00', '2026-10-20 00:49:40.896407+00', 'Công ty TNHH Vạn Xuân (mẫu)', 'Vạn Xuân (mẫu)', NULL, 2022, 'Số 24 đường Mẫu, Huế', '50_200', '', '', '', 'published', 'association', '', NULL, false, '2026-09-27 00:00:00+00', true, NULL, 6, 35);
INSERT INTO public.directory_company (id, slug, search_text, created_at, updated_at, legal_name, brand_name, tax_code, founded_year, address, size_band, website, logo, cover, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, province_id, primary_sector_id) VALUES (2, 'la-xanh-mau', 'cong ty tnhh la xanh (mau) la xanh (mau)', '2026-10-20 00:49:40.369669+00', '2026-10-20 00:49:40.369684+00', 'Công ty TNHH Lá Xanh (mẫu)', 'Lá Xanh (mẫu)', NULL, 2016, 'Số 2 đường Mẫu, Hà Nội', '10_50', '', '', '', 'published', 'basic', '', NULL, true, '2026-10-19 00:00:00+00', true, 5, 1, 3);


--
-- Data for Name: directory_person; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (2, 'tran-ngoc-ha-ho-so-mau', 'tran ngoc ha (ho so mau) nha sang lap & ceo la xanh (mau) la xanh (mau)', '2026-10-20 00:49:40.374741+00', '2026-10-20 00:49:40.387032+00', 'Trần Ngọc Hà (hồ sơ mẫu)', 1990, 'Nhà sáng lập & CEO Lá Xanh (mẫu)', '', '', '', true, true, false, 'published', 'basic', '', NULL, true, '2026-10-17 00:00:00+00', true, NULL, 1, 18);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (3, 'le-thao-bao-ho-so-mau', 'le thao bao (ho so mau) dong sang lap bao long (mau) bao long (mau)', '2026-10-20 00:49:40.394388+00', '2026-10-20 00:49:40.407964+00', 'Lê Thảo Bảo (hồ sơ mẫu)', 1995, 'Đồng sáng lập Bảo Long (mẫu)', '', '', '', true, true, false, 'published', 'none', '', NULL, true, '2026-10-14 00:00:00+00', true, NULL, 4, 4);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (4, 'pham-thanh-linh-ho-so-mau', 'pham thanh linh (ho so mau) tong giam doc / ceo sao mai (mau) sao mai (mau)', '2026-10-20 00:49:40.413832+00', '2026-10-20 00:49:40.432953+00', 'Phạm Thanh Linh (hồ sơ mẫu)', 1996, 'Tổng giám đốc / CEO Sao Mai (mẫu)', '', '', '', true, true, false, 'published', 'association', '', NULL, true, '2026-10-11 00:00:00+00', true, NULL, 5, 7);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (5, 'hoang-khanh-nam-ho-so-mau', 'hoang khanh nam (ho so mau) nha sang lap hung thinh (mau) hung thinh (mau)', '2026-10-20 00:49:40.441924+00', '2026-10-20 00:49:40.456709+00', 'Hoàng Khánh Nam (hồ sơ mẫu)', 1996, 'Nhà sáng lập Hưng Thịnh (mẫu)', '', '', '', true, true, false, 'published', 'verified', '', NULL, true, '2026-10-08 00:00:00+00', true, NULL, 3, 3);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (6, 'vo-thu-vy-ho-so-mau', 'vo thu vy (ho so mau) nha sang lap & ceo moc lan (mau) moc lan (mau)', '2026-10-20 00:49:40.464599+00', '2026-10-20 00:49:40.478561+00', 'Võ Thu Vy (hồ sơ mẫu)', 1991, 'Nhà sáng lập & CEO Mộc Lan (mẫu)', '', '', '', true, true, false, 'published', 'basic', '', NULL, true, '2026-10-05 00:00:00+00', true, NULL, 13, 6);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (7, 'dang-duc-phuc-ho-so-mau', 'dang duc phuc (ho so mau) nha sang lap & ceo viet tin (mau) viet tin (mau)', '2026-10-20 00:49:40.486063+00', '2026-10-20 00:49:40.506944+00', 'Đặng Đức Phúc (hồ sơ mẫu)', 1988, 'Nhà sáng lập & CEO Việt Tín (mẫu)', '', '', '', true, true, false, 'published', 'none', '', NULL, true, '2026-10-02 00:00:00+00', true, NULL, 8, 8);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (8, 'bui-anh-trang-ho-so-mau', 'bui anh trang (ho so mau) dong sang lap phuong nam (mau) phuong nam (mau)', '2026-10-20 00:49:40.515765+00', '2026-10-20 00:49:40.530027+00', 'Bùi Anh Trang (hồ sơ mẫu)', 1991, 'Đồng sáng lập Phương Nam (mẫu)', '', '', '', true, true, false, 'published', 'association', '', NULL, true, '2026-09-29 00:00:00+00', true, NULL, 18, 1);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (9, 'do-hai-khoa-ho-so-mau', 'do hai khoa (ho so mau) tong giam doc / ceo dai duong (mau) dai duong (mau)', '2026-10-20 00:49:40.53733+00', '2026-10-20 00:49:40.554983+00', 'Đỗ Hải Khoa (hồ sơ mẫu)', 1995, 'Tổng giám đốc / CEO Đại Dương (mẫu)', '', '', '', true, true, false, 'published', 'verified', '', NULL, false, '2026-09-26 00:00:00+00', true, NULL, 20, 20);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (10, 'ho-bao-mai-ho-so-mau', 'ho bao mai (ho so mau) nha sang lap hoa binh (mau) hoa binh (mau)', '2026-10-20 00:49:40.5615+00', '2026-10-20 00:49:40.576479+00', 'Hồ Bảo Mai (hồ sơ mẫu)', 1994, 'Nhà sáng lập Hòa Bình (mẫu)', '', '', '', true, true, false, 'published', 'basic', '', NULL, false, '2026-09-23 00:00:00+00', true, NULL, 7, 5);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (11, 'ngo-quoc-tuan-ho-so-mau', 'ngo quoc tuan (ho so mau) nha sang lap & ceo tan tien (mau) tan tien (mau)', '2026-10-20 00:49:40.584633+00', '2026-10-20 00:49:40.600665+00', 'Ngô Quốc Tuấn (hồ sơ mẫu)', 1989, 'Nhà sáng lập & CEO Tân Tiến (mẫu)', '', '', '', true, true, false, 'published', 'none', '', NULL, false, '2026-09-20 00:00:00+00', true, NULL, 23, 23);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (12, 'duong-gia-chau-ho-so-mau', 'duong gia chau (ho so mau) nha sang lap & ceo anh duong (mau) anh duong (mau)', '2026-10-20 00:49:40.607303+00', '2026-10-20 00:49:40.621996+00', 'Dương Gia Châu (hồ sơ mẫu)', 1994, 'Nhà sáng lập & CEO Ánh Dương (mẫu)', '', '', '', true, true, false, 'published', 'association', '', NULL, false, '2026-09-17 00:00:00+00', true, NULL, 6, 13);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (13, 'nguyen-minh-long-ho-so-mau', 'nguyen minh long (ho so mau) dong sang lap truong son (mau) truong son (mau)', '2026-10-20 00:49:40.629427+00', '2026-10-20 00:49:40.647811+00', 'Nguyễn Minh Long (hồ sơ mẫu)', 1989, 'Đồng sáng lập Trường Sơn (mẫu)', '', '', '', true, true, false, 'published', 'verified', '', NULL, false, '2026-09-14 00:00:00+00', true, NULL, 2, 2);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (1, 'nguyen-minh-an-ho-so-mau', 'nguyen minh an (ho so mau) nha sang lap & ceo an phat (mau) an phat (mau)', '2026-10-20 00:49:40.34909+00', '2026-10-20 00:49:40.36661+00', 'Nguyễn Minh An (hồ sơ mẫu)', 1987, 'Nhà sáng lập & CEO An Phát (mẫu)', '', '', '', true, true, false, 'published', 'verified', '', NULL, true, '2026-10-20 00:00:00+00', true, 4, 2, 2);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (14, 'tran-ngoc-nhi-ho-so-mau', 'tran ngoc nhi (ho so mau) tong giam doc / ceo kim ngan (mau) kim ngan (mau)', '2026-10-20 00:49:40.654496+00', '2026-10-20 00:49:40.675089+00', 'Trần Ngọc Nhi (hồ sơ mẫu)', 1982, 'Tổng giám đốc / CEO Kim Ngân (mẫu)', '', '', '', true, true, false, 'published', 'basic', '', NULL, false, '2026-09-11 00:00:00+00', true, NULL, 1, 18);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (15, 'le-thao-huy-ho-so-mau', 'le thao huy (ho so mau) nha sang lap binh minh (mau) binh minh (mau)', '2026-10-20 00:49:40.683145+00', '2026-10-20 00:49:40.699355+00', 'Lê Thảo Huy (hồ sơ mẫu)', 1983, 'Nhà sáng lập Bình Minh (mẫu)', '', '', '', true, true, false, 'published', 'none', '', NULL, false, '2026-09-08 00:00:00+00', true, NULL, 4, 4);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (16, 'pham-thanh-ngan-ho-so-mau', 'pham thanh ngan (ho so mau) nha sang lap & ceo thien phu (mau) thien phu (mau)', '2026-10-20 00:49:40.705198+00', '2026-10-20 00:49:40.719784+00', 'Phạm Thanh Ngân (hồ sơ mẫu)', 1986, 'Nhà sáng lập & CEO Thiên Phú (mẫu)', '', '', '', true, true, false, 'published', 'association', '', NULL, false, '2026-09-05 00:00:00+00', true, NULL, 5, 7);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (17, 'hoang-khanh-son-ho-so-mau', 'hoang khanh son (ho so mau) nha sang lap & ceo hong ha (mau) hong ha (mau)', '2026-10-20 00:49:40.728235+00', '2026-10-20 00:49:40.746598+00', 'Hoàng Khánh Sơn (hồ sơ mẫu)', 1983, 'Nhà sáng lập & CEO Hồng Hà (mẫu)', '', '', '', true, true, false, 'published', 'verified', '', NULL, false, '2026-09-02 00:00:00+00', true, NULL, 3, 3);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (18, 'vo-thu-thu-ho-so-mau', 'vo thu thu (ho so mau) dong sang lap cuu long (mau) cuu long (mau)', '2026-10-20 00:49:40.755189+00', '2026-10-20 00:49:40.77738+00', 'Võ Thu Thư (hồ sơ mẫu)', 1982, 'Đồng sáng lập Cửu Long (mẫu)', '', '', '', true, true, false, 'published', 'basic', '', NULL, false, '2026-08-30 00:00:00+00', true, NULL, 13, 6);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (19, 'dang-duc-dat-ho-so-mau', 'dang duc dat (ho so mau) tong giam doc / ceo nhat quang (mau) nhat quang (mau)', '2026-10-20 00:49:40.785938+00', '2026-10-20 00:49:40.803517+00', 'Đặng Đức Đạt (hồ sơ mẫu)', 1996, 'Tổng giám đốc / CEO Nhật Quang (mẫu)', '', '', '', true, true, false, 'published', 'none', '', NULL, false, '2026-08-27 00:00:00+00', true, NULL, 8, 8);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (20, 'bui-anh-yen-ho-so-mau', 'bui anh yen (ho so mau) nha sang lap minh khang (mau) minh khang (mau)', '2026-10-20 00:49:40.811673+00', '2026-10-20 00:49:40.825975+00', 'Bùi Anh Yến (hồ sơ mẫu)', 1989, 'Nhà sáng lập Minh Khang (mẫu)', '', '', '', true, true, false, 'published', 'association', '', NULL, false, '2026-08-24 00:00:00+00', true, NULL, 18, 1);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (21, 'do-hai-tin-ho-so-mau', 'do hai tin (ho so mau) nha sang lap & ceo gia hung (mau) gia hung (mau)', '2026-10-20 00:49:40.833427+00', '2026-10-20 00:49:40.84784+00', 'Đỗ Hải Tín (hồ sơ mẫu)', 1987, 'Nhà sáng lập & CEO Gia Hưng (mẫu)', '', '', '', true, true, false, 'published', 'verified', '', NULL, false, '2026-08-21 00:00:00+00', true, NULL, 20, 20);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (22, 'ho-bao-my-ho-so-mau', 'ho bao my (ho so mau) nha sang lap & ceo phu quy (mau) phu quy (mau)', '2026-10-20 00:49:40.85568+00', '2026-10-20 00:49:40.869598+00', 'Hồ Bảo My (hồ sơ mẫu)', 1988, 'Nhà sáng lập & CEO Phú Quý (mẫu)', '', '', '', true, true, false, 'published', 'basic', '', NULL, false, '2026-08-18 00:00:00+00', true, NULL, 7, 5);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (23, 'ngo-quoc-quan-ho-so-mau', 'ngo quoc quan (ho so mau) dong sang lap thanh dat (mau) thanh dat (mau)', '2026-10-20 00:49:40.877218+00', '2026-10-20 00:49:40.893622+00', 'Ngô Quốc Quân (hồ sơ mẫu)', 1987, 'Đồng sáng lập Thành Đạt (mẫu)', '', '', '', true, true, false, 'published', 'none', '', NULL, false, '2026-08-15 00:00:00+00', true, NULL, 23, 23);
INSERT INTO public.directory_person (id, slug, search_text, created_at, updated_at, full_name, birth_year, headline, portrait, email_public, website, show_birth_year, show_hometown, show_email, status, verification, verification_note, verified_at, is_featured, published_at, is_demo, owner_id, current_province_id, hometown_id) VALUES (24, 'duong-gia-huong-ho-so-mau', 'duong gia huong (ho so mau) tong giam doc / ceo van xuan (mau) van xuan (mau)', '2026-10-20 00:49:40.90151+00', '2026-10-20 00:49:40.91787+00', 'Dương Gia Hương (hồ sơ mẫu)', 1987, 'Tổng giám đốc / CEO Vạn Xuân (mẫu)', '', '', '', true, true, false, 'published', 'association', '', NULL, false, '2026-08-12 00:00:00+00', true, NULL, 6, 13);


--
-- Data for Name: directory_articlesection; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (1, 'summary', 'Nguyễn Minh An là nhân vật hư cấu, nhà sáng lập & ceo an phát (mẫu), hoạt động trong lĩnh vực phần mềm doanh nghiệp tại TP. Hồ Chí Minh.[^1]', 30, 0, NULL, 1);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (2, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 1);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (3, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 1);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (4, 'achievements', '- 2014 — Giải thưởng doanh nhân trẻ (mẫu).[^2]', 9, 3, NULL, 1);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (5, 'philosophy', '> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”', 12, 4, NULL, 1);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (6, 'overview', 'An Phát (mẫu) là doanh nghiệp hư cấu trong lĩnh vực phần mềm doanh nghiệp, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 22, 0, 1, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (7, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 1, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (8, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 1, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (9, 'summary', 'Trần Ngọc Hà là nhân vật hư cấu, nhà sáng lập & ceo lá xanh (mẫu), hoạt động trong lĩnh vực thương mại điện tử tại Hà Nội.[^1]', 28, 0, NULL, 2);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (10, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 2);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (11, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 2);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (12, 'overview', 'Lá Xanh (mẫu) là doanh nghiệp hư cấu trong lĩnh vực thương mại điện tử, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 22, 0, 2, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (13, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 2, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (14, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 2, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (15, 'summary', 'Lê Thảo Bảo là nhân vật hư cấu, đồng sáng lập bảo long (mẫu), hoạt động trong lĩnh vực fintech tại Đà Nẵng.[^1]', 23, 0, NULL, 3);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (16, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 3);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (17, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 3);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (18, 'achievements', '- 2023 — Giải thưởng doanh nhân trẻ (mẫu).[^2]', 9, 3, NULL, 3);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (19, 'philosophy', '> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”', 12, 4, NULL, 3);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (20, 'overview', 'Bảo Long (mẫu) là doanh nghiệp hư cấu trong lĩnh vực fintech, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 19, 0, 3, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (21, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 3, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (22, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 3, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (23, 'summary', 'Phạm Thanh Linh là nhân vật hư cấu, tổng giám đốc / ceo sao mai (mẫu), hoạt động trong lĩnh vực ai & dữ liệu tại Cần Thơ.[^1]', 28, 0, NULL, 4);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (24, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 4);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (25, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 4);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (26, 'overview', 'Sao Mai (mẫu) là doanh nghiệp hư cấu trong lĩnh vực ai & dữ liệu, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 22, 0, 4, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (27, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 4, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (28, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 4, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (29, 'summary', 'Hoàng Khánh Nam là nhân vật hư cấu, nhà sáng lập hưng thịnh (mẫu), hoạt động trong lĩnh vực edtech tại Hải Phòng.[^1]', 23, 0, NULL, 5);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (30, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 5);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (31, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 5);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (32, 'achievements', '- 2016 — Giải thưởng doanh nhân trẻ (mẫu).[^2]', 9, 3, NULL, 5);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (33, 'philosophy', '> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”', 12, 4, NULL, 5);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (34, 'overview', 'Hưng Thịnh (mẫu) là doanh nghiệp hư cấu trong lĩnh vực edtech, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 19, 0, 5, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (35, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 5, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (36, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 5, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (37, 'summary', 'Võ Thu Vy là nhân vật hư cấu, nhà sáng lập & ceo mộc lan (mẫu), hoạt động trong lĩnh vực marketing số tại Đồng Nai.[^1]', 26, 0, NULL, 6);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (38, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 6);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (39, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 6);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (40, 'overview', 'Mộc Lan (mẫu) là doanh nghiệp hư cấu trong lĩnh vực marketing số, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 20, 0, 6, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (41, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 6, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (42, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 6, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (43, 'summary', 'Đặng Đức Phúc là nhân vật hư cấu, nhà sáng lập & ceo việt tín (mẫu), hoạt động trong lĩnh vực cơ khí – chế tạo tại Bắc Ninh.[^1]', 29, 0, NULL, 7);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (44, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 7);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (45, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 7);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (46, 'achievements', '- 2021 — Giải thưởng doanh nhân trẻ (mẫu).[^2]', 9, 3, NULL, 7);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (47, 'philosophy', '> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”', 12, 4, NULL, 7);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (48, 'overview', 'Việt Tín (mẫu) là doanh nghiệp hư cấu trong lĩnh vực cơ khí – chế tạo, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 23, 0, 7, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (49, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 7, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (50, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 7, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (51, 'summary', 'Bùi Anh Trang là nhân vật hư cấu, đồng sáng lập phương nam (mẫu), hoạt động trong lĩnh vực vật liệu xây dựng tại Khánh Hòa.[^1]', 26, 0, NULL, 8);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (52, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 8);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (53, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 8);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (54, 'overview', 'Phương Nam (mẫu) là doanh nghiệp hư cấu trong lĩnh vực vật liệu xây dựng, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 22, 0, 8, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (55, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 8, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (56, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 8, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (57, 'summary', 'Đỗ Hải Khoa là nhân vật hư cấu, tổng giám đốc / ceo đại dương (mẫu), hoạt động trong lĩnh vực dệt may – da giày tại Lâm Đồng.[^1]', 29, 0, NULL, 9);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (58, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 9);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (59, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 9);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (60, 'achievements', '- 2021 — Giải thưởng doanh nhân trẻ (mẫu).[^2]', 9, 3, NULL, 9);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (61, 'philosophy', '> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”', 12, 4, NULL, 9);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (62, 'overview', 'Đại Dương (mẫu) là doanh nghiệp hư cấu trong lĩnh vực dệt may – da giày, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 23, 0, 9, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (63, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 9, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (64, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 9, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (65, 'summary', 'Hồ Bảo Mai là nhân vật hư cấu, nhà sáng lập hòa bình (mẫu), hoạt động trong lĩnh vực bao bì – nhựa tại An Giang.[^1]', 26, 0, NULL, 10);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (66, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 10);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (67, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 10);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (68, 'overview', 'Hòa Bình (mẫu) là doanh nghiệp hư cấu trong lĩnh vực bao bì – nhựa, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 22, 0, 10, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (69, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 10, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (70, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 10, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (71, 'summary', 'Ngô Quốc Tuấn là nhân vật hư cấu, nhà sáng lập & ceo tân tiến (mẫu), hoạt động trong lĩnh vực chuỗi bán lẻ tại Nghệ An.[^1]', 27, 0, NULL, 11);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (72, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 11);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (73, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 11);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (74, 'achievements', '- 2025 — Giải thưởng doanh nhân trẻ (mẫu).[^2]', 9, 3, NULL, 11);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (75, 'philosophy', '> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”', 12, 4, NULL, 11);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (76, 'overview', 'Tân Tiến (mẫu) là doanh nghiệp hư cấu trong lĩnh vực chuỗi bán lẻ, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 21, 0, 11, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (77, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 11, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (78, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 11, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (79, 'summary', 'Dương Gia Châu là nhân vật hư cấu, nhà sáng lập & ceo ánh dương (mẫu), hoạt động trong lĩnh vực phân phối tại Huế.[^1]', 25, 0, NULL, 12);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (80, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 12);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (81, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 12);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (82, 'overview', 'Ánh Dương (mẫu) là doanh nghiệp hư cấu trong lĩnh vực phân phối, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 20, 0, 12, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (83, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 12, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (84, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 12, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (85, 'summary', 'Nguyễn Minh Long là nhân vật hư cấu, đồng sáng lập trường sơn (mẫu), hoạt động trong lĩnh vực xuất nhập khẩu tại TP. Hồ Chí Minh.[^1]', 27, 0, NULL, 13);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (86, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 13);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (87, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 13);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (88, 'achievements', '- 2022 — Giải thưởng doanh nhân trẻ (mẫu).[^2]', 9, 3, NULL, 13);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (89, 'philosophy', '> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”', 12, 4, NULL, 13);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (90, 'overview', 'Trường Sơn (mẫu) là doanh nghiệp hư cấu trong lĩnh vực xuất nhập khẩu, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 21, 0, 13, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (91, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 13, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (92, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 13, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (93, 'summary', 'Trần Ngọc Nhi là nhân vật hư cấu, tổng giám đốc / ceo kim ngân (mẫu), hoạt động trong lĩnh vực chuỗi nhà hàng tại Hà Nội.[^1]', 27, 0, NULL, 14);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (94, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 14);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (95, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 14);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (96, 'overview', 'Kim Ngân (mẫu) là doanh nghiệp hư cấu trong lĩnh vực chuỗi nhà hàng, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 21, 0, 14, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (97, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 14, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (98, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 14, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (99, 'summary', 'Lê Thảo Huy là nhân vật hư cấu, nhà sáng lập bình minh (mẫu), hoạt động trong lĩnh vực cà phê – đồ uống tại Đà Nẵng.[^1]', 27, 0, NULL, 15);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (100, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 15);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (101, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 15);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (102, 'achievements', '- 2022 — Giải thưởng doanh nhân trẻ (mẫu).[^2]', 9, 3, NULL, 15);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (103, 'philosophy', '> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”', 12, 4, NULL, 15);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (104, 'overview', 'Bình Minh (mẫu) là doanh nghiệp hư cấu trong lĩnh vực cà phê – đồ uống, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 23, 0, 15, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (105, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 15, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (106, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 15, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (107, 'summary', 'Phạm Thanh Ngân là nhân vật hư cấu, nhà sáng lập & ceo thiên phú (mẫu), hoạt động trong lĩnh vực thực phẩm chế biến tại Cần Thơ.[^1]', 28, 0, NULL, 16);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (108, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 16);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (136, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 20);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (164, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 24);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (109, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 16);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (110, 'overview', 'Thiên Phú (mẫu) là doanh nghiệp hư cấu trong lĩnh vực thực phẩm chế biến, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 22, 0, 16, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (111, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 16, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (112, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 16, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (113, 'summary', 'Hoàng Khánh Sơn là nhân vật hư cấu, nhà sáng lập & ceo hồng hà (mẫu), hoạt động trong lĩnh vực thi công xây dựng tại Hải Phòng.[^1]', 28, 0, NULL, 17);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (114, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 17);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (115, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 17);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (116, 'achievements', '- 2026 — Giải thưởng doanh nhân trẻ (mẫu).[^2]', 9, 3, NULL, 17);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (117, 'philosophy', '> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”', 12, 4, NULL, 17);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (118, 'overview', 'Hồng Hà (mẫu) là doanh nghiệp hư cấu trong lĩnh vực thi công xây dựng, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 22, 0, 17, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (119, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 17, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (120, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 17, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (121, 'summary', 'Võ Thu Thư là nhân vật hư cấu, đồng sáng lập cửu long (mẫu), hoạt động trong lĩnh vực nội thất – kiến trúc tại Đồng Nai.[^1]', 27, 0, NULL, 18);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (122, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 18);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (123, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 18);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (124, 'overview', 'Cửu Long (mẫu) là doanh nghiệp hư cấu trong lĩnh vực nội thất – kiến trúc, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 23, 0, 18, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (125, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 18, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (126, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 18, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (127, 'summary', 'Đặng Đức Đạt là nhân vật hư cấu, tổng giám đốc / ceo nhật quang (mẫu), hoạt động trong lĩnh vực đào tạo kỹ năng tại Bắc Ninh.[^1]', 28, 0, NULL, 19);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (128, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 19);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (129, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 19);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (130, 'achievements', '- 2026 — Giải thưởng doanh nhân trẻ (mẫu).[^2]', 9, 3, NULL, 19);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (131, 'philosophy', '> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”', 12, 4, NULL, 19);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (132, 'overview', 'Nhật Quang (mẫu) là doanh nghiệp hư cấu trong lĩnh vực đào tạo kỹ năng, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 22, 0, 19, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (133, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 19, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (134, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 19, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (135, 'summary', 'Bùi Anh Yến là nhân vật hư cấu, nhà sáng lập minh khang (mẫu), hoạt động trong lĩnh vực ngoại ngữ tại Khánh Hòa.[^1]', 24, 0, NULL, 20);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (137, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 20);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (138, 'overview', 'Minh Khang (mẫu) là doanh nghiệp hư cấu trong lĩnh vực ngoại ngữ, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 20, 0, 20, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (139, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 20, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (140, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 20, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (141, 'summary', 'Đỗ Hải Tín là nhân vật hư cấu, nhà sáng lập & ceo gia hưng (mẫu), hoạt động trong lĩnh vực nông sản sạch tại Lâm Đồng.[^1]', 27, 0, NULL, 21);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (142, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 21);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (143, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 21);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (144, 'achievements', '- 2023 — Giải thưởng doanh nhân trẻ (mẫu).[^2]', 9, 3, NULL, 21);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (145, 'philosophy', '> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”', 12, 4, NULL, 21);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (146, 'overview', 'Gia Hưng (mẫu) là doanh nghiệp hư cấu trong lĩnh vực nông sản sạch, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 21, 0, 21, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (147, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 21, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (148, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 21, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (149, 'summary', 'Hồ Bảo My là nhân vật hư cấu, nhà sáng lập & ceo phú quý (mẫu), hoạt động trong lĩnh vực thủy sản tại An Giang.[^1]', 26, 0, NULL, 22);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (150, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 22);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (151, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 22);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (152, 'overview', 'Phú Quý (mẫu) là doanh nghiệp hư cấu trong lĩnh vực thủy sản, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 20, 0, 22, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (153, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 22, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (154, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 22, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (155, 'summary', 'Ngô Quốc Quân là nhân vật hư cấu, đồng sáng lập thành đạt (mẫu), hoạt động trong lĩnh vực vận tải tại Nghệ An.[^1]', 24, 0, NULL, 23);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (156, 'biography', 'Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.', 27, 1, NULL, 23);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (157, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 23);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (158, 'achievements', '- 2017 — Giải thưởng doanh nhân trẻ (mẫu).[^2]', 9, 3, NULL, 23);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (159, 'philosophy', '> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”', 12, 4, NULL, 23);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (160, 'overview', 'Thành Đạt (mẫu) là doanh nghiệp hư cấu trong lĩnh vực vận tải, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 20, 0, 23, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (161, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 23, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (162, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 23, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (163, 'summary', 'Dương Gia Hương là nhân vật hư cấu, tổng giám đốc / ceo vạn xuân (mẫu), hoạt động trong lĩnh vực kho bãi tại Huế.[^1]', 25, 0, NULL, 24);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (165, 'journey', '## Ý tưởng ban đầu
Đoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]

## Những năm đầu và khó khăn
Sản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.

> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”

## Bước ngoặt và phát triển
Mở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]

## Hiện nay
Vai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.', 142, 2, NULL, 24);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (166, 'overview', 'Vạn Xuân (mẫu) là doanh nghiệp hư cấu trong lĩnh vực kho bãi, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]', 20, 0, 24, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (167, 'history', 'Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.', 15, 1, 24, NULL);
INSERT INTO public.directory_articlesection (id, key, body_md, word_count, sort_order, company_id, person_id) VALUES (168, 'products', 'Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính.', 11, 2, 24, NULL);


--
-- Data for Name: directory_association; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_association (id, slug, search_text, created_at, updated_at, name, short_name, level, is_partner, partner_since, description, logo, website, status, parent_id, province_id) VALUES (1, 'hdnt-tq', 'hoi doanh nhan tre mau toan quoc (mau) hdnt-tq', '2026-10-20 00:49:40.311615+00', '2026-10-20 00:49:40.31164+00', 'Hội Doanh nhân trẻ mẫu Toàn quốc (mẫu)', 'HDNT-TQ', 'national', true, '2025-10-20', '**Hội Doanh nhân trẻ mẫu Toàn quốc (mẫu)** là tổ chức hư cấu dùng để minh họa trang hiệp hội trên doanhnhan.wiki.', '', '', 'published', NULL, 1);
INSERT INTO public.directory_association (id, slug, search_text, created_at, updated_at, name, short_name, level, is_partner, partner_since, description, logo, website, status, parent_id, province_id) VALUES (2, 'hdnt-hcm', 'hoi doanh nhan tre mau tp. ho chi minh (mau) hdnt-hcm', '2026-10-20 00:49:40.315618+00', '2026-10-20 00:49:40.315641+00', 'Hội Doanh nhân trẻ mẫu TP. Hồ Chí Minh (mẫu)', 'HDNT-HCM', 'provincial', true, '2025-10-20', '**Hội Doanh nhân trẻ mẫu TP. Hồ Chí Minh (mẫu)** là tổ chức hư cấu dùng để minh họa trang hiệp hội trên doanhnhan.wiki.', '', '', 'published', 1, 2);
INSERT INTO public.directory_association (id, slug, search_text, created_at, updated_at, name, short_name, level, is_partner, partner_since, description, logo, website, status, parent_id, province_id) VALUES (3, 'ch-sg', 'chi hoi doanh nhan tre mau sai gon (mau) ch-sg', '2026-10-20 00:49:40.317937+00', '2026-10-20 00:49:40.317953+00', 'Chi hội Doanh nhân trẻ mẫu Sài Gòn (mẫu)', 'CH-SG', 'branch', true, '2025-10-20', '**Chi hội Doanh nhân trẻ mẫu Sài Gòn (mẫu)** là tổ chức hư cấu dùng để minh họa trang hiệp hội trên doanhnhan.wiki.', '', '', 'published', 2, 2);
INSERT INTO public.directory_association (id, slug, search_text, created_at, updated_at, name, short_name, level, is_partner, partner_since, description, logo, website, status, parent_id, province_id) VALUES (4, 'clb-cn', 'clb doanh nhan cong nghe mau (mau) clb-cn', '2026-10-20 00:49:40.320181+00', '2026-10-20 00:49:40.320199+00', 'CLB Doanh nhân Công nghệ mẫu (mẫu)', 'CLB-CN', 'club', false, NULL, '**CLB Doanh nhân Công nghệ mẫu (mẫu)** là tổ chức hư cấu dùng để minh họa trang hiệp hội trên doanhnhan.wiki.', '', '', 'published', 1, 4);


--
-- Data for Name: directory_association_sectors; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_association_sectors (id, association_id, sector_id) VALUES (1, 4, 1);


--
-- Data for Name: directory_company_sectors; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (1, 1, 1);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (2, 1, 2);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (3, 2, 1);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (4, 2, 3);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (5, 3, 1);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (6, 3, 4);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (7, 4, 1);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (8, 4, 5);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (9, 5, 1);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (10, 5, 6);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (11, 6, 1);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (12, 6, 7);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (13, 7, 8);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (14, 7, 9);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (15, 8, 8);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (16, 8, 10);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (17, 9, 8);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (18, 9, 11);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (19, 10, 8);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (20, 10, 12);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (21, 11, 13);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (22, 11, 14);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (23, 12, 13);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (24, 12, 15);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (25, 13, 16);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (26, 13, 13);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (27, 14, 17);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (28, 14, 18);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (29, 15, 17);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (30, 15, 19);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (31, 16, 17);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (32, 16, 20);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (33, 17, 21);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (34, 17, 22);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (35, 18, 24);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (36, 18, 21);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (37, 19, 25);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (38, 19, 27);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (39, 20, 25);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (40, 20, 28);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (41, 21, 29);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (42, 21, 30);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (43, 22, 32);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (44, 22, 29);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (45, 23, 33);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (46, 23, 34);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (47, 24, 33);
INSERT INTO public.directory_company_sectors (id, company_id, sector_id) VALUES (48, 24, 35);


--
-- Data for Name: directory_companyproduct; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (1, 'Sản phẩm mẫu 1', 'Mô tả ngắn 1–2 câu.', 0, 1);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (2, 'Sản phẩm mẫu 2', 'Mô tả ngắn 1–2 câu.', 0, 2);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (3, 'Sản phẩm mẫu 3', 'Mô tả ngắn 1–2 câu.', 0, 3);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (4, 'Sản phẩm mẫu 4', 'Mô tả ngắn 1–2 câu.', 0, 4);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (5, 'Sản phẩm mẫu 5', 'Mô tả ngắn 1–2 câu.', 0, 5);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (6, 'Sản phẩm mẫu 6', 'Mô tả ngắn 1–2 câu.', 0, 6);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (7, 'Sản phẩm mẫu 7', 'Mô tả ngắn 1–2 câu.', 0, 7);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (8, 'Sản phẩm mẫu 8', 'Mô tả ngắn 1–2 câu.', 0, 8);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (9, 'Sản phẩm mẫu 9', 'Mô tả ngắn 1–2 câu.', 0, 9);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (10, 'Sản phẩm mẫu 10', 'Mô tả ngắn 1–2 câu.', 0, 10);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (11, 'Sản phẩm mẫu 11', 'Mô tả ngắn 1–2 câu.', 0, 11);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (12, 'Sản phẩm mẫu 12', 'Mô tả ngắn 1–2 câu.', 0, 12);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (13, 'Sản phẩm mẫu 13', 'Mô tả ngắn 1–2 câu.', 0, 13);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (14, 'Sản phẩm mẫu 14', 'Mô tả ngắn 1–2 câu.', 0, 14);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (15, 'Sản phẩm mẫu 15', 'Mô tả ngắn 1–2 câu.', 0, 15);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (16, 'Sản phẩm mẫu 16', 'Mô tả ngắn 1–2 câu.', 0, 16);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (17, 'Sản phẩm mẫu 17', 'Mô tả ngắn 1–2 câu.', 0, 17);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (18, 'Sản phẩm mẫu 18', 'Mô tả ngắn 1–2 câu.', 0, 18);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (19, 'Sản phẩm mẫu 19', 'Mô tả ngắn 1–2 câu.', 0, 19);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (20, 'Sản phẩm mẫu 20', 'Mô tả ngắn 1–2 câu.', 0, 20);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (21, 'Sản phẩm mẫu 21', 'Mô tả ngắn 1–2 câu.', 0, 21);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (22, 'Sản phẩm mẫu 22', 'Mô tả ngắn 1–2 câu.', 0, 22);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (23, 'Sản phẩm mẫu 23', 'Mô tả ngắn 1–2 câu.', 0, 23);
INSERT INTO public.directory_companyproduct (id, name, description, sort_order, company_id) VALUES (24, 'Sản phẩm mẫu 24', 'Mô tả ngắn 1–2 câu.', 0, 24);


--
-- Data for Name: directory_event; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_event (id, slug, search_text, created_at, updated_at, title, kind, starts_at, ends_at, venue, is_online, organizer_text, description, registration_url, cover, status, is_featured, organizer_id, province_id) VALUES (1, 'dien-dan-doanh-nhan-tre-mau-mau-2026', 'dien dan doanh nhan tre mau (mau) 2026', '2026-10-20 00:49:40.328511+00', '2026-10-20 00:49:40.328526+00', 'Diễn đàn Doanh nhân trẻ mẫu (mẫu)', 'conference', '2026-11-19 08:00:00+00', '2026-11-19 12:00:00+00', 'Hội trường mẫu số 1', false, '', 'Sự kiện **hư cấu** minh họa trang sự kiện: Diễn đàn Doanh nhân trẻ mẫu (mẫu).', '', '', 'published', true, 2, 2);
INSERT INTO public.directory_event (id, slug, search_text, created_at, updated_at, title, kind, starts_at, ends_at, venue, is_online, organizer_text, description, registration_url, cover, status, is_featured, organizer_id, province_id) VALUES (2, 'ket-noi-giao-thuong-mau-quy-iv-mau-2026', 'ket noi giao thuong mau quy iv (mau) 2026', '2026-10-20 00:49:40.331718+00', '2026-10-20 00:49:40.331739+00', 'Kết nối giao thương mẫu Quý IV (mẫu)', 'b2b', '2026-12-04 08:00:00+00', '2026-12-04 12:00:00+00', 'Hội trường mẫu số 2', false, '', 'Sự kiện **hư cấu** minh họa trang sự kiện: Kết nối giao thương mẫu Quý IV (mẫu).', '', '', 'published', false, 3, 2);
INSERT INTO public.directory_event (id, slug, search_text, created_at, updated_at, title, kind, starts_at, ends_at, venue, is_online, organizer_text, description, registration_url, cover, status, is_featured, organizer_id, province_id) VALUES (3, 'le-vinh-danh-doanh-nhan-tre-mau-mau-2027', 'le vinh danh doanh nhan tre mau (mau) 2027', '2026-10-20 00:49:40.3342+00', '2026-10-20 00:49:40.334219+00', 'Lễ vinh danh Doanh nhân trẻ mẫu (mẫu)', 'award', '2027-01-03 08:00:00+00', '2027-01-03 12:00:00+00', 'Hội trường mẫu số 3', false, '', 'Sự kiện **hư cấu** minh họa trang sự kiện: Lễ vinh danh Doanh nhân trẻ mẫu (mẫu).', '', '', 'published', false, 1, 1);
INSERT INTO public.directory_event (id, slug, search_text, created_at, updated_at, title, kind, starts_at, ends_at, venue, is_online, organizer_text, description, registration_url, cover, status, is_featured, organizer_id, province_id) VALUES (4, 'khoa-dao-tao-quan-tri-mau-mau-2026', 'khoa dao tao quan tri mau (mau) 2026', '2026-10-20 00:49:40.336592+00', '2026-10-20 00:49:40.336608+00', 'Khóa đào tạo quản trị mẫu (mẫu)', 'training', '2026-09-30 08:00:00+00', '2026-09-30 12:00:00+00', 'Hội trường mẫu số 4', false, '', 'Sự kiện **hư cấu** minh họa trang sự kiện: Khóa đào tạo quản trị mẫu (mẫu).', '', '', 'published', false, 4, 4);
INSERT INTO public.directory_event (id, slug, search_text, created_at, updated_at, title, kind, starts_at, ends_at, venue, is_online, organizer_text, description, registration_url, cover, status, is_featured, organizer_id, province_id) VALUES (5, 'hoi-thao-chuyen-doi-so-mau-mau-2026', 'hoi thao chuyen doi so mau (mau) 2026', '2026-10-20 00:49:40.338258+00', '2026-10-20 00:49:40.33827+00', 'Hội thảo chuyển đổi số mẫu (mẫu)', 'conference', '2026-08-21 08:00:00+00', '2026-08-21 12:00:00+00', 'Hội trường mẫu số 5', false, '', 'Sự kiện **hư cấu** minh họa trang sự kiện: Hội thảo chuyển đổi số mẫu (mẫu).', '', '', 'published', false, 4, 4);
INSERT INTO public.directory_event (id, slug, search_text, created_at, updated_at, title, kind, starts_at, ends_at, venue, is_online, organizer_text, description, registration_url, cover, status, is_featured, organizer_id, province_id) VALUES (6, 'dai-hoi-chi-hoi-mau-mau-2026', 'dai hoi chi hoi mau (mau) 2026', '2026-10-20 00:49:40.339769+00', '2026-10-20 00:49:40.33978+00', 'Đại hội Chi hội mẫu (mẫu)', 'gala', '2026-06-22 08:00:00+00', '2026-06-22 12:00:00+00', 'Hội trường mẫu số 6', false, '', 'Sự kiện **hư cấu** minh họa trang sự kiện: Đại hội Chi hội mẫu (mẫu).', '', '', 'published', false, 3, 2);


--
-- Data for Name: directory_milestone; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (1, 2009, 'founding', 'Thành lập An Phát (mẫu)', '', NULL, NULL, 1);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (2, 2009, 'founding', 'Thành lập An Phát (mẫu)', '', 1, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (3, 2012, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 1);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (4, 2012, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 1, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (5, 2015, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 1);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (6, 2015, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 1, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (7, 2016, 'founding', 'Thành lập Lá Xanh (mẫu)', '', NULL, NULL, 2);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (8, 2016, 'founding', 'Thành lập Lá Xanh (mẫu)', '', 2, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (9, 2019, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 2);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (10, 2019, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 2, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (11, 2022, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 2);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (12, 2022, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 2, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (13, 2018, 'founding', 'Thành lập Bảo Long (mẫu)', '', NULL, NULL, 3);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (14, 2018, 'founding', 'Thành lập Bảo Long (mẫu)', '', 3, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (15, 2021, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 3);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (16, 2021, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 3, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (17, 2024, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 3);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (18, 2024, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 3, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (19, 2009, 'founding', 'Thành lập Sao Mai (mẫu)', '', NULL, NULL, 4);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (20, 2009, 'founding', 'Thành lập Sao Mai (mẫu)', '', 4, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (21, 2012, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 4);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (22, 2012, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 4, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (23, 2015, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 4);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (24, 2015, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 4, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (25, 2011, 'founding', 'Thành lập Hưng Thịnh (mẫu)', '', NULL, NULL, 5);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (26, 2011, 'founding', 'Thành lập Hưng Thịnh (mẫu)', '', 5, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (27, 2014, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 5);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (28, 2014, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 5, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (29, 2017, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 5);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (30, 2017, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 5, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (31, 2017, 'founding', 'Thành lập Mộc Lan (mẫu)', '', NULL, NULL, 6);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (32, 2017, 'founding', 'Thành lập Mộc Lan (mẫu)', '', 6, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (33, 2020, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 6);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (34, 2020, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 6, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (35, 2023, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 6);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (36, 2023, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 6, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (37, 2016, 'founding', 'Thành lập Việt Tín (mẫu)', '', NULL, NULL, 7);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (38, 2016, 'founding', 'Thành lập Việt Tín (mẫu)', '', 7, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (39, 2019, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 7);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (40, 2019, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 7, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (41, 2022, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 7);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (42, 2022, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 7, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (43, 2020, 'founding', 'Thành lập Phương Nam (mẫu)', '', NULL, NULL, 8);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (44, 2020, 'founding', 'Thành lập Phương Nam (mẫu)', '', 8, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (45, 2023, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 8);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (46, 2023, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 8, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (47, 2026, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 8);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (48, 2026, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 8, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (49, 2016, 'founding', 'Thành lập Đại Dương (mẫu)', '', NULL, NULL, 9);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (50, 2016, 'founding', 'Thành lập Đại Dương (mẫu)', '', 9, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (51, 2019, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 9);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (52, 2019, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 9, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (53, 2022, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 9);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (54, 2022, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 9, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (55, 2019, 'founding', 'Thành lập Hòa Bình (mẫu)', '', NULL, NULL, 10);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (56, 2019, 'founding', 'Thành lập Hòa Bình (mẫu)', '', 10, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (57, 2022, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 10);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (58, 2022, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 10, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (59, 2025, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 10);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (60, 2025, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 10, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (61, 2020, 'founding', 'Thành lập Tân Tiến (mẫu)', '', NULL, NULL, 11);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (62, 2020, 'founding', 'Thành lập Tân Tiến (mẫu)', '', 11, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (63, 2023, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 11);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (64, 2023, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 11, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (65, 2026, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 11);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (66, 2026, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 11, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (67, 2020, 'founding', 'Thành lập Ánh Dương (mẫu)', '', NULL, NULL, 12);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (68, 2020, 'founding', 'Thành lập Ánh Dương (mẫu)', '', 12, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (69, 2023, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 12);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (70, 2023, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 12, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (71, 2026, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 12);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (72, 2026, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 12, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (73, 2017, 'founding', 'Thành lập Trường Sơn (mẫu)', '', NULL, NULL, 13);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (74, 2017, 'founding', 'Thành lập Trường Sơn (mẫu)', '', 13, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (75, 2020, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 13);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (76, 2020, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 13, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (77, 2023, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 13);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (78, 2023, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 13, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (79, 2011, 'founding', 'Thành lập Kim Ngân (mẫu)', '', NULL, NULL, 14);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (80, 2011, 'founding', 'Thành lập Kim Ngân (mẫu)', '', 14, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (81, 2014, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 14);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (82, 2014, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 14, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (83, 2017, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 14);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (84, 2017, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 14, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (85, 2017, 'founding', 'Thành lập Bình Minh (mẫu)', '', NULL, NULL, 15);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (86, 2017, 'founding', 'Thành lập Bình Minh (mẫu)', '', 15, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (87, 2020, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 15);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (88, 2020, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 15, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (89, 2023, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 15);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (90, 2023, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 15, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (91, 2009, 'founding', 'Thành lập Thiên Phú (mẫu)', '', NULL, NULL, 16);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (92, 2009, 'founding', 'Thành lập Thiên Phú (mẫu)', '', 16, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (93, 2012, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 16);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (94, 2012, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 16, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (95, 2015, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 16);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (96, 2015, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 16, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (97, 2021, 'founding', 'Thành lập Hồng Hà (mẫu)', '', NULL, NULL, 17);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (98, 2021, 'founding', 'Thành lập Hồng Hà (mẫu)', '', 17, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (99, 2024, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 17);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (100, 2024, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 17, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (101, 2027, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 17);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (102, 2027, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 17, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (103, 2015, 'founding', 'Thành lập Cửu Long (mẫu)', '', NULL, NULL, 18);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (104, 2015, 'founding', 'Thành lập Cửu Long (mẫu)', '', 18, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (105, 2018, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 18);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (106, 2018, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 18, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (107, 2021, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 18);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (108, 2021, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 18, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (109, 2021, 'founding', 'Thành lập Nhật Quang (mẫu)', '', NULL, NULL, 19);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (110, 2021, 'founding', 'Thành lập Nhật Quang (mẫu)', '', 19, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (111, 2024, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 19);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (112, 2024, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 19, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (113, 2027, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 19);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (114, 2027, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 19, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (115, 2018, 'founding', 'Thành lập Minh Khang (mẫu)', '', NULL, NULL, 20);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (116, 2018, 'founding', 'Thành lập Minh Khang (mẫu)', '', 20, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (117, 2021, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 20);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (118, 2021, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 20, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (119, 2024, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 20);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (120, 2024, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 20, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (121, 2018, 'founding', 'Thành lập Gia Hưng (mẫu)', '', NULL, NULL, 21);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (122, 2018, 'founding', 'Thành lập Gia Hưng (mẫu)', '', 21, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (123, 2021, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 21);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (124, 2021, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 21, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (125, 2024, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 21);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (126, 2024, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 21, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (127, 2011, 'founding', 'Thành lập Phú Quý (mẫu)', '', NULL, NULL, 22);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (128, 2011, 'founding', 'Thành lập Phú Quý (mẫu)', '', 22, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (129, 2014, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 22);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (130, 2014, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 22, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (131, 2017, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 22);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (132, 2017, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 22, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (133, 2012, 'founding', 'Thành lập Thành Đạt (mẫu)', '', NULL, NULL, 23);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (134, 2012, 'founding', 'Thành lập Thành Đạt (mẫu)', '', 23, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (135, 2015, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 23);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (136, 2015, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 23, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (137, 2018, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 23);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (138, 2018, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 23, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (139, 2022, 'founding', 'Thành lập Vạn Xuân (mẫu)', '', NULL, NULL, 24);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (140, 2022, 'founding', 'Thành lập Vạn Xuân (mẫu)', '', 24, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (141, 2025, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', NULL, NULL, 24);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (142, 2025, 'product', 'Ra mắt sản phẩm chủ lực (mẫu)', '', 24, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (143, 2028, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', NULL, NULL, 24);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (144, 2028, 'award', 'Nhận giải thưởng doanh nhân trẻ (mẫu)', '', 24, NULL, NULL);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (145, 2026, 'community', 'Diễn giả tại Khóa đào tạo quản trị mẫu (mẫu)', '', NULL, 4, 13);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (146, 2026, 'award', 'Nhận giải tại Khóa đào tạo quản trị mẫu (mẫu)', '', NULL, 4, 15);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (147, 2026, 'community', 'Diễn giả tại Hội thảo chuyển đổi số mẫu (mẫu)', '', NULL, 5, 17);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (148, 2026, 'award', 'Nhận giải tại Hội thảo chuyển đổi số mẫu (mẫu)', '', NULL, 5, 19);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (149, 2026, 'community', 'Diễn giả tại Đại hội Chi hội mẫu (mẫu)', '', NULL, 6, 21);
INSERT INTO public.directory_milestone (id, year, kind, title, source_url, company_id, event_id, person_id) VALUES (150, 2026, 'award', 'Nhận giải tại Đại hội Chi hội mẫu (mẫu)', '', NULL, 6, 23);


--
-- Data for Name: directory_eventparticipant; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (1, 'speaker', '', 1, NULL, 1);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (2, 'sponsor', '', 1, NULL, 2);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (3, 'awardee', 'Giải Doanh nhân trẻ tiêu biểu (mẫu)', 1, NULL, 3);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (4, 'attendee', '', 1, NULL, 4);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (5, 'attendee', '', 1, NULL, 5);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (6, 'speaker', '', 2, NULL, 5);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (7, 'sponsor', '', 2, NULL, 6);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (8, 'awardee', 'Giải Doanh nhân trẻ tiêu biểu (mẫu)', 2, NULL, 7);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (9, 'attendee', '', 2, NULL, 8);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (10, 'attendee', '', 2, NULL, 9);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (11, 'speaker', '', 3, NULL, 9);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (12, 'sponsor', '', 3, NULL, 10);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (13, 'awardee', 'Giải Doanh nhân trẻ tiêu biểu (mẫu)', 3, NULL, 11);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (14, 'attendee', '', 3, NULL, 12);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (15, 'attendee', '', 3, NULL, 13);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (16, 'speaker', '', 4, 145, 13);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (17, 'sponsor', '', 4, NULL, 14);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (18, 'awardee', 'Giải Doanh nhân trẻ tiêu biểu (mẫu)', 4, 146, 15);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (19, 'attendee', '', 4, NULL, 16);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (20, 'attendee', '', 4, NULL, 17);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (21, 'speaker', '', 5, 147, 17);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (22, 'sponsor', '', 5, NULL, 18);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (23, 'awardee', 'Giải Doanh nhân trẻ tiêu biểu (mẫu)', 5, 148, 19);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (24, 'attendee', '', 5, NULL, 20);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (25, 'attendee', '', 5, NULL, 21);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (26, 'speaker', '', 6, 149, 21);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (27, 'sponsor', '', 6, NULL, 22);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (28, 'awardee', 'Giải Doanh nhân trẻ tiêu biểu (mẫu)', 6, 150, 23);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (29, 'attendee', '', 6, NULL, 24);
INSERT INTO public.directory_eventparticipant (id, role, note, event_id, milestone_id, person_id) VALUES (30, 'attendee', '', 6, NULL, 1);


--
-- Data for Name: directory_membership; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (1, 'Chủ tịch', true, 0, 2020, NULL, 'confirmed', '2026-10-20 00:00:00+00', 1, 1);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (2, 'Phó Chủ tịch', true, 1, 2021, NULL, 'confirmed', '2026-10-20 00:00:00+00', 1, 2);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (3, 'Tổng Thư ký', true, 2, 2022, NULL, 'confirmed', '2026-10-20 00:00:00+00', 1, 3);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (4, 'Ủy viên Ban chấp hành', true, 3, 2023, NULL, 'confirmed', '2026-10-20 00:00:00+00', 1, 4);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (5, 'Hội viên', false, 4, 2020, NULL, 'confirmed', '2026-10-20 00:00:00+00', 1, 5);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (6, 'Hội viên', false, 5, 2021, NULL, 'confirmed', '2026-10-20 00:00:00+00', 1, 6);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (7, 'Hội viên', false, 6, 2022, NULL, 'confirmed', '2026-10-20 00:00:00+00', 1, 11);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (8, 'Chủ tịch', true, 0, 2020, NULL, 'confirmed', '2026-10-20 00:00:00+00', 2, 7);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (9, 'Phó Chủ tịch', true, 1, 2021, NULL, 'confirmed', '2026-10-20 00:00:00+00', 2, 8);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (10, 'Tổng Thư ký', true, 2, 2022, NULL, 'confirmed', '2026-10-20 00:00:00+00', 2, 9);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (11, 'Ủy viên Ban chấp hành', true, 3, 2023, NULL, 'confirmed', '2026-10-20 00:00:00+00', 2, 10);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (12, 'Hội viên', false, 4, 2020, NULL, 'confirmed', '2026-10-20 00:00:00+00', 2, 11);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (13, 'Hội viên', false, 5, 2021, NULL, 'confirmed', '2026-10-20 00:00:00+00', 2, 12);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (14, 'Hội viên', false, 6, 2022, NULL, 'confirmed', '2026-10-20 00:00:00+00', 2, 2);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (15, 'Chủ tịch', true, 0, 2020, NULL, 'confirmed', '2026-10-20 00:00:00+00', 3, 13);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (16, 'Phó Chủ tịch', true, 1, 2021, NULL, 'confirmed', '2026-10-20 00:00:00+00', 3, 14);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (17, 'Tổng Thư ký', true, 2, 2022, NULL, 'confirmed', '2026-10-20 00:00:00+00', 3, 15);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (18, 'Ủy viên Ban chấp hành', true, 3, 2023, NULL, 'confirmed', '2026-10-20 00:00:00+00', 3, 16);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (19, 'Hội viên', false, 4, 2020, NULL, 'confirmed', '2026-10-20 00:00:00+00', 3, 17);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (20, 'Hội viên', false, 5, 2021, NULL, 'confirmed', '2026-10-20 00:00:00+00', 3, 18);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (21, 'Hội viên', false, 6, 2022, NULL, 'confirmed', '2026-10-20 00:00:00+00', 3, 3);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (22, 'Hội viên', false, 7, 2023, NULL, 'confirmed', '2026-10-20 00:00:00+00', 3, 8);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (23, 'Chủ tịch', true, 0, 2020, NULL, 'confirmed', '2026-10-20 00:00:00+00', 4, 19);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (24, 'Phó Chủ tịch', true, 1, 2021, NULL, 'confirmed', '2026-10-20 00:00:00+00', 4, 20);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (25, 'Tổng Thư ký', true, 2, 2022, NULL, 'confirmed', '2026-10-20 00:00:00+00', 4, 21);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (26, 'Ủy viên Ban chấp hành', true, 3, 2023, NULL, 'confirmed', '2026-10-20 00:00:00+00', 4, 22);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (27, 'Hội viên', false, 4, 2020, NULL, 'confirmed', '2026-10-20 00:00:00+00', 4, 23);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (28, 'Hội viên', false, 5, 2021, NULL, 'confirmed', '2026-10-20 00:00:00+00', 4, 24);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (29, 'Hội viên', false, 6, 2022, NULL, 'confirmed', '2026-10-20 00:00:00+00', 4, 4);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (30, 'Hội viên', false, 7, 2023, NULL, 'confirmed', '2026-10-20 00:00:00+00', 4, 9);
INSERT INTO public.directory_membership (id, "position", is_leadership, sort_order, start_year, end_year, state, confirmed_at, association_id, person_id) VALUES (31, 'Hội viên', false, 8, 2020, NULL, 'pending', '2026-10-20 00:00:00+00', 4, 14);


--
-- Data for Name: directory_personcompany; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (1, 'founder_ceo', '', 2009, NULL, true, 1, 1);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (2, 'founder_ceo', '', 2016, NULL, true, 2, 2);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (3, 'cofounder', '', 2018, NULL, true, 3, 3);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (4, 'ceo', '', 2009, NULL, true, 4, 4);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (5, 'founder', '', 2011, NULL, true, 5, 5);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (6, 'founder_ceo', '', 2017, NULL, true, 6, 6);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (7, 'founder_ceo', '', 2016, NULL, true, 7, 7);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (8, 'cofounder', '', 2020, NULL, true, 8, 8);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (9, 'ceo', '', 2016, NULL, true, 9, 9);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (10, 'founder', '', 2019, NULL, true, 10, 10);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (11, 'founder_ceo', '', 2020, NULL, true, 11, 11);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (12, 'founder_ceo', '', 2020, NULL, true, 12, 12);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (13, 'cofounder', '', 2017, NULL, true, 13, 13);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (14, 'ceo', '', 2011, NULL, true, 14, 14);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (15, 'founder', '', 2017, NULL, true, 15, 15);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (16, 'founder_ceo', '', 2009, NULL, true, 16, 16);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (17, 'founder_ceo', '', 2021, NULL, true, 17, 17);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (18, 'cofounder', '', 2015, NULL, true, 18, 18);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (19, 'ceo', '', 2021, NULL, true, 19, 19);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (20, 'founder', '', 2018, NULL, true, 20, 20);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (21, 'founder_ceo', '', 2018, NULL, true, 21, 21);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (22, 'founder_ceo', '', 2011, NULL, true, 22, 22);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (23, 'cofounder', '', 2012, NULL, true, 23, 23);
INSERT INTO public.directory_personcompany (id, role, title, start_year, end_year, is_primary, company_id, person_id) VALUES (24, 'ceo', '', 2022, NULL, true, 24, 24);


--
-- Data for Name: directory_source; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (1, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 1);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (2, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 1, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (3, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 1);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (4, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 1, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (5, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 2);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (6, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 2, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (7, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 2);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (8, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 2, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (9, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 3);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (10, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 3, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (11, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 3);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (12, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 3, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (13, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 4);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (14, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 4, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (15, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 4);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (16, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 4, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (17, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 5);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (18, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 5, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (19, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 5);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (20, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 5, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (21, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 6);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (22, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 6, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (23, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 6);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (24, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 6, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (25, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 7);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (26, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 7, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (27, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 7);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (28, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 7, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (29, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 8);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (30, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 8, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (31, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 8);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (32, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 8, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (33, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 9);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (34, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 9, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (35, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 9);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (36, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 9, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (37, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 10);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (38, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 10, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (39, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 10);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (40, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 10, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (41, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 11);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (42, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 11, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (43, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 11);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (44, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 11, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (45, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 12);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (46, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 12, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (47, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 12);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (48, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 12, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (49, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 13);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (50, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 13, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (51, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 13);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (52, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 13, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (53, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 14);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (54, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 14, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (55, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 14);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (56, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 14, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (57, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 15);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (58, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 15, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (59, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 15);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (60, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 15, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (61, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 16);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (62, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 16, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (63, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 16);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (64, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 16, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (65, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 17);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (66, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 17, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (67, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 17);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (68, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 17, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (69, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 18);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (70, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 18, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (71, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 18);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (72, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 18, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (73, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 19);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (74, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 19, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (75, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 19);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (76, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 19, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (77, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 20);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (78, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 20, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (79, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 20);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (80, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 20, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (81, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 21);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (82, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 21, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (83, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 21);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (84, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 21, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (85, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 22);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (86, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 22, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (87, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 22);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (88, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 22, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (89, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 23);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (90, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 23, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (91, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 23);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (92, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 23, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (93, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', NULL, 24);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (94, 1, 'Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp', '', 'registry', 24, NULL);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (95, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', NULL, 24);
INSERT INTO public.directory_source (id, number, title, url, kind, company_id, person_id) VALUES (96, 2, 'Nguồn mẫu – Bài báo giới thiệu (hư cấu)', '', 'press', 24, NULL);


--
-- Data for Name: directory_video; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_video (id, url, platform, external_id, title, description, kind, thumbnail_url, duration_seconds, channel_name, published_on, status, availability, last_checked_at, is_featured, search_text, created_at) VALUES (1, 'https://example.com/video-mau-1', 'other', '', 'Phỏng vấn: hành trình khởi nghiệp phần mềm (mẫu)', '', 'interview', '', 300, 'Kênh mẫu (thử)', '2026-10-20', 'published', 'ok', NULL, true, 'phong van: hanh trinh khoi nghiep phan mem (mau) kenh mau (thu)', '2026-10-20 00:49:50.248239+00');
INSERT INTO public.directory_video (id, url, platform, external_id, title, description, kind, thumbnail_url, duration_seconds, channel_name, published_on, status, availability, last_checked_at, is_featured, search_text, created_at) VALUES (2, 'https://example.com/video-mau-2', 'other', '', 'Câu chuyện doanh nghiệp: chuỗi cà phê Lá Xanh (mẫu)', '', 'company', '', 395, 'Kênh mẫu (thử)', '2026-10-10', 'published', 'ok', NULL, false, 'cau chuyen doanh nghiep: chuoi ca phe la xanh (mau) kenh mau (thu)', '2026-10-20 00:49:50.250952+00');
INSERT INTO public.directory_video (id, url, platform, external_id, title, description, kind, thumbnail_url, duration_seconds, channel_name, published_on, status, availability, last_checked_at, is_featured, search_text, created_at) VALUES (3, 'https://example.com/video-mau-3', 'other', '', 'Bài nói tại Diễn đàn Doanh nhân trẻ (mẫu)', '', 'talk', '', 490, 'Kênh mẫu (thử)', '2026-09-30', 'published', 'ok', NULL, false, 'bai noi tai dien dan doanh nhan tre (mau) kenh mau (thu)', '2026-10-20 00:49:50.253162+00');
INSERT INTO public.directory_video (id, url, platform, external_id, title, description, kind, thumbnail_url, duration_seconds, channel_name, published_on, status, availability, last_checked_at, is_featured, search_text, created_at) VALUES (4, 'https://example.com/video-mau-4', 'other', '', 'Ghi hình Lễ vinh danh Doanh nhân trẻ (mẫu)', '', 'event', '', 585, 'Kênh mẫu (thử)', '2026-09-20', 'published', 'ok', NULL, false, 'ghi hinh le vinh danh doanh nhan tre (mau) kenh mau (thu)', '2026-10-20 00:49:50.255245+00');
INSERT INTO public.directory_video (id, url, platform, external_id, title, description, kind, thumbnail_url, duration_seconds, channel_name, published_on, status, availability, last_checked_at, is_featured, search_text, created_at) VALUES (5, 'https://example.com/video-mau-5', 'other', '', 'Phỏng vấn: xây dựng nhà máy vật liệu (mẫu)', '', 'interview', '', 680, 'Kênh mẫu (thử)', '2026-09-10', 'published', 'ok', NULL, false, 'phong van: xay dung nha may vat lieu (mau) kenh mau (thu)', '2026-10-20 00:49:50.257425+00');
INSERT INTO public.directory_video (id, url, platform, external_id, title, description, kind, thumbnail_url, duration_seconds, channel_name, published_on, status, availability, last_checked_at, is_featured, search_text, created_at) VALUES (6, 'https://example.com/video-mau-6', 'other', '', 'Câu chuyện doanh nghiệp: logistics Bảo Long (mẫu)', '', 'company', '', 775, 'Kênh mẫu (thử)', '2026-08-31', 'published', 'ok', NULL, false, 'cau chuyen doanh nghiep: logistics bao long (mau) kenh mau (thu)', '2026-10-20 00:49:50.258737+00');


--
-- Data for Name: directory_video_associations; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- Data for Name: directory_video_companies; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_video_companies (id, video_id, company_id) VALUES (1, 2, 2);
INSERT INTO public.directory_video_companies (id, video_id, company_id) VALUES (2, 6, 3);


--
-- Data for Name: directory_video_events; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_video_events (id, video_id, event_id) VALUES (1, 4, 1);


--
-- Data for Name: directory_video_persons; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_video_persons (id, video_id, person_id) VALUES (1, 1, 1);
INSERT INTO public.directory_video_persons (id, video_id, person_id) VALUES (2, 3, 3);
INSERT INTO public.directory_video_persons (id, video_id, person_id) VALUES (3, 5, 4);


--
-- Data for Name: moderation_auditlog; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.moderation_auditlog (id, action, target_type, target_id, target_label, detail, ip, created_at, actor_id) VALUES (1, 'revision.submit', 'Revision', '49', 'Phạm Gia Huy (hồ sơ thử)', '{}', NULL, '2026-10-20 00:49:50.138865+00', 7);
INSERT INTO public.moderation_auditlog (id, action, target_type, target_id, target_label, detail, ip, created_at, actor_id) VALUES (2, 'revision.submit', 'Revision', '50', 'Ví Mẫu (thử)', '{}', NULL, '2026-10-20 00:49:50.143195+00', 5);
INSERT INTO public.moderation_auditlog (id, action, target_type, target_id, target_label, detail, ip, created_at, actor_id) VALUES (3, 'revision.submit', 'Revision', '51', 'Nguyễn Minh An (hồ sơ mẫu)', '{}', NULL, '2026-10-20 00:49:50.168943+00', 4);
INSERT INTO public.moderation_auditlog (id, action, target_type, target_id, target_label, detail, ip, created_at, actor_id) VALUES (4, 'revision.submit', 'Revision', '52', 'Bảo Long (mẫu)', '{}', NULL, '2026-10-20 00:49:50.200162+00', 7);
INSERT INTO public.moderation_auditlog (id, action, target_type, target_id, target_label, detail, ip, created_at, actor_id) VALUES (5, 'revision.needs_info', 'Revision', '52', 'Bảo Long (mẫu)', '{"note": "Vui lòng thêm nguồn xác nhận quy mô nhân sự (dữ liệu thử)."}', NULL, '2026-10-20 00:49:50.203594+00', 3);
INSERT INTO public.moderation_auditlog (id, action, target_type, target_id, target_label, detail, ip, created_at, actor_id) VALUES (6, 'revision.save_draft', 'Revision', '53', 'Võ Thu Vy (hồ sơ mẫu)', '{}', NULL, '2026-10-20 00:49:50.235763+00', 7);
INSERT INTO public.moderation_auditlog (id, action, target_type, target_id, target_label, detail, ip, created_at, actor_id) VALUES (7, 'test_data.create', '', '', 'Tạo bộ dữ liệu thử nghiệm', '{}', NULL, '2026-10-20 00:49:50.259948+00', 1);


--
-- Data for Name: moderation_profileclaim; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.moderation_profileclaim (id, evidence, note, state, reviewed_at, review_note, created_at, person_id, reviewed_by_id, user_id) VALUES (1, 'claims/2026/giay-to-thu.pdf', 'Tôi là chính chủ (dữ liệu thử).', 'pending', NULL, '', '2026-10-20 00:49:50.237287+00', 2, NULL, 6);


--
-- Data for Name: moderation_revision; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (1, 'person', 'create', 'Nguyễn Minh An (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.973513+00', '2026-10-20 00:49:40.973523+00', NULL, NULL, 1, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (2, 'person', 'create', 'Trần Ngọc Hà (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.975497+00', '2026-10-20 00:49:40.975506+00', NULL, NULL, 2, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (3, 'person', 'create', 'Lê Thảo Bảo (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.976611+00', '2026-10-20 00:49:40.976619+00', NULL, NULL, 3, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (4, 'person', 'create', 'Phạm Thanh Linh (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.97759+00', '2026-10-20 00:49:40.977597+00', NULL, NULL, 4, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (5, 'person', 'create', 'Hoàng Khánh Nam (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.97838+00', '2026-10-20 00:49:40.978387+00', NULL, NULL, 5, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (6, 'person', 'create', 'Võ Thu Vy (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.979286+00', '2026-10-20 00:49:40.979292+00', NULL, NULL, 6, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (7, 'person', 'create', 'Đặng Đức Phúc (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.979945+00', '2026-10-20 00:49:40.979951+00', NULL, NULL, 7, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (8, 'person', 'create', 'Bùi Anh Trang (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.980647+00', '2026-10-20 00:49:40.980653+00', NULL, NULL, 8, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (9, 'person', 'create', 'Đỗ Hải Khoa (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.981311+00', '2026-10-20 00:49:40.981316+00', NULL, NULL, 9, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (10, 'person', 'create', 'Hồ Bảo Mai (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.982343+00', '2026-10-20 00:49:40.982348+00', NULL, NULL, 10, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (11, 'person', 'create', 'Ngô Quốc Tuấn (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.984489+00', '2026-10-20 00:49:40.984495+00', NULL, NULL, 11, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (12, 'person', 'create', 'Dương Gia Châu (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.985504+00', '2026-10-20 00:49:40.985511+00', NULL, NULL, 12, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (13, 'person', 'create', 'Nguyễn Minh Long (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.986402+00', '2026-10-20 00:49:40.986408+00', NULL, NULL, 13, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (14, 'person', 'create', 'Trần Ngọc Nhi (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.987293+00', '2026-10-20 00:49:40.987299+00', NULL, NULL, 14, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (15, 'person', 'create', 'Lê Thảo Huy (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.98823+00', '2026-10-20 00:49:40.988236+00', NULL, NULL, 15, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (16, 'person', 'create', 'Phạm Thanh Ngân (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.988971+00', '2026-10-20 00:49:40.988977+00', NULL, NULL, 16, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (17, 'person', 'create', 'Hoàng Khánh Sơn (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.989783+00', '2026-10-20 00:49:40.989789+00', NULL, NULL, 17, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (18, 'person', 'create', 'Võ Thu Thư (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.990648+00', '2026-10-20 00:49:40.990655+00', NULL, NULL, 18, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (19, 'person', 'create', 'Đặng Đức Đạt (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.991587+00', '2026-10-20 00:49:40.991594+00', NULL, NULL, 19, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (20, 'person', 'create', 'Bùi Anh Yến (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.992661+00', '2026-10-20 00:49:40.992668+00', NULL, NULL, 20, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (21, 'person', 'create', 'Đỗ Hải Tín (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.993536+00', '2026-10-20 00:49:40.993542+00', NULL, NULL, 21, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (22, 'person', 'create', 'Hồ Bảo My (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.994312+00', '2026-10-20 00:49:40.994318+00', NULL, NULL, 22, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (23, 'person', 'create', 'Ngô Quốc Quân (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.995079+00', '2026-10-20 00:49:40.995084+00', NULL, NULL, 23, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (24, 'person', 'create', 'Dương Gia Hương (hồ sơ mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.995835+00', '2026-10-20 00:49:40.995841+00', NULL, NULL, 24, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (25, 'company', 'create', 'An Phát (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.996626+00', '2026-10-20 00:49:40.996632+00', NULL, 1, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (26, 'company', 'create', 'Bình Minh (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.997346+00', '2026-10-20 00:49:40.997351+00', NULL, 15, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (27, 'company', 'create', 'Bảo Long (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.998037+00', '2026-10-20 00:49:40.998042+00', NULL, 3, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (28, 'company', 'create', 'Cửu Long (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.998841+00', '2026-10-20 00:49:40.998847+00', NULL, 18, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (29, 'company', 'create', 'Gia Hưng (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:40.999571+00', '2026-10-20 00:49:40.999577+00', NULL, 21, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (30, 'company', 'create', 'Hòa Bình (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.000279+00', '2026-10-20 00:49:41.000284+00', NULL, 10, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (31, 'company', 'create', 'Hưng Thịnh (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.000981+00', '2026-10-20 00:49:41.000987+00', NULL, 5, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (32, 'company', 'create', 'Hồng Hà (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.001624+00', '2026-10-20 00:49:41.00163+00', NULL, 17, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (33, 'company', 'create', 'Kim Ngân (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.002258+00', '2026-10-20 00:49:41.002264+00', NULL, 14, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (34, 'company', 'create', 'Lá Xanh (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.003047+00', '2026-10-20 00:49:41.003053+00', NULL, 2, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (35, 'company', 'create', 'Minh Khang (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.003803+00', '2026-10-20 00:49:41.003809+00', NULL, 20, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (36, 'company', 'create', 'Mộc Lan (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.004587+00', '2026-10-20 00:49:41.004592+00', NULL, 6, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (37, 'company', 'create', 'Nhật Quang (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.005247+00', '2026-10-20 00:49:41.005253+00', NULL, 19, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (38, 'company', 'create', 'Phú Quý (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.005922+00', '2026-10-20 00:49:41.005928+00', NULL, 22, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (39, 'company', 'create', 'Phương Nam (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.006659+00', '2026-10-20 00:49:41.006665+00', NULL, 8, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (40, 'company', 'create', 'Sao Mai (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.007401+00', '2026-10-20 00:49:41.007406+00', NULL, 4, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (41, 'company', 'create', 'Thiên Phú (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.008101+00', '2026-10-20 00:49:41.008144+00', NULL, 16, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (42, 'company', 'create', 'Thành Đạt (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.008848+00', '2026-10-20 00:49:41.008853+00', NULL, 23, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (43, 'company', 'create', 'Trường Sơn (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.009611+00', '2026-10-20 00:49:41.009617+00', NULL, 13, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (44, 'company', 'create', 'Tân Tiến (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.010265+00', '2026-10-20 00:49:41.010271+00', NULL, 11, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (45, 'company', 'create', 'Việt Tín (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.010961+00', '2026-10-20 00:49:41.010967+00', NULL, 7, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (46, 'company', 'create', 'Vạn Xuân (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.011891+00', '2026-10-20 00:49:41.011896+00', NULL, 24, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (47, 'company', 'create', 'Ánh Dương (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.012604+00', '2026-10-20 00:49:41.01261+00', NULL, 12, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (48, 'company', 'create', 'Đại Dương (mẫu)', '{}', '{}', '[]', 'Dữ liệu mẫu', 'approved', 1, 'editor', '2026-10-20 00:00:00+00', '', '2026-10-20 00:49:41.013304+00', '2026-10-20 00:49:41.013311+00', NULL, 9, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (49, 'person', 'create', 'Phạm Gia Huy (hồ sơ thử)', '{"videos": [], "sources": [{"url": "https://example.com/bai-bao", "kind": "press", "title": "Nguồn thử nghiệm"}], "website": "", "headline": "Nhà sáng lập Ví Mẫu (thử)", "hometown": 2, "portrait": "", "sections": {"journey": "Đoạn hành trình thử nghiệm, chưa đủ 500 từ để biên tập viên thấy cảnh báo.", "summary": "Phạm Gia Huy là nhân vật thử nghiệm, sáng lập một ví điện tử mẫu.[^1]"}, "companies": [{"role": "founder_ceo", "title": "", "end_year": null, "company_id": null, "is_primary": true, "start_year": 2020, "company_name": "Ví Mẫu (thử)"}], "full_name": "Phạm Gia Huy (hồ sơ thử)", "birth_year": 1993, "milestones": [{"kind": "founding", "year": 2020, "title": "Thành lập Ví Mẫu (thử)", "source_url": ""}], "show_email": false, "memberships": [], "email_public": "", "show_hometown": true, "show_birth_year": true, "current_province": 2}', '{}', '[{"text": "Doanh nghiệp chưa có trong hệ thống, sẽ được tạo ở trạng thái bản nháp: Ví Mẫu (thử)", "level": "info"}, {"text": "Bài viết “Hành trình khởi nghiệp” mới có 16 từ (khuyến nghị từ 500 từ).", "level": "warn"}, {"text": "Nên có ít nhất 3 dấu mốc để dựng dòng thời gian.", "level": "warn"}, {"text": "Mới có 1 nguồn tham khảo — nên có từ 2 nguồn.", "level": "info"}]', 'Hồ sơ thử: kiểm tra cảnh báo thiếu bài viết, thiếu dấu mốc.', 'pending', NULL, 'member', NULL, '', '2026-10-20 00:49:50.137681+00', '2026-10-20 00:49:50.137694+00', 7, NULL, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (50, 'company', 'create', 'Ví Mẫu (thử)', '{"logo": "", "cover": "", "videos": [], "address": "Số 1 đường Thử Nghiệm", "leaders": [{"role": "founder_ceo", "title": "", "person_id": null, "is_primary": true, "start_year": 2020, "person_name": "Phạm Gia Huy (hồ sơ thử)"}], "sectors": [4], "sources": [], "website": "https://example.com", "products": [{"name": "Ứng dụng ví (thử)", "description": "Mô tả thử nghiệm."}], "province": 2, "sections": {"overview": "Doanh nghiệp thử nghiệm trong lĩnh vực fintech."}, "tax_code": "", "size_band": "10_50", "brand_name": "Ví Mẫu (thử)", "legal_name": "Công ty Cổ phần Ví Mẫu (thử)", "milestones": [], "founded_year": 2020, "primary_sector": 4}', '{}', '[{"text": "Chưa có mã số thuế — khó xác minh doanh nghiệp.", "level": "warn"}, {"text": "Người điều hành chưa có hồ sơ, sẽ được tạo ở trạng thái bản nháp: Phạm Gia Huy (hồ sơ thử)", "level": "info"}, {"text": "Bài viết “Lịch sử hình thành & phát triển” mới có 0 từ (khuyến nghị từ 400 từ).", "level": "warn"}, {"text": "Nên có ít nhất 3 dấu mốc để dựng dòng thời gian.", "level": "warn"}, {"text": "Chưa có nguồn tham khảo nào.", "level": "warn"}]', 'Doanh nghiệp thử: chưa có mã số thuế → có cảnh báo.', 'pending', NULL, 'member', NULL, '', '2026-10-20 00:49:50.141838+00', '2026-10-20 00:49:50.141849+00', 5, NULL, NULL, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (51, 'person', 'update', 'Nguyễn Minh An (hồ sơ mẫu)', '{"status": "published", "videos": [], "sources": [{"url": "", "kind": "registry", "title": "Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp"}, {"url": "", "kind": "press", "title": "Nguồn mẫu – Bài báo giới thiệu (hư cấu)"}], "website": "", "headline": "Nhà sáng lập & CEO An Phát (mẫu), Chủ tịch Hội mẫu", "hometown": 2, "portrait": "", "sections": {"journey": "## Ý tưởng ban đầu\nĐoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]\n\n## Những năm đầu và khó khăn\nSản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.\n\n> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”\n\n## Bước ngoặt và phát triển\nMở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]\n\n## Hiện nay\nVai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.", "summary": "Nguyễn Minh An là nhân vật hư cấu, nhà sáng lập & ceo an phát (mẫu), hoạt động trong lĩnh vực phần mềm doanh nghiệp tại TP. Hồ Chí Minh.[^1] Cập nhật thử nghiệm năm nay.", "biography": "Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.", "philosophy": "> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”", "achievements": "- 2014 — Giải thưởng doanh nhân trẻ (mẫu).[^2]"}, "companies": [{"role": "founder_ceo", "title": "", "end_year": null, "company_id": 1, "is_primary": true, "start_year": 2009, "company_name": "An Phát (mẫu)"}], "full_name": "Nguyễn Minh An (hồ sơ mẫu)", "birth_year": 1987, "milestones": [{"kind": "founding", "year": 2009, "title": "Thành lập An Phát (mẫu)", "source_url": ""}, {"kind": "product", "year": 2012, "title": "Ra mắt sản phẩm chủ lực (mẫu)", "source_url": ""}, {"kind": "award", "year": 2015, "title": "Nhận giải thưởng doanh nhân trẻ (mẫu)", "source_url": ""}, {"kind": "position", "year": 2026, "title": "Được bầu Chủ tịch Hội (thử)", "source_url": "https://example.com/quyet-dinh"}], "show_email": false, "is_featured": true, "memberships": [{"position": "Chủ tịch", "start_year": 2020, "association_id": 1}], "email_public": "", "verification": "verified", "show_hometown": true, "show_birth_year": true, "current_province": 2, "verification_note": ""}', '{"status": "published", "videos": [], "sources": [{"url": "", "kind": "registry", "title": "Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp"}, {"url": "", "kind": "press", "title": "Nguồn mẫu – Bài báo giới thiệu (hư cấu)"}], "website": "", "headline": "Nhà sáng lập & CEO An Phát (mẫu)", "hometown": 2, "portrait": "", "sections": {"journey": "## Ý tưởng ban đầu\nĐoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]\n\n## Những năm đầu và khó khăn\nSản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.\n\n> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”\n\n## Bước ngoặt và phát triển\nMở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]\n\n## Hiện nay\nVai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.", "summary": "Nguyễn Minh An là nhân vật hư cấu, nhà sáng lập & ceo an phát (mẫu), hoạt động trong lĩnh vực phần mềm doanh nghiệp tại TP. Hồ Chí Minh.[^1]", "biography": "Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh.", "philosophy": "> “Câu nói tiêu biểu thể hiện triết lý kinh doanh (mẫu).”", "achievements": "- 2014 — Giải thưởng doanh nhân trẻ (mẫu).[^2]"}, "companies": [{"role": "founder_ceo", "title": "", "end_year": null, "company_id": 1, "is_primary": true, "start_year": 2009, "company_name": "An Phát (mẫu)"}], "full_name": "Nguyễn Minh An (hồ sơ mẫu)", "birth_year": 1987, "milestones": [{"kind": "founding", "year": 2009, "title": "Thành lập An Phát (mẫu)", "source_url": ""}, {"kind": "product", "year": 2012, "title": "Ra mắt sản phẩm chủ lực (mẫu)", "source_url": ""}, {"kind": "award", "year": 2015, "title": "Nhận giải thưởng doanh nhân trẻ (mẫu)", "source_url": ""}], "show_email": false, "is_featured": true, "memberships": [{"position": "Chủ tịch", "start_year": 2020, "association_id": 1}], "email_public": "", "verification": "verified", "show_hometown": true, "show_birth_year": true, "current_province": 2, "verification_note": ""}', '[{"text": "Bài viết “Hành trình khởi nghiệp” mới có 142 từ (khuyến nghị từ 500 từ).", "level": "warn"}]', 'Chính chủ cập nhật chức danh và dấu mốc mới.', 'pending', NULL, 'owner', NULL, '', '2026-10-20 00:49:50.16715+00', '2026-10-20 00:49:50.167164+00', 4, NULL, 1, NULL);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (52, 'company', 'update', 'Bảo Long (mẫu)', '{"logo": "", "cover": "", "status": "published", "videos": [], "address": "Số 3 đường Mẫu, Đà Nẵng", "leaders": [{"role": "cofounder", "title": "", "person_id": 3, "is_primary": true, "start_year": 2018, "person_name": "Lê Thảo Bảo (hồ sơ mẫu)"}], "sectors": [1, 4], "sources": [{"url": "", "kind": "registry", "title": "Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp"}, {"url": "", "kind": "press", "title": "Nguồn mẫu – Bài báo giới thiệu (hư cấu)"}], "website": "", "products": [{"name": "Sản phẩm mẫu 3", "description": "Mô tả ngắn 1–2 câu."}], "province": 4, "sections": {"history": "Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.", "overview": "Bảo Long (mẫu) là doanh nghiệp hư cấu trong lĩnh vực fintech, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]", "products": "Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính."}, "tax_code": "", "size_band": "50_200", "brand_name": "Bảo Long (mẫu)", "legal_name": "Công ty TNHH Bảo Long (mẫu)", "milestones": [{"kind": "founding", "year": 2018, "title": "Thành lập Bảo Long (mẫu)", "source_url": ""}, {"kind": "product", "year": 2021, "title": "Ra mắt sản phẩm chủ lực (mẫu)", "source_url": ""}, {"kind": "award", "year": 2024, "title": "Nhận giải thưởng doanh nhân trẻ (mẫu)", "source_url": ""}], "is_featured": true, "founded_year": 2018, "verification": "none", "primary_sector": 4, "verification_note": ""}', '{"logo": "", "cover": "", "status": "published", "videos": [], "address": "Số 3 đường Mẫu, Đà Nẵng", "leaders": [{"role": "cofounder", "title": "", "person_id": 3, "is_primary": true, "start_year": 2018, "person_name": "Lê Thảo Bảo (hồ sơ mẫu)"}], "sectors": [1, 4], "sources": [{"url": "", "kind": "registry", "title": "Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp"}, {"url": "", "kind": "press", "title": "Nguồn mẫu – Bài báo giới thiệu (hư cấu)"}], "website": "", "products": [{"name": "Sản phẩm mẫu 3", "description": "Mô tả ngắn 1–2 câu."}], "province": 4, "sections": {"history": "Đoạn mẫu: hoàn cảnh ra đời, các giai đoạn phát triển, bước ngoặt, mở rộng.", "overview": "Bảo Long (mẫu) là doanh nghiệp hư cấu trong lĩnh vực fintech, minh họa trang doanh nghiệp trên doanhnhan.wiki.[^1]", "products": "Đoạn mẫu mô tả các dòng sản phẩm, dịch vụ chính."}, "tax_code": "", "size_band": "10_50", "brand_name": "Bảo Long (mẫu)", "legal_name": "Công ty TNHH Bảo Long (mẫu)", "milestones": [{"kind": "founding", "year": 2018, "title": "Thành lập Bảo Long (mẫu)", "source_url": ""}, {"kind": "product", "year": 2021, "title": "Ra mắt sản phẩm chủ lực (mẫu)", "source_url": ""}, {"kind": "award", "year": 2024, "title": "Nhận giải thưởng doanh nhân trẻ (mẫu)", "source_url": ""}], "is_featured": true, "founded_year": 2018, "verification": "none", "primary_sector": 4, "verification_note": ""}', '[{"text": "Chưa có mã số thuế — khó xác minh doanh nghiệp.", "level": "warn"}, {"text": "Bài viết “Lịch sử hình thành & phát triển” mới có 15 từ (khuyến nghị từ 400 từ).", "level": "warn"}]', 'Đề nghị đổi quy mô nhân sự.', 'needs_info', NULL, 'member', '2026-10-20 00:49:50.200899+00', 'Vui lòng thêm nguồn xác nhận quy mô nhân sự (dữ liệu thử).', '2026-10-20 00:49:50.198764+00', '2026-10-20 00:49:50.201114+00', 7, 3, NULL, 3);
INSERT INTO public.moderation_revision (id, entity_type, kind, title, data, previous_data, checks, note, state, revision_no, author_role, reviewed_at, review_note, created_at, updated_at, author_id, company_id, person_id, reviewer_id) VALUES (53, 'person', 'update', 'Võ Thu Vy (hồ sơ mẫu)', '{"status": "published", "videos": [], "sources": [{"url": "", "kind": "registry", "title": "Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp"}, {"url": "", "kind": "press", "title": "Nguồn mẫu – Bài báo giới thiệu (hư cấu)"}], "website": "https://example.com/linkedin", "headline": "Nhà sáng lập & CEO Mộc Lan (mẫu)", "hometown": 6, "portrait": "", "sections": {"journey": "## Ý tưởng ban đầu\nĐoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]\n\n## Những năm đầu và khó khăn\nSản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.\n\n> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”\n\n## Bước ngoặt và phát triển\nMở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]\n\n## Hiện nay\nVai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.", "summary": "Võ Thu Vy là nhân vật hư cấu, nhà sáng lập & ceo mộc lan (mẫu), hoạt động trong lĩnh vực marketing số tại Đồng Nai.[^1]", "biography": "Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh."}, "companies": [{"role": "founder_ceo", "title": "", "end_year": null, "company_id": 6, "is_primary": true, "start_year": 2017, "company_name": "Mộc Lan (mẫu)"}], "full_name": "Võ Thu Vy (hồ sơ mẫu)", "birth_year": 1991, "milestones": [{"kind": "founding", "year": 2017, "title": "Thành lập Mộc Lan (mẫu)", "source_url": ""}, {"kind": "product", "year": 2020, "title": "Ra mắt sản phẩm chủ lực (mẫu)", "source_url": ""}, {"kind": "award", "year": 2023, "title": "Nhận giải thưởng doanh nhân trẻ (mẫu)", "source_url": ""}], "show_email": false, "is_featured": true, "memberships": [{"position": "Hội viên", "start_year": 2021, "association_id": 1}], "email_public": "", "verification": "basic", "show_hometown": true, "show_birth_year": true, "current_province": 13, "verification_note": ""}', '{"status": "published", "videos": [], "sources": [{"url": "", "kind": "registry", "title": "Nguồn mẫu – Cổng thông tin đăng ký doanh nghiệp"}, {"url": "", "kind": "press", "title": "Nguồn mẫu – Bài báo giới thiệu (hư cấu)"}], "website": "", "headline": "Nhà sáng lập & CEO Mộc Lan (mẫu)", "hometown": 6, "portrait": "", "sections": {"journey": "## Ý tưởng ban đầu\nĐoạn văn mẫu minh họa phần hành trình khởi nghiệp. Nhân vật và doanh nghiệp trong hồ sơ này là hư cấu. Phần thật sẽ kể bối cảnh ra đời ý tưởng, nhu cầu thị trường, nguồn lực ban đầu như vốn, cộng sự, nơi làm việc.[^1]\n\n## Những năm đầu và khó khăn\nSản phẩm đầu tiên, khách hàng đầu tiên, thử thách lớn và quyết định quan trọng để vượt qua — mỗi sự kiện nên kèm năm và nguồn kiểm chứng.\n\n> “Một câu trích dẫn trực tiếp của doanh nhân về giai đoạn này (mẫu).”\n\n## Bước ngoặt và phát triển\nMở rộng thị trường, ra mắt dòng sản phẩm mới, hợp tác chiến lược.[^2]\n\n## Hiện nay\nVai trò hiện tại, quy mô doanh nghiệp đã công bố, định hướng sắp tới.", "summary": "Võ Thu Vy là nhân vật hư cấu, nhà sáng lập & ceo mộc lan (mẫu), hoạt động trong lĩnh vực marketing số tại Đồng Nai.[^1]", "biography": "Đoạn mẫu cho phần tiểu sử & học vấn: xuất thân, quá trình học tập, bằng cấp, những trải nghiệm ảnh hưởng tới lựa chọn kinh doanh."}, "companies": [{"role": "founder_ceo", "title": "", "end_year": null, "company_id": 6, "is_primary": true, "start_year": 2017, "company_name": "Mộc Lan (mẫu)"}], "full_name": "Võ Thu Vy (hồ sơ mẫu)", "birth_year": 1991, "milestones": [{"kind": "founding", "year": 2017, "title": "Thành lập Mộc Lan (mẫu)", "source_url": ""}, {"kind": "product", "year": 2020, "title": "Ra mắt sản phẩm chủ lực (mẫu)", "source_url": ""}, {"kind": "award", "year": 2023, "title": "Nhận giải thưởng doanh nhân trẻ (mẫu)", "source_url": ""}], "show_email": false, "is_featured": true, "memberships": [{"position": "Hội viên", "start_year": 2021, "association_id": 1}], "email_public": "", "verification": "basic", "show_hometown": true, "show_birth_year": true, "current_province": 13, "verification_note": ""}', '[{"text": "Bài viết “Hành trình khởi nghiệp” mới có 142 từ (khuyến nghị từ 500 từ).", "level": "warn"}]', 'Bản nháp chưa gửi.', 'draft', NULL, 'member', NULL, '', '2026-10-20 00:49:50.23397+00', '2026-10-20 00:49:50.234017+00', 7, NULL, 6, NULL);


--
-- Data for Name: sitecontent_contactmessage; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.sitecontent_contactmessage (id, topic, full_name, organization, email, phone, message, handled, staff_note, created_at) VALUES (1, 'partner', 'Đại diện Hội thử', 'Hội thử', 'doitac@example.com', '', 'Đăng ký làm hiệp hội đối tác (thử).', false, '', '2026-10-20 00:49:50.240802+00');
INSERT INTO public.sitecontent_contactmessage (id, topic, full_name, organization, email, phone, message, handled, staff_note, created_at) VALUES (2, 'correction', 'Người đọc thử', '', 'docgia@example.com', '', 'Năm thành lập trên một hồ sơ mẫu chưa đúng (thử).', false, '', '2026-10-20 00:49:50.24152+00');


--
-- Data for Name: sitecontent_datarequest; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.sitecontent_datarequest (id, full_name, email, profile_url, kind, detail, state, resolved_at, staff_note, created_at, handled_by_id) VALUES (1, 'Người yêu cầu thử', 'dulieu@example.com', '/doanh-nhan/', 'correct', 'Đề nghị sửa quê quán (dữ liệu thử).', 'open', NULL, '', '2026-10-20 00:49:50.24207+00', NULL);


--
-- Data for Name: sitecontent_donationaccount; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.sitecontent_donationaccount (id, bank_name, account_number, account_holder, qr_image, sort_order, state, approved_at, created_at, approved_by_id, created_by_id, replaces_id) VALUES (1, 'Ngân hàng Mẫu (dữ liệu thử)', '0000000001', 'CONG TY MAU - DU LIEU THU', '', 0, 'active', '2026-10-20 00:49:41.025181+00', '2026-10-20 00:49:50.24314+00', 2, 1, NULL);
INSERT INTO public.sitecontent_donationaccount (id, bank_name, account_number, account_holder, qr_image, sort_order, state, approved_at, created_at, approved_by_id, created_by_id, replaces_id) VALUES (2, 'Ngân hàng Mẫu 2 (dữ liệu thử)', '0000000002', 'CONG TY MAU - DU LIEU THU', '', 0, 'pending', NULL, '2026-10-20 00:49:50.244186+00', NULL, 1, NULL);


--
-- Data for Name: sitecontent_interviewrequest; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.sitecontent_interviewrequest (id, full_name, title, company, phone, email, kind, story, format, preferred_time, reference_url, state, staff_note, consent_at, created_at, assignee_id, video_id) VALUES (1, 'Người Liên Hệ 1 (thử)', 'Nhà sáng lập', 'Công ty Liên Hệ 1 (thử)', '0900000000', 'lienhe1@example.com', 'interview', 'Câu chuyện thử nghiệm muốn chia sẻ.', 'onsite', 'Sáng thứ 3–5', '', 'new', '', '2026-10-20 00:49:50.238389+00', '2026-10-20 00:49:50.238607+00', NULL, NULL);
INSERT INTO public.sitecontent_interviewrequest (id, full_name, title, company, phone, email, kind, story, format, preferred_time, reference_url, state, staff_note, consent_at, created_at, assignee_id, video_id) VALUES (2, 'Người Liên Hệ 2 (thử)', 'Nhà sáng lập', 'Công ty Liên Hệ 2 (thử)', '0900000000', 'lienhe2@example.com', 'company', 'Câu chuyện thử nghiệm muốn chia sẻ.', 'studio', 'Sáng thứ 3–5', '', 'scheduled', '', '2026-10-20 00:49:50.239526+00', '2026-10-20 00:49:50.239633+00', 3, NULL);
INSERT INTO public.sitecontent_interviewrequest (id, full_name, title, company, phone, email, kind, story, format, preferred_time, reference_url, state, staff_note, consent_at, created_at, assignee_id, video_id) VALUES (3, 'Người Liên Hệ 3 (thử)', 'Nhà sáng lập', 'Công ty Liên Hệ 3 (thử)', '0900000000', 'lienhe3@example.com', 'event', 'Câu chuyện thử nghiệm muốn chia sẻ.', 'event', 'Sáng thứ 3–5', '', 'published', '', '2026-10-20 00:49:50.240121+00', '2026-10-20 00:49:50.240219+00', 3, NULL);


--
-- Data for Name: sitecontent_policyacceptance; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (1, '2026-10-20 00:49:41.972933+00', '127.0.0.1', '', 'signup', 1, 1);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (2, '2026-10-20 00:49:41.974758+00', '127.0.0.1', '', 'signup', 1, 2);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (3, '2026-10-20 00:49:42.796685+00', '127.0.0.1', '', 'signup', 2, 1);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (4, '2026-10-20 00:49:42.797406+00', '127.0.0.1', '', 'signup', 2, 2);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (5, '2026-10-20 00:49:43.544034+00', '127.0.0.1', '', 'signup', 3, 1);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (6, '2026-10-20 00:49:43.544847+00', '127.0.0.1', '', 'signup', 3, 2);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (7, '2026-10-20 00:49:44.558263+00', '127.0.0.1', '', 'signup', 4, 1);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (8, '2026-10-20 00:49:44.559169+00', '127.0.0.1', '', 'signup', 4, 2);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (9, '2026-10-20 00:49:45.449172+00', '127.0.0.1', '', 'signup', 5, 1);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (10, '2026-10-20 00:49:45.450191+00', '127.0.0.1', '', 'signup', 5, 2);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (11, '2026-10-20 00:49:46.112199+00', '127.0.0.1', '', 'signup', 6, 1);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (12, '2026-10-20 00:49:46.112901+00', '127.0.0.1', '', 'signup', 6, 2);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (13, '2026-10-20 00:49:46.955667+00', '127.0.0.1', '', 'signup', 7, 1);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (14, '2026-10-20 00:49:46.956393+00', '127.0.0.1', '', 'signup', 7, 2);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (15, '2026-10-20 00:49:47.594175+00', '127.0.0.1', '', 'signup', 8, 1);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (16, '2026-10-20 00:49:47.594865+00', '127.0.0.1', '', 'signup', 8, 2);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (17, '2026-10-20 00:49:48.360812+00', '127.0.0.1', '', 'signup', 9, 1);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (18, '2026-10-20 00:49:48.361795+00', '127.0.0.1', '', 'signup', 9, 2);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (19, '2026-10-20 00:49:49.146531+00', '127.0.0.1', '', 'signup', 10, 1);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (20, '2026-10-20 00:49:49.147331+00', '127.0.0.1', '', 'signup', 10, 2);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (21, '2026-10-20 00:49:50.117388+00', '127.0.0.1', '', 'signup', 11, 1);
INSERT INTO public.sitecontent_policyacceptance (id, accepted_at, ip, user_agent, method, user_id, version_id) VALUES (22, '2026-10-20 00:49:50.118042+00', '127.0.0.1', '', 'signup', 11, 2);


--
-- Name: accounts_accountapplication_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_accountapplication_id_seq', 9, true);


--
-- Name: accounts_rolechangerequest_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_rolechangerequest_id_seq', 1, true);


--
-- Name: accounts_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.accounts_user_id_seq', 11, true);


--
-- Name: directory_articlesection_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_articlesection_id_seq', 168, true);


--
-- Name: directory_association_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_association_id_seq', 4, true);


--
-- Name: directory_association_sectors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_association_sectors_id_seq', 1, true);


--
-- Name: directory_company_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_company_id_seq', 24, true);


--
-- Name: directory_company_sectors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_company_sectors_id_seq', 48, true);


--
-- Name: directory_companyproduct_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_companyproduct_id_seq', 24, true);


--
-- Name: directory_event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_event_id_seq', 6, true);


--
-- Name: directory_eventparticipant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_eventparticipant_id_seq', 30, true);


--
-- Name: directory_membership_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_membership_id_seq', 31, true);


--
-- Name: directory_milestone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_milestone_id_seq', 150, true);


--
-- Name: directory_person_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_person_id_seq', 24, true);


--
-- Name: directory_personcompany_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_personcompany_id_seq', 24, true);


--
-- Name: directory_source_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_source_id_seq', 96, true);


--
-- Name: directory_video_associations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_video_associations_id_seq', 1, false);


--
-- Name: directory_video_companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_video_companies_id_seq', 2, true);


--
-- Name: directory_video_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_video_events_id_seq', 1, true);


--
-- Name: directory_video_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_video_id_seq', 6, true);


--
-- Name: directory_video_persons_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_video_persons_id_seq', 3, true);


--
-- Name: moderation_auditlog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.moderation_auditlog_id_seq', 7, true);


--
-- Name: moderation_profileclaim_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.moderation_profileclaim_id_seq', 1, true);


--
-- Name: moderation_revision_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.moderation_revision_id_seq', 53, true);


--
-- Name: sitecontent_contactmessage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sitecontent_contactmessage_id_seq', 2, true);


--
-- Name: sitecontent_datarequest_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sitecontent_datarequest_id_seq', 1, true);


--
-- Name: sitecontent_donationaccount_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sitecontent_donationaccount_id_seq', 2, true);


--
-- Name: sitecontent_interviewrequest_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sitecontent_interviewrequest_id_seq', 3, true);


--
-- Name: sitecontent_policyacceptance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sitecontent_policyacceptance_id_seq', 22, true);


--
-- PostgreSQL database dump complete
--

\unrestrict LKmpzhC1CZdSRxA7QH6LZ3S7VFFkZh7fqmcXTEV2DpXpE4yDvyUfErFLBg8jcmJ

COMMIT;
