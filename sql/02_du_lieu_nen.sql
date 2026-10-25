-- doanhnhan.wiki · 02 – Dữ liệu nền (dữ liệu thật)
-- Sinh tự động từ PostgreSQL ngày 20/10/2026 bằng sql/xuat_sql.sh. Mã hóa UTF-8.
-- 34 tỉnh/thành (sắp xếp từ 12/6/2025), cây ngành nghề kèm mã VSIC 2025 cấp 2, văn bản chính sách (bản khung chờ luật sư), bài viết trang Donate, cài đặt chung.

BEGIN;
SET CONSTRAINTS ALL DEFERRED;
--
-- PostgreSQL database dump
--

\restrict EhErHRaLDS6uRL3sR6qPm3PW64tvAuUlUt83WcOWoq0PU7yoXFJMm2CuMFCHI6A

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
-- Data for Name: directory_province; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (1, 'ha-noi', 'Hà Nội', true, '', 0);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (2, 'tp-ho-chi-minh', 'TP. Hồ Chí Minh', true, 'TP. Hồ Chí Minh, Bà Rịa – Vũng Tàu, Bình Dương', 1);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (3, 'hai-phong', 'Hải Phòng', true, 'Hải Phòng, Hải Dương', 2);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (4, 'da-nang', 'Đà Nẵng', true, 'Đà Nẵng, Quảng Nam', 3);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (5, 'can-tho', 'Cần Thơ', true, 'Cần Thơ, Sóc Trăng, Hậu Giang', 4);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (6, 'hue', 'Huế', true, '', 5);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (7, 'an-giang', 'An Giang', false, 'An Giang, Kiên Giang', 6);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (8, 'bac-ninh', 'Bắc Ninh', false, 'Bắc Ninh, Bắc Giang', 7);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (9, 'ca-mau', 'Cà Mau', false, 'Cà Mau, Bạc Liêu', 8);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (10, 'cao-bang', 'Cao Bằng', false, '', 9);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (11, 'dak-lak', 'Đắk Lắk', false, 'Đắk Lắk, Phú Yên', 10);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (12, 'dien-bien', 'Điện Biên', false, '', 11);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (13, 'dong-nai', 'Đồng Nai', false, 'Đồng Nai, Bình Phước', 12);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (14, 'dong-thap', 'Đồng Tháp', false, 'Đồng Tháp, Tiền Giang', 13);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (15, 'gia-lai', 'Gia Lai', false, 'Gia Lai, Bình Định', 14);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (16, 'ha-tinh', 'Hà Tĩnh', false, '', 15);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (17, 'hung-yen', 'Hưng Yên', false, 'Hưng Yên, Thái Bình', 16);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (18, 'khanh-hoa', 'Khánh Hòa', false, 'Khánh Hòa, Ninh Thuận', 17);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (19, 'lai-chau', 'Lai Châu', false, '', 18);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (20, 'lam-dong', 'Lâm Đồng', false, 'Lâm Đồng, Đắk Nông, Bình Thuận', 19);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (21, 'lang-son', 'Lạng Sơn', false, '', 20);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (22, 'lao-cai', 'Lào Cai', false, 'Lào Cai, Yên Bái', 21);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (23, 'nghe-an', 'Nghệ An', false, '', 22);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (24, 'ninh-binh', 'Ninh Bình', false, 'Ninh Bình, Hà Nam, Nam Định', 23);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (25, 'phu-tho', 'Phú Thọ', false, 'Phú Thọ, Vĩnh Phúc, Hòa Bình', 24);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (26, 'quang-ngai', 'Quảng Ngãi', false, 'Quảng Ngãi, Kon Tum', 25);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (27, 'quang-ninh', 'Quảng Ninh', false, '', 26);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (28, 'quang-tri', 'Quảng Trị', false, 'Quảng Trị, Quảng Bình', 27);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (29, 'son-la', 'Sơn La', false, '', 28);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (30, 'tay-ninh', 'Tây Ninh', false, 'Tây Ninh, Long An', 29);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (31, 'thai-nguyen', 'Thái Nguyên', false, 'Thái Nguyên, Bắc Kạn', 30);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (32, 'thanh-hoa', 'Thanh Hóa', false, '', 31);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (33, 'tuyen-quang', 'Tuyên Quang', false, 'Tuyên Quang, Hà Giang', 32);
INSERT INTO public.directory_province (id, code, name, is_city, merged_from, sort_order) VALUES (34, 'vinh-long', 'Vĩnh Long', false, 'Vĩnh Long, Bến Tre, Trà Vinh', 33);


