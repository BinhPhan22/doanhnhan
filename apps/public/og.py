"""
Tự động tạo ảnh OpenGraph (1200x630) chất lượng cao cho chia sẻ mạng xã hội (Facebook, Zalo, LinkedIn, Twitter/X).
"""
import io
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]


def _get_font(size=20, bold=False):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def generate_person_og_image(person):
    width, height = 1200, 630
    im = Image.new("RGB", (width, height), color="#0B1A2E")
    draw = ImageDraw.Draw(im)

    # 1. Subtle decorative background panels and gold borders
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline="#C9A24A", width=2)
    draw.rectangle([(26, 26), (width - 26, height - 26)], outline="#22344F", width=1)

    # Accent banner at top
    draw.rectangle([(20, 20), (width - 20, 90)], fill="#12253F")
    draw.line([(20, 90), (width - 20, 90)], fill="#C9A24A", width=2)

    font_brand = _get_font(22, bold=True)
    font_brand_sub = _get_font(14)
    draw.text((50, 42), "DOANHNHAN.WIKI", fill="#E3C77A", font=font_brand)
    draw.text((270, 47), "·  BÁCH KHOA TOÀN THƯ DOANH NHÂN TRẺ VIỆT NAM", fill="#C3CAD4", font=font_brand_sub)

    # 2. Portrait / Avatar (left column)
    portrait_size = (240, 240)
    portrait_box = (60, 150)
    has_portrait = False

    if person.portrait and hasattr(person.portrait, "path") and os.path.exists(person.portrait.path):
        try:
            p_img = Image.open(person.portrait.path).convert("RGBA")
            p_img = ImageOps.fit(p_img, portrait_size, method=Image.Resampling.LANCZOS)

            # Circular mask
            mask = Image.new("L", portrait_size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, portrait_size[0], portrait_size[1]), fill=255)

            im.paste(p_img, portrait_box, mask)
            # Gold circle border
            draw.ellipse([portrait_box[0] - 2, portrait_box[1] - 2,
                          portrait_box[0] + portrait_size[0] + 2, portrait_box[1] + portrait_size[1] + 2],
                         outline="#C9A24A", width=4)
            has_portrait = True
        except Exception:
            has_portrait = False

    if not has_portrait:
        # Monogram initials circle
        draw.ellipse([portrait_box[0], portrait_box[1],
                      portrait_box[0] + portrait_size[0], portrait_box[1] + portrait_size[1]],
                     fill="#1A2C45", outline="#C9A24A", width=4)
        font_initials = _get_font(90, bold=True)
        initials = person.initials
        bbox = draw.textbbox((0, 0), initials, font=font_initials)
        w_text = bbox[2] - bbox[0]
        h_text = bbox[3] - bbox[1]
        x_text = portrait_box[0] + (portrait_size[0] - w_text) / 2
        y_text = portrait_box[1] + (portrait_size[1] - h_text) / 2 - 10
        draw.text((x_text, y_text), initials, fill="#E3C77A", font=font_initials)

    # 3. Content Details (right column)
    text_x = 350
    curr_y = 145

    # Badges / Pills: Verification & Award
    badge_x = text_x
    if person.verification != "none":
        ver_text = "✓ ĐÃ XÁC MINH"
        font_pill = _get_font(14, bold=True)
        draw.rounded_rectangle([badge_x, curr_y, badge_x + 140, curr_y + 30], radius=15, fill="#0B4A3E")
        draw.text((badge_x + 16, curr_y + 6), ver_text, fill="#E3F2EC", font=font_pill)
        badge_x += 155

    # Honorary award badge (Feature 4 integration)
    award = person.awards.select_related("badge").first()
    if award:
        award_label = f"★ {award.badge.name}"
        if award.year:
            award_label += f" ({award.year})"
        if len(award_label) > 42:
            award_label = award_label[:40] + "…"
        font_award = _get_font(14, bold=True)
        bbox = draw.textbbox((0, 0), award_label, font=font_award)
        bw = bbox[2] - bbox[0] + 30
        draw.rounded_rectangle([badge_x, curr_y, badge_x + bw, curr_y + 30], radius=15, fill="#8A6A1F")
        draw.text((badge_x + 15, curr_y + 6), award_label, fill="#FFFFFF", font=font_award)

    curr_y += 45

    # Full Name
    font_name = _get_font(44, bold=True)
    draw.text((text_x, curr_y), person.full_name, fill="#FFFFFF", font=font_name)
    curr_y += 60

    # Role & Primary Company
    primary = person.primary_link
    if primary:
        role_label = f"{primary.label} · {primary.company.display_name}"
    else:
        role_label = person.headline or "Doanh nhân tiêu biểu"

    font_role = _get_font(24, bold=True)
    draw.text((text_x, curr_y), role_label, fill="#E3C77A", font=font_role)
    curr_y += 45

    # Association / Industry metadata
    meta_parts = []
    if primary and primary.company.primary_sector:
        meta_parts.append(f"Ngành: {primary.company.primary_sector.name}")
    if person.current_province:
        meta_parts.append(f"Địa bàn: {person.current_province.name}")
    if person.birth_year and person.show_birth_year:
        meta_parts.append(f"Năm sinh: {person.birth_year}")

    if meta_parts:
        font_meta = _get_font(18)
        draw.text((text_x, curr_y), "   |   ".join(meta_parts), fill="#C3CAD4", font=font_meta)
        curr_y += 40

    # Summary excerpt
    summary_sec = person.sections.filter(key="summary").first()
    if summary_sec:
        summary_text = summary_sec.body_md.replace("\n", " ").strip()
        if len(summary_text) > 140:
            summary_text = summary_text[:137] + "..."
        font_summary = _get_font(16)
        draw.text((text_x, curr_y + 10), summary_text, fill="#A6B4C4", font=font_summary)

    # 4. Footer Bar
    draw.line([(20, 560), (width - 20, 560)], fill="#22344F", width=1)
    font_foot = _get_font(15)
    draw.text((60, 575), "Hồ sơ công khai có nguồn kiểm chứng độc lập & lịch sử minh bạch", fill="#AEB8C5", font=font_foot)
    draw.text((width - 380, 575), f"doanhnhan.wiki/doanh-nhan/{person.slug}/", fill="#E3C77A", font=font_foot)

    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def generate_company_og_image(company):
    width, height = 1200, 630
    im = Image.new("RGB", (width, height), color="#0B1A2E")
    draw = ImageDraw.Draw(im)

    # 1. Subtle decorative background panels and gold borders
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline="#C9A24A", width=2)
    draw.rectangle([(26, 26), (width - 26, height - 26)], outline="#22344F", width=1)

    # Accent banner at top
    draw.rectangle([(20, 20), (width - 20, 90)], fill="#12253F")
    draw.line([(20, 90), (width - 20, 90)], fill="#C9A24A", width=2)

    font_brand = _get_font(22, bold=True)
    font_brand_sub = _get_font(14)
    draw.text((50, 42), "DOANHNHAN.WIKI", fill="#E3C77A", font=font_brand)
    draw.text((270, 47), "·  HỒ SƠ DOANH NGHIỆP TIÊU BIỂU VIỆT NAM", fill="#C3CAD4", font=font_brand_sub)

    # 2. Company Logo / Monogram (left column)
    logo_size = (240, 240)
    logo_box = (60, 150)
    has_logo = False

    if company.logo and hasattr(company.logo, "path") and os.path.exists(company.logo.path):
        try:
            l_img = Image.open(company.logo.path).convert("RGBA")
            bg = Image.new("RGBA", logo_size, (255, 255, 255, 255))
            l_fit = ImageOps.contain(l_img, (200, 200), method=Image.Resampling.LANCZOS)
            offset_x = (240 - l_fit.width) // 2
            offset_y = (240 - l_fit.height) // 2
            bg.paste(l_fit, (offset_x, offset_y), l_fit if l_fit.mode == "RGBA" else None)
            im.paste(bg.convert("RGB"), logo_box)
            draw.rectangle([logo_box[0] - 2, logo_box[1] - 2,
                            logo_box[0] + logo_size[0] + 2, logo_box[1] + logo_size[1] + 2],
                           outline="#C9A24A", width=3)
            has_logo = True
        except Exception:
            has_logo = False

    if not has_logo:
        draw.rectangle([logo_box[0], logo_box[1],
                        logo_box[0] + logo_size[0], logo_box[1] + logo_size[1]],
                       fill="#1A2C45", outline="#C9A24A", width=3)
        font_initials = _get_font(80, bold=True)
        initials = company.initials
        bbox = draw.textbbox((0, 0), initials, font=font_initials)
        w_text = bbox[2] - bbox[0]
        h_text = bbox[3] - bbox[1]
        x_text = logo_box[0] + (logo_size[0] - w_text) / 2
        y_text = logo_box[1] + (logo_size[1] - h_text) / 2 - 10
        draw.text((x_text, y_text), initials, fill="#E3C77A", font=font_initials)

    # 3. Content Details (right column)
    text_x = 350
    curr_y = 145

    # Badges / Pills: Verification & Award
    badge_x = text_x
    if company.verification != "none":
        ver_text = "✓ DOANH NGHIỆP XÁC MINH"
        font_pill = _get_font(14, bold=True)
        draw.rounded_rectangle([badge_x, curr_y, badge_x + 210, curr_y + 30], radius=15, fill="#0B4A3E")
        draw.text((badge_x + 14, curr_y + 6), ver_text, fill="#E3F2EC", font=font_pill)
        badge_x += 225

    award = company.awards.select_related("badge").first()
    if award:
        award_label = f"★ {award.badge.name}"
        if award.year:
            award_label += f" ({award.year})"
        if len(award_label) > 40:
            award_label = award_label[:38] + "…"
        font_award = _get_font(14, bold=True)
        bbox = draw.textbbox((0, 0), award_label, font=font_award)
        bw = bbox[2] - bbox[0] + 30
        draw.rounded_rectangle([badge_x, curr_y, badge_x + bw, curr_y + 30], radius=15, fill="#8A6A1F")
        draw.text((badge_x + 15, curr_y + 6), award_label, fill="#FFFFFF", font=font_award)

    curr_y += 45

    # Display Name
    font_name = _get_font(40, bold=True)
    name_display = company.display_name
    if len(name_display) > 30:
        name_display = name_display[:28] + "…"
    draw.text((text_x, curr_y), name_display, fill="#FFFFFF", font=font_name)
    curr_y += 58

    # Legal Name & Tax code
    legal_line = company.legal_name
    if company.tax_code:
        legal_line += f"  ·  MST: {company.tax_code}"
    font_sub = _get_font(21, bold=True)
    draw.text((text_x, curr_y), legal_line, fill="#E3C77A", font=font_sub)
    curr_y += 45

    # Sector / Location / Founded
    meta_parts = []
    if company.primary_sector:
        meta_parts.append(f"Ngành: {company.primary_sector.name}")
    if company.province:
        meta_parts.append(f"Trụ sở: {company.province.name}")
    if company.founded_year:
        meta_parts.append(f"Thành lập: {company.founded_year}")

    if meta_parts:
        font_meta = _get_font(18)
        draw.text((text_x, curr_y), "   |   ".join(meta_parts), fill="#C3CAD4", font=font_meta)
        curr_y += 40

    # Overview excerpt
    overview_sec = company.sections.filter(key="overview").first()
    if overview_sec:
        ov_text = overview_sec.body_md.replace("\n", " ").strip()
        if len(ov_text) > 140:
            ov_text = ov_text[:137] + "..."
        font_overview = _get_font(16)
        draw.text((text_x, curr_y + 10), ov_text, fill="#A6B4C4", font=font_overview)

    # 4. Footer Bar
    draw.line([(20, 560), (width - 20, 560)], fill="#22344F", width=1)
    font_foot = _get_font(15)
    draw.text((60, 575), "Hồ sơ doanh nghiệp chính thức được xác thực thông tin minh bạch", fill="#AEB8C5", font=font_foot)
    draw.text((width - 400, 575), f"doanhnhan.wiki/doanh-nghiep/{company.slug}/", fill="#E3C77A", font=font_foot)

    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def generate_default_og_image():
    width, height = 1200, 630
    im = Image.new("RGB", (width, height), color="#0B1A2E")
    draw = ImageDraw.Draw(im)

    # Borders
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline="#C9A24A", width=2)
    draw.rectangle([(26, 26), (width - 26, height - 26)], outline="#22344F", width=1)

    # Accent banner at top
    draw.rectangle([(20, 20), (width - 20, 90)], fill="#12253F")
    draw.line([(20, 90), (width - 20, 90)], fill="#C9A24A", width=2)

    font_brand = _get_font(24, bold=True)
    font_brand_sub = _get_font(15)
    draw.text((50, 40), "DOANHNHAN.WIKI", fill="#E3C77A", font=font_brand)
    draw.text((290, 45), "·  BÁCH KHOA TOÀN THƯ DOANH NHÂN TRẺ VIỆT NAM", fill="#C3CAD4", font=font_brand_sub)

    # Center branding
    font_title = _get_font(56, bold=True)
    title_text = "doanhnhan.wiki"
    bbox = draw.textbbox((0, 0), title_text, font=font_title)
    w = bbox[2] - bbox[0]
    draw.text(((width - w) / 2, 200), title_text, fill="#E3C77A", font=font_title)

    font_lead = _get_font(24, bold=True)
    lead_text = "Nơi lưu giữ hành trình của doanh nhân trẻ tiêu biểu Việt Nam"
    bbox = draw.textbbox((0, 0), lead_text, font=font_lead)
    w = bbox[2] - bbox[0]
    draw.text(((width - w) / 2, 275), lead_text, fill="#FFFFFF", font=font_lead)

    font_desc = _get_font(18)
    desc_text = "Hồ sơ doanh nhân · Doanh nghiệp · Dấu mốc · Sự kiện · Video phỏng vấn có kiểm chứng"
    bbox = draw.textbbox((0, 0), desc_text, font=font_desc)
    w = bbox[2] - bbox[0]
    draw.text(((width - w) / 2, 325), desc_text, fill="#C3CAD4", font=font_desc)

    # Badges row
    font_pill = _get_font(15, bold=True)
    pills = ["✓ Có nguồn đối chiếu", "✓ Kiểm duyệt minh bạch", "✓ Bản quyền xác nhận"]
    total_w = len(pills) * 230
    start_x = (width - total_w) / 2
    for idx, p in enumerate(pills):
        px = start_x + idx * 230
        draw.rounded_rectangle([px, 395, px + 210, 435], radius=20, fill="#12253F", outline="#C9A24A", width=1)
        draw.text((px + 20, 407), p, fill="#E3C77A", font=font_pill)

    # Footer
    draw.line([(20, 560), (width - 20, 560)], fill="#22344F", width=1)
    font_foot = _get_font(15)
    draw.text((60, 575), "Bách khoa toàn thư mở dành cho cộng đồng khởi nghiệp & doanh nhân", fill="#AEB8C5", font=font_foot)
    draw.text((width - 270, 575), "https://doanhnhan.wiki", fill="#E3C77A", font=font_foot)

    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