--
-- Data for Name: directory_sector; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (1, 'cong-nghe-phan-mem', 'cong nghe & phan mem', '2026-10-20 00:49:39.156806+00', '2026-10-20 00:49:39.156834+00', 'Công nghệ & Phần mềm', 'Nền tảng số, AI, thương mại điện tử', 'tech', '62, 63', 0, true, NULL);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (2, 'phan-mem-doanh-nghiep', 'phan mem doanh nghiep', '2026-10-20 00:49:39.161766+00', '2026-10-20 00:49:39.161787+00', 'Phần mềm doanh nghiệp', '', 'tech', '62', 0, true, 1);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (3, 'thuong-mai-dien-tu', 'thuong mai dien tu', '2026-10-20 00:49:39.16568+00', '2026-10-20 00:49:39.1657+00', 'Thương mại điện tử', '', 'tech', '47', 1, true, 1);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (4, 'fintech', 'fintech', '2026-10-20 00:49:39.169398+00', '2026-10-20 00:49:39.169418+00', 'Fintech', '', 'tech', '66', 2, true, 1);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (5, 'ai-du-lieu', 'ai & du lieu', '2026-10-20 00:49:39.172709+00', '2026-10-20 00:49:39.172729+00', 'AI & Dữ liệu', '', 'tech', '63', 3, true, 1);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (6, 'edtech', 'edtech', '2026-10-20 00:49:39.176213+00', '2026-10-20 00:49:39.176232+00', 'Edtech', '', 'tech', '85', 4, true, 1);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (7, 'marketing-so', 'marketing so', '2026-10-20 00:49:39.179656+00', '2026-10-20 00:49:39.179674+00', 'Marketing số', '', 'tech', '73', 5, true, 1);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (8, 'san-xuat-vat-lieu', 'san xuat – vat lieu', '2026-10-20 00:49:39.182836+00', '2026-10-20 00:49:39.182856+00', 'Sản xuất – Vật liệu', 'Nhà máy, cơ khí, vật liệu xây dựng', 'factory', 'C', 1, true, NULL);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (9, 'co-khi-che-tao', 'co khi – che tao', '2026-10-20 00:49:39.186305+00', '2026-10-20 00:49:39.186326+00', 'Cơ khí – chế tạo', '', 'factory', '25', 0, true, 8);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (10, 'vat-lieu-xay-dung', 'vat lieu xay dung', '2026-10-20 00:49:39.189231+00', '2026-10-20 00:49:39.189247+00', 'Vật liệu xây dựng', '', 'factory', '23', 1, true, 8);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (11, 'det-may-da-giay', 'det may – da giay', '2026-10-20 00:49:39.19299+00', '2026-10-20 00:49:39.193007+00', 'Dệt may – da giày', '', 'factory', '13, 14, 15', 2, true, 8);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (12, 'bao-bi-nhua', 'bao bi – nhua', '2026-10-20 00:49:39.196385+00', '2026-10-20 00:49:39.196406+00', 'Bao bì – nhựa', '', 'factory', '22', 3, true, 8);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (13, 'thuong-mai-ban-le', 'thuong mai – ban le', '2026-10-20 00:49:39.199892+00', '2026-10-20 00:49:39.199912+00', 'Thương mại – Bán lẻ', 'Chuỗi cửa hàng, phân phối, xuất nhập khẩu', 'retail', '46, 47', 2, true, NULL);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (14, 'chuoi-ban-le', 'chuoi ban le', '2026-10-20 00:49:39.203725+00', '2026-10-20 00:49:39.203748+00', 'Chuỗi bán lẻ', '', 'retail', '47', 0, true, 13);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (15, 'phan-phoi', 'phan phoi', '2026-10-20 00:49:39.208349+00', '2026-10-20 00:49:39.208366+00', 'Phân phối', '', 'retail', '46', 1, true, 13);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (16, 'xuat-nhap-khau', 'xuat nhap khau', '2026-10-20 00:49:39.212021+00', '2026-10-20 00:49:39.21204+00', 'Xuất nhập khẩu', '', 'retail', '46', 2, true, 13);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (17, 'f-b-nha-hang', 'f&b – nha hang', '2026-10-20 00:49:39.214962+00', '2026-10-20 00:49:39.21498+00', 'F&B – Nhà hàng', 'Chuỗi ẩm thực, cà phê, thực phẩm chế biến', 'food', '56, 10', 3, true, NULL);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (18, 'chuoi-nha-hang', 'chuoi nha hang', '2026-10-20 00:49:39.21797+00', '2026-10-20 00:49:39.217989+00', 'Chuỗi nhà hàng', '', 'food', '56', 0, true, 17);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (19, 'ca-phe-do-uong', 'ca phe – do uong', '2026-10-20 00:49:39.221957+00', '2026-10-20 00:49:39.221971+00', 'Cà phê – đồ uống', '', 'food', '56', 1, true, 17);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (20, 'thuc-pham-che-bien', 'thuc pham che bien', '2026-10-20 00:49:39.22495+00', '2026-10-20 00:49:39.224965+00', 'Thực phẩm chế biến', '', 'food', '10', 2, true, 17);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (21, 'xay-dung-bat-dong-san', 'xay dung – bat dong san', '2026-10-20 00:49:39.227648+00', '2026-10-20 00:49:39.227671+00', 'Xây dựng – Bất động sản', 'Thi công, phát triển dự án, nội thất', 'building', '41–43, 68', 4, true, NULL);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (22, 'thi-cong-xay-dung', 'thi cong xay dung', '2026-10-20 00:49:39.230782+00', '2026-10-20 00:49:39.230796+00', 'Thi công xây dựng', '', 'building', '41, 42', 0, true, 21);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (23, 'phat-trien-du-an', 'phat trien du an', '2026-10-20 00:49:39.235685+00', '2026-10-20 00:49:39.235706+00', 'Phát triển dự án', '', 'building', '68', 1, true, 21);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (24, 'noi-that-kien-truc', 'noi that – kien truc', '2026-10-20 00:49:39.243314+00', '2026-10-20 00:49:39.243331+00', 'Nội thất – kiến trúc', '', 'building', '43', 2, true, 21);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (25, 'giao-duc-dao-tao', 'giao duc – dao tao', '2026-10-20 00:49:39.246312+00', '2026-10-20 00:49:39.246328+00', 'Giáo dục – Đào tạo', 'Trường học, đào tạo kỹ năng, edtech', 'education', '85', 5, true, NULL);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (26, 'truong-hoc', 'truong hoc', '2026-10-20 00:49:39.24974+00', '2026-10-20 00:49:39.249757+00', 'Trường học', '', 'education', '85', 0, true, 25);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (27, 'dao-tao-ky-nang', 'dao tao ky nang', '2026-10-20 00:49:39.253102+00', '2026-10-20 00:49:39.253124+00', 'Đào tạo kỹ năng', '', 'education', '85', 1, true, 25);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (28, 'ngoai-ngu', 'ngoai ngu', '2026-10-20 00:49:39.256945+00', '2026-10-20 00:49:39.25696+00', 'Ngoại ngữ', '', 'education', '85', 2, true, 25);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (29, 'nong-nghiep-thuc-pham', 'nong nghiep – thuc pham', '2026-10-20 00:49:39.259681+00', '2026-10-20 00:49:39.259695+00', 'Nông nghiệp – Thực phẩm', 'Nông sản sạch, chế biến, chuỗi cung ứng', 'agri', '01, 03, 10', 6, true, NULL);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (30, 'nong-san-sach', 'nong san sach', '2026-10-20 00:49:39.262339+00', '2026-10-20 00:49:39.262353+00', 'Nông sản sạch', '', 'agri', '01', 0, true, 29);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (31, 'che-bien-nong-san', 'che bien nong san', '2026-10-20 00:49:39.266617+00', '2026-10-20 00:49:39.266632+00', 'Chế biến nông sản', '', 'agri', '10', 1, true, 29);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (32, 'thuy-san', 'thuy san', '2026-10-20 00:49:39.269889+00', '2026-10-20 00:49:39.269909+00', 'Thủy sản', '', 'agri', '03', 2, true, 29);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (33, 'dich-vu-logistics', 'dich vu – logistics', '2026-10-20 00:49:39.273072+00', '2026-10-20 00:49:39.273092+00', 'Dịch vụ – Logistics', 'Vận tải, kho bãi, dịch vụ doanh nghiệp', 'logistics', '49–53, 82', 7, true, NULL);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (34, 'van-tai', 'van tai', '2026-10-20 00:49:39.276616+00', '2026-10-20 00:49:39.276631+00', 'Vận tải', '', 'logistics', '49', 0, true, 33);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (35, 'kho-bai', 'kho bai', '2026-10-20 00:49:39.279298+00', '2026-10-20 00:49:39.279313+00', 'Kho bãi', '', 'logistics', '52', 1, true, 33);
INSERT INTO public.directory_sector (id, slug, search_text, created_at, updated_at, name, description, icon, vsic_code, sort_order, is_active, parent_id) VALUES (36, 'dich-vu-doanh-nghiep', 'dich vu doanh nghiep', '2026-10-20 00:49:39.28207+00', '2026-10-20 00:49:39.282084+00', 'Dịch vụ doanh nghiệp', '', 'logistics', '82', 2, true, 33);


--
-- Data for Name: sitecontent_donationsettings; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.sitecontent_donationsettings (id, title, lead, body_md, memo, updated_at, updated_by_id) VALUES (1, 'Cùng doanhnhan.wiki lưu giữ hành trình của doanh nhân trẻ tiêu biểu Việt Nam', 'Mỗi doanh nhân trẻ tiêu biểu là một câu chuyện về khát vọng, bản lĩnh và đóng góp cho nền kinh tế. doanhnhan.wiki ra đời để những câu chuyện ấy được ghi chép đầy đủ, xác minh cẩn thận và lưu giữ lâu dài — để hôm nay có nơi tra cứu, và thế hệ sau có nơi học hỏi.', '## Vì sao cần doanhnhan.wiki
Thông tin về doanh nhân trẻ hôm nay nằm rải rác trên báo chí, mạng xã hội và hồ sơ của các hiệp hội — khó tìm, khó kiểm chứng và dễ thất lạc theo thời gian. doanhnhan.wiki gom những thông tin ấy về một nơi: hồ sơ doanh nhân, doanh nghiệp, dấu mốc sự nghiệp, sự kiện và video phỏng vấn. Mỗi thông tin đều có nguồn trích dẫn và lịch sử chỉnh sửa minh bạch. Việc tra cứu luôn miễn phí cho tất cả mọi người.

## Chi phí để trang được duy trì
Để một kho dữ liệu đáng tin cậy tồn tại lâu dài, doanhnhan.wiki cần chi trả thường xuyên cho:

- **Máy chủ, tên miền và đường truyền** — để trang luôn hoạt động ổn định.
- **Bảo mật và sao lưu dữ liệu** — bảo vệ thông tin của các doanh nhân.
- **Biên tập và xác minh** — đối chiếu nguồn, kiểm duyệt từng hồ sơ trước khi công bố.
- **Phỏng vấn và ghi hình** — lưu lại câu chuyện bằng chính lời kể của doanh nhân.
- **Phát triển tính năng** — giúp cộng đồng tra cứu và kết nối dễ dàng hơn.

## Mọi khoản tài trợ đều quý giá
Không có mức tối thiểu. Dù nhiều hay ít, khoản tài trợ của anh chị là sự tiếp sức để doanhnhan.wiki tiếp tục ghi lại hành trình của doanh nhân trẻ Việt Nam. Toàn bộ kinh phí nhận được được dùng cho hoạt động của trang.

**Trân trọng cảm ơn anh chị đã đồng hành!**

*Ban vận hành doanhnhan.wiki*
', 'Tài trợ website doanhnhan.wiki', '2026-10-20 00:49:39.312763+00', NULL);


--
-- Data for Name: sitecontent_policydocument; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.sitecontent_policydocument (id, code, title, requires_acceptance, sort_order) VALUES (1, 'dieu-khoan', 'Điều khoản sử dụng', true, 1);
INSERT INTO public.sitecontent_policydocument (id, code, title, requires_acceptance, sort_order) VALUES (2, 'chinh-sach-du-lieu', 'Chính sách bảo vệ dữ liệu cá nhân', true, 2);
INSERT INTO public.sitecontent_policydocument (id, code, title, requires_acceptance, sort_order) VALUES (3, 'quy-che-bien-tap', 'Quy chế biên tập & xác minh', false, 3);
INSERT INTO public.sitecontent_policydocument (id, code, title, requires_acceptance, sort_order) VALUES (4, 'chinh-sach-cookie', 'Chính sách cookie', false, 4);
INSERT INTO public.sitecontent_policydocument (id, code, title, requires_acceptance, sort_order) VALUES (5, 'quy-dinh-tai-tro', 'Quy định về tài trợ', false, 5);


--
-- Data for Name: sitecontent_policyversion; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.sitecontent_policyversion (id, version, effective_at, summary_of_changes, summary_points, body_md, status, require_reaccept, created_at, created_by_id, document_id) VALUES (1, '1.0', '2026-10-20 00:49:39.288034+00', 'Phiên bản đầu tiên.', 'doanhnhan.wiki là trang cộng đồng lưu giữ hồ sơ doanh nhân trẻ, do Digits Technology vận hành.
Xem thông tin không cần tài khoản; muốn đưa thông tin lên cần tài khoản được duyệt.
Mọi nội dung được duyệt trước khi công bố và có lịch sử sửa đổi.', '> **Bản khung — cần luật sư rà soát và hoàn thiện trước khi công bố chính thức.**

## 1. Phạm vi áp dụng
[Nội dung do luật sư soạn: đơn vị vận hành, đối tượng áp dụng, hiệu lực khi truy cập hoặc đăng ký.]

## 2. Tài khoản & hồ sơ
- Xem thông tin trên doanhnhan.wiki không cần tài khoản.
- Tài khoản chỉ cần khi đưa thông tin lên; mỗi tài khoản được ban quản trị duyệt trước khi sử dụng.
- Người dùng chịu trách nhiệm về tính chính xác của thông tin mình gửi.
[Nội dung do luật sư soạn: nhận quản lý hồ sơ, đình chỉ tài khoản.]

## 3. Nội dung đóng góp
- Mọi nội dung được ban biên tập duyệt trước khi công bố và lưu lịch sử sửa đổi.
- Video được nhúng từ nền tảng gốc (YouTube, Vimeo, Facebook, TikTok); doanhnhan.wiki không lưu trữ tệp video.
[Nội dung do luật sư soạn: quyền sử dụng nội dung người dùng gửi, giấy phép.]

## 4. Quyền sở hữu trí tuệ
[Nội dung do luật sư soạn.]

## 5. Hành vi bị cấm
[Nội dung do luật sư soạn: mạo danh, đăng thông tin sai sự thật, xâm phạm quyền riêng tư, spam…]

## 6. Giới hạn trách nhiệm
[Nội dung do luật sư soạn.]

## 7. Tạm ngừng, chấm dứt
[Nội dung do luật sư soạn.]

## 8. Luật áp dụng & tranh chấp
[Nội dung do luật sư soạn.]

## 9. Liên hệ
Digits Technology · [Địa chỉ] · [Email liên hệ]
', 'published', false, '2026-10-20 00:49:39.288363+00', NULL, 1);
INSERT INTO public.sitecontent_policyversion (id, version, effective_at, summary_of_changes, summary_points, body_md, status, require_reaccept, created_at, created_by_id, document_id) VALUES (2, '1.0', '2026-10-20 00:49:39.293401+00', 'Phiên bản đầu tiên.', 'Thông tin trên hồ sơ được công bố công khai.
Giấy tờ xác minh được lưu riêng tư.
Bạn có quyền yêu cầu xem, sửa, xóa dữ liệu hoặc rút lại đồng ý.', '> **Bản khung — cần luật sư rà soát và hoàn thiện trước khi công bố chính thức.**

## 1. Dữ liệu chúng tôi thu thập
- **Tài khoản:** họ tên, email, số điện thoại, mật khẩu (lưu dạng băm), thông tin đăng ký.
- **Hồ sơ công khai:** thông tin doanh nhân, doanh nghiệp do người dùng hoặc ban biên tập đưa lên.
- **Giấy tờ xác minh** khi nhận quản lý hồ sơ: lưu riêng tư, chỉ ban biên tập xem, không công khai.
- **Nhật ký kỹ thuật:** địa chỉ IP, thời điểm thao tác quan trọng (đăng nhập, duyệt, đồng ý điều khoản).

## 2. Mục đích xử lý
[Nội dung do luật sư soạn theo quy định hiện hành về bảo vệ dữ liệu cá nhân.]

## 3. Công khai thông tin
Thông tin trên hồ sơ được công bố công khai cho cộng đồng tra cứu. Chủ hồ sơ có thể chọn ẩn năm sinh, quê quán, email.

## 4. Quyền của chủ thể dữ liệu
Bạn có quyền yêu cầu xem, sửa, ẩn/xóa dữ liệu hoặc rút lại đồng ý tại trang **Yêu cầu về dữ liệu cá nhân**.
[Nội dung do luật sư soạn: thời hạn phản hồi, quy trình xác minh.]

## 5. Lưu trữ & bảo mật
[Nội dung do luật sư soạn.]

## 6. Liên hệ
Digits Technology · [Email bảo vệ dữ liệu]
', 'published', false, '2026-10-20 00:49:39.293611+00', NULL, 2);
INSERT INTO public.sitecontent_policyversion (id, version, effective_at, summary_of_changes, summary_points, body_md, status, require_reaccept, created_at, created_by_id, document_id) VALUES (3, '1.0', '2026-10-20 00:49:39.297934+00', 'Phiên bản đầu tiên.', 'Văn phong trung lập, có nguồn.
Biên tập viên duyệt trước khi công bố.
Mỗi lần sửa là một phiên bản.', 'Quy chế này áp dụng cho mọi nội dung trên doanhnhan.wiki: hồ sơ doanh nhân, doanh nghiệp, hiệp hội, sự kiện và video.

## 1. Nguyên tắc chung
- **Trung lập:** viết như bách khoa, ngôi thứ ba, không dùng ngôn ngữ quảng cáo.
- **Có nguồn:** mọi con số, giải thưởng, mốc quan trọng cần nguồn kiểm chứng; chú thích bằng [^1], [^2]… khớp mục Nguồn tham khảo.
- **Riêng tư:** không đăng thông tin cá nhân của người khác khi chưa được đồng ý; chủ hồ sơ có thể ẩn năm sinh, quê quán, email.

## 2. Quy trình duyệt
1. Thành viên đã được duyệt tài khoản gửi hồ sơ mới hoặc đề xuất sửa.
2. Hệ thống kiểm tra tự động theo quy tắc (trùng tên, mã số thuế, số từ, nguồn, dấu mốc, link video) để hỗ trợ biên tập viên.
3. Biên tập viên duyệt, yêu cầu bổ sung hoặc từ chối kèm lý do.
4. Nội dung được duyệt mới công bố; mỗi lần công bố là một phiên bản trong lịch sử sửa đổi.

## 3. Xác minh
- **Đã kiểm tra cơ bản:** đối chiếu thông tin công khai.
- **Đã xác minh:** đối chiếu mã số thuế trên Cổng thông tin quốc gia về đăng ký doanh nghiệp và/hoặc giấy tờ do chính chủ cung cấp.
- **Hiệp hội xác nhận:** hiệp hội đối tác xác nhận hội viên.

## 4. Video
Chỉ nhúng link từ YouTube, Vimeo, Facebook, TikTok; không lưu tệp video. Video có link không còn xem được sẽ tự ẩn.

## 5. Khiếu nại, đính chính
Báo thông tin chưa chính xác qua trang Liên hệ. Ban biên tập phản hồi trong thời gian sớm nhất.
', 'published', false, '2026-10-20 00:49:39.298112+00', NULL, 3);
INSERT INTO public.sitecontent_policyversion (id, version, effective_at, summary_of_changes, summary_points, body_md, status, require_reaccept, created_at, created_by_id, document_id) VALUES (4, '1.0', '2026-10-20 00:49:39.301921+00', 'Phiên bản đầu tiên.', 'Chỉ dùng cookie cần thiết.
Không có cookie quảng cáo.', 'doanhnhan.wiki chỉ dùng cookie cần thiết cho hoạt động của trang:

- **sessionid** — giữ trạng thái đăng nhập (chỉ khi bạn đăng nhập).
- **csrftoken** — chống giả mạo yêu cầu khi gửi biểu mẫu.

Trang không dùng cookie quảng cáo. Video nhúng chỉ được tải khi bạn bấm Phát; khi đó nền tảng video (YouTube dùng chế độ youtube-nocookie, Vimeo, Facebook, TikTok) có thể đặt cookie theo chính sách của họ.
', 'published', false, '2026-10-20 00:49:39.302092+00', NULL, 4);
INSERT INTO public.sitecontent_policyversion (id, version, effective_at, summary_of_changes, summary_points, body_md, status, require_reaccept, created_at, created_by_id, document_id) VALUES (5, '1.0', '2026-10-20 00:49:39.30721+00', 'Phiên bản đầu tiên.', 'Chỉ nhận qua tài khoản công bố trên trang Donate.
Tài trợ không ảnh hưởng việc duyệt hồ sơ.', '- doanhnhan.wiki chỉ nhận tài trợ qua tài khoản được công bố tại trang **Donate**. Tài khoản mới hoặc thay đổi phải được hai quản trị viên xác nhận.
- Không có mức tài trợ tối thiểu; tài trợ không ảnh hưởng tới việc duyệt, xác minh hay vị trí hiển thị của bất kỳ hồ sơ nào.
- Toàn bộ kinh phí dùng cho hoạt động của trang: máy chủ, bảo mật, biên tập, ghi hình, phát triển tính năng.
- [Nội dung do luật sư/kế toán bổ sung: chứng từ, hóa đơn, hoàn trả.]
', 'published', false, '2026-10-20 00:49:39.307407+00', NULL, 5);


--
-- Data for Name: sitecontent_sitesettings; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.sitecontent_sitesettings (id, operator_name, contact_email, editorial_email, contact_phone, address, about_md, review_days, updated_at) VALUES (1, 'Digits Technology', '', '', '', '', 'doanhnhan.wiki là **trang cộng đồng** lưu giữ hồ sơ doanh nhân trẻ tiêu biểu Việt Nam: doanh nghiệp, ngành nghề, hiệp hội, sự kiện và video phỏng vấn.

- **Ai cũng xem được** — không cần tài khoản.
- **Muốn đưa thông tin lên** — tạo tài khoản và chờ ban quản trị duyệt; mỗi nội dung vẫn được biên tập viên kiểm duyệt trước khi công bố.
- **Minh bạch** — mọi thông tin có nguồn trích dẫn và lịch sử sửa đổi.
- **Video** chỉ được nhúng từ nền tảng gốc, trang không lưu trữ tệp video.

Muốn kể câu chuyện của mình trước ống kính? Hãy liên hệ để được ghi hình, phỏng vấn.
', 3, '2026-10-20 00:49:39.316439+00');


--
-- Name: directory_province_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_province_id_seq', 34, true);


--
-- Name: directory_sector_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.directory_sector_id_seq', 36, true);


--
-- Name: sitecontent_donationsettings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sitecontent_donationsettings_id_seq', 1, false);


--
-- Name: sitecontent_policydocument_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sitecontent_policydocument_id_seq', 5, true);


--
-- Name: sitecontent_policyversion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sitecontent_policyversion_id_seq', 5, true);


--
-- Name: sitecontent_sitesettings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sitecontent_sitesettings_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

\unrestrict EhErHRaLDS6uRL3sR6qPm3PW64tvAuUlUt83WcOWoq0PU7yoXFJMm2CuMFCHI6A

COMMIT;
