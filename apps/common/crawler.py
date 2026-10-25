"""
Mô-đun cào dữ liệu và trích xuất hồ sơ doanh nhân & doanh nghiệp bằng AI (Google Gemini).
Hỗ trợ cào bài viết từ URL báo chí chính thống, chuẩn hóa văn bản, bóc tách cấu trúc JSON,
kiểm tra trùng lặp và lưu trữ vào cơ sở dữ liệu.
"""
import ipaddress
import json
import logging
import re
import socket
from urllib.parse import urlparse

from django.core.files.base import ContentFile
from django.core.validators import URLValidator
from django.db import transaction
from django.utils import timezone

import nh3
import requests

from apps.common.ai import get_ai_config
from apps.common.text import normalize, slugify_vi, word_count
from apps.common.validators import TAX_CODE_RE
from apps.directory.models import (
    ArticleSection, Company, Milestone, Person, PersonCompany, Province, Sector, Source, Status, Story,
)
from apps.moderation.models import AuditLog, log

logger = logging.getLogger(__name__)

DOMAIN_PUBLISHERS = {
    "tuoitre.vn": "Báo Tuổi Trẻ",
    "vnexpress.net": "VnExpress",
    "thanhnien.vn": "Báo Thanh Niên",
    "cafef.vn": "CafeF",
    "cafebiz.vn": "CafeBiz",
    "dantri.com.vn": "Báo Dân Trí",
    "vietnamnet.vn": "Báo VietNamNet",
    "forbes.vn": "Forbes Việt Nam",
    "vneconomy.vn": "VnEconomy",
    "baodautu.vn": "Báo Đầu Tư",
    "tienphong.vn": "Báo Tiền Phong",
    "laodong.vn": "Báo Lao Động",
    "doanhnhansaigon.vn": "Doanh Nhân Sài Gòn",
    "congly.vn": "Báo Công Lý",
    "sggp.org.vn": "Báo Sài Gòn Giải Phóng",
    "nhandan.vn": "Báo Nhân Dân",
    "bnews.vn": "Bnews - TTXVN",
    "znews.vn": "Tri Thức - Znews",
    "tapchitaichinh.vn": "Tạp chí Tài chính",
    "dttc.sggp.org.vn": "Đầu Tư Tài Chính",
    "vcci.com.vn": "Liên đoàn Thương mại & Công nghiệp VN (VCCI)",
    "dangcongsan.vn": "Báo điện tử Đảng Cộng sản VN",
    "chinhphu.vn": "Cổng Thông tin điện tử Chính phủ",
    "vi.wikipedia.org": "Wikipedia Tiếng Việt",
}


def detect_publisher(url: str, default_name: str = "") -> str:
    """Xác định cơ quan báo chí / cổng thông tin từ URL."""
    try:
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        for known_domain, pub_name in DOMAIN_PUBLISHERS.items():
            if domain == known_domain or domain.endswith("." + known_domain):
                return pub_name
        return default_name or domain or "Báo chí"
    except Exception:
        return default_name or "Báo chí"


def is_safe_url(url: str) -> tuple[bool, str]:
    """Kiểm tra URL an toàn, chống SSRF (chặn dải IP nội bộ, loopback, cloud metadata)."""
    if not url:
        return False, "Đường dẫn trống."
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"URL không hợp lệ: {e}"
    if parsed.scheme not in ("http", "https"):
        return False, "Chỉ chấp nhận giao thức HTTP hoặc HTTPS."
    hostname = (parsed.hostname or "").lower().strip()
    if not hostname:
        return False, "Đường dẫn không có tên miền hợp lệ."
    if (hostname in ("localhost", "127.0.0.1", "0.0.0.0", "metadata.google.internal")
            or hostname.endswith(".local") or hostname.endswith(".internal")
            or hostname.endswith(".localhost")):
        return False, "Không được phép truy cập tên miền hoặc địa chỉ nội bộ."
    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except Exception as e:
        return False, f"Không thể phân giải tên miền: {e}"

    for item in addr_info:
        ip_str = item[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
            if (ip.is_private or ip.is_loopback or ip.is_link_local
                    or ip.is_reserved or ip.is_multicast or ip_str == "169.254.169.254"):
                return False, f"Địa chỉ IP ({ip_str}) thuộc mạng nội bộ hoặc không an toàn."
        except ValueError:
            return False, "Địa chỉ IP không hợp lệ."
    return True, ""


def clean_html_to_text(html: str) -> dict:
    """Loại bỏ thẻ rác (script, style, ads, nav, footer) và lấy nội dung bài viết sạch."""
    title = ""
    # Tìm title hoặc og:title
    m_og_title = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
    if m_og_title:
        title = m_og_title.group(1).strip()
    else:
        m_title = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.DOTALL)
        if m_title:
            title = re.sub(r'\s+', ' ', m_title.group(1)).strip()

    # Tìm og:site_name
    site_name = ""
    m_site = re.search(r'<meta[^>]+property=["\']og:site_name["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
    if m_site:
        site_name = m_site.group(1).strip()

    # Bóc tách ngày xuất bản nếu có
    pub_date = ""
    m_date = re.search(r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
    if m_date:
        pub_date = m_date.group(1).strip()[:10]

    # Tìm ảnh đại diện bài viết (og:image, twitter:image)
    image_url = ""
    m_img = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
    if not m_img:
        m_img = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html, re.I)
    if not m_img:
        m_img = re.search(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
    if not m_img:
        m_img = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image["\']', html, re.I)
    if m_img:
        image_url = m_img.group(1).strip()

    # Loại bỏ các khối không liên quan
    text = re.sub(r'<(script|style|header|footer|nav|aside|noscript|svg|iframe)[^>]*>.*?</\1>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    # Loại bỏ các khối comment, share, quảng cáo phổ biến
    text = re.sub(r'<div[^>]+class=["\'][^"\']*(comment|share|social|advert|banner|sidebar|relate)[^"\']*["\'][^>]*>.*?</div\s*>', ' ', text, flags=re.DOTALL | re.IGNORECASE)

    # Giữ cấu trúc đoạn văn
    text = re.sub(r'</?(p|h[1-6]|li|article|section|blockquote|br)[^>]*>', '\n', text, flags=re.IGNORECASE)

    # Dùng nh3 để gỡ toàn bộ thẻ html còn lại một cách an toàn
    cleaned = nh3.clean(text, tags=set())
    # Chuẩn hóa khoảng trắng và dòng trống
    lines = [line.strip() for line in cleaned.splitlines()]
    clean_text = "\n".join(l for l in lines if l)
    clean_text = re.sub(r'\n{3,}', '\n\n', clean_text).strip()

    return {
        "title": title,
        "site_name": site_name,
        "published_on": pub_date,
        "image_url": image_url,
        "text": clean_text[:12000],  # Giới hạn 12.000 ký tự an toàn cho AI
    }


def fetch_article(url_or_text: str) -> dict:
    """Tải bài viết từ URL hoặc nhận trực tiếp văn bản được admin dán vào."""
    url_or_text = url_or_text.strip()
    is_url = url_or_text.startswith("http://") or url_or_text.startswith("https://")

    if not is_url:
        # Admin dán trực tiếp bài viết dạng text
        lines = [line.strip() for line in url_or_text.splitlines() if line.strip()]
        first_line = lines[0] if lines else "Tài liệu văn bản"
        return {
            "is_url": False,
            "url": "",
            "title": first_line[:150],
            "publisher": "Tài liệu nội bộ / Báo chí",
            "published_on": "",
            "text": url_or_text[:12000],
        }

    # Admin nhập URL - Kiểm tra an toàn chống SSRF
    safe, reason = is_safe_url(url_or_text)
    if not safe:
        raise ValueError(f"Đường dẫn không hợp lệ hoặc bị chặn vì lý do bảo mật: {reason}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
    }
    resp = requests.get(url_or_text, headers=headers, timeout=12)
    resp.raise_for_status()

    # Nhận diện encoding chuẩn tiếng Việt
    if resp.encoding is None or resp.encoding == 'ISO-8859-1':
        resp.encoding = resp.apparent_encoding or 'utf-8'

    parsed = clean_html_to_text(resp.text)
    publisher = detect_publisher(url_or_text, parsed.get("site_name"))

    raw_img = parsed.get("image_url", "")
    if raw_img and not (raw_img.startswith("http://") or raw_img.startswith("https://")):
        from urllib.parse import urljoin
        raw_img = urljoin(url_or_text, raw_img)

    return {
        "is_url": True,
        "url": url_or_text,
        "title": parsed["title"],
        "publisher": publisher,
        "published_on": parsed.get("published_on", ""),
        "image_url": raw_img,
        "text": parsed["text"],
    }


def find_matching_province(name_or_text: str):
    """Tìm đối tượng Province phù hợp theo tên."""
    if not name_or_text:
        return None
    name_norm = normalize(name_or_text).strip()
    # Tìm trực tiếp
    p = Province.objects.filter(name__iexact=name_or_text.strip()).first()
    if p:
        return p
    # Tìm theo normalize
    for prov in Province.objects.all():
        pn = normalize(prov.name)
        if pn in name_norm or name_norm in pn:
            return prov
    return None


def find_matching_sector(name_or_text: str):
    """Tìm đối tượng Sector phù hợp theo tên hoặc mã ngành."""
    if not name_or_text:
        return None
    name_norm = normalize(name_or_text).strip()
    s = Sector.objects.filter(name__iexact=name_or_text.strip()).first()
    if s:
        return s
    for sec in Sector.objects.all():
        sn = normalize(sec.name)
        if sn in name_norm or name_norm in sn:
            return sec
    return None


AI_EXTRACTION_SYSTEM_PROMPT = """Bạn là Trưởng Ban Biên tập cấp cao kiêm Chuyên gia Phân tích Dữ liệu của Bách khoa toàn thư doanhnhan.wiki.
Nhiệm vụ của bạn là đọc kỹ toàn bộ văn bản bài báo được cung cấp, sau đó BIÊN TẬP VÀ VIẾT LẠI thành hồ sơ bách khoa thư CHUẨN MỰC, GIÀU CHI TIẾT, HẤP DẪN VÀ ĐẦY ĐỦ THÔNG TIN NHẤT.

TIÊU CHUẨN VIẾT BÀI ĐẲNG CẤP ("VIẾT HAY & ĐẦY ĐỦ THÔNG TIN"):
1. VĂN PHONG BÁCH KHOA TRANG TRỌNG & CUỐN HÚT:
   - Viết bằng tiếng Việt trong sáng, điềm đạm, trang trọng như phong cách kết hợp giữa Wikipedia và Tạp chí Forbes / Harvard Business Review.
   - Tuyệt đối LOẠI BỎ văn phong quảng cáo PR thô thiển, tâng bốc vô căn cứ ("số 1 thế giới", "đỉnh cao", "siêu nhân").
   - Thay vào đó, tôn vinh nhân vật và doanh nghiệp bằng SỰ THẬT, TƯ DUY CHIẾN LƯỢC, BẢN LĨNH VƯỢT KHÓ và CÁC THÀNH TỰU ĐO ĐẾM ĐƯỢC.
   - Câu từ mạch lạc, giàu sức gợi cảm, ngắt đoạn tự nhiên, liên kết ý logic.

2. ĐỘ ĐẦY ĐỦ VÀ CHIỀU SÂU THÔNG TIN (TUYỆT ĐỐI KHÔNG TÓM TẮT QUA LOA):
   - Đoạn tóm tắt (summary): 3-4 câu sắc sảo, khắc họa rõ vị thế, tầm vóc và dấu ấn đậm nét nhất.
   - Đoạn hành trình (journey) & Giới thiệu tổng quan (overview): Phải viết thành các đoạn văn hoàn chỉnh, chi tiết và có chiều sâu. Giữ trọn vẹn mọi số liệu tài chính, mốc thời gian, tên công nghệ, dự án, chứng nhận chất lượng quốc tế (như Level 1 Australia, FDA, ISO...), đối tác lớn và bước ngoặt kinh doanh.
   - Dấu mốc sự nghiệp (milestones): Bóc tách tối đa TẤT CẢ các mốc thời gian (năm/tháng) có trong bài báo, ghi rõ sự kiện cụ thể.
   - Triết lý kinh doanh (philosophy): Trích dẫn hoặc đúc kết những câu nói tâm đắc, bài học quản trị sâu sắc nếu bài báo có nhắc đến.

3. NGUYÊN TẮC TRUNG THỰC VỚI NGUỒN TIN:
   - Tất cả sự kiện, số liệu, năm sinh, mã số thuế, địa danh PHẢI CÓ THẬT trong bài báo. Tuyệt đối không bịa đặt số liệu tài chính hay ngày tháng nếu bài báo không có.
   - Nếu trường nào không có thông tin, hãy để giá trị null hoặc chuỗi rỗng "".

SCHEMA JSON CẦN TRẢ VỀ DUY NHẤT (Không kèm lời dẫn):
{
  "has_person": true (hoặc false nếu bài thuần túy về công ty/sản phẩm),
  "person": {
    "full_name": "Họ và tên doanh nhân (viết hoa chuẩn)",
    "headline": "Dòng chức danh ngắn gọn, trang trọng",
    "gender": "male" hoặc "female" hoặc "other",
    "birth_year": 1985 (số nguyên hoặc null),
    "hometown": "Tên tỉnh/thành quê quán hoặc null",
    "current_province": "Tên tỉnh/thành hoạt động chính hoặc null",
    "education": "Trường lớp, bằng cấp hoặc null",
    "summary": "Đoạn văn tóm tắt 3-4 câu sắc sảo, trang trọng, khái quát tầm vóc nhân vật",
    "biography": "Đoạn văn tiểu sử, xuất thân, quá trình học tập và khởi đầu sự nghiệp",
    "journey": "Đoạn văn hành trình khởi nghiệp, vượt qua thử thách, bước ngoặt chiến lược và thành tựu thương trường",
    "philosophy": "Triết lý kinh doanh, quan điểm sống hoặc bài học quản trị tâm đắc",
    "milestones": [
      {"year": 2018, "title": "Chi tiết dấu mốc sự nghiệp...", "kind": "founding"},
      {"year": 2024, "title": "Chi tiết giải thưởng / thành tựu...", "kind": "award"}
    ]
  },
  "has_company": true (hoặc false nếu bài chỉ viết về nhân vật độc lập),
  "company": {
    "legal_name": "Tên pháp lý đầy đủ theo ĐKKD",
    "brand_name": "Tên thương hiệu ngắn gọn / Tên viết tắt (ví dụ: PVCFC, Masan, THACO...)",
    "tax_code": "Mã số thuế (nếu có, không có thì null)",
    "founded_year": 2011 (số nguyên hoặc null),
    "province": "Tên tỉnh thành trụ sở hoặc null",
    "address": "Địa chỉ trụ sở nếu có hoặc null",
    "website": "https://... hoặc null",
    "sector": "Tên ngành nghề/lĩnh vực hoạt động chính",
    "size_band": "lt10" hoặc "10_50" hoặc "50_200" hoặc "gt200" hoặc null,
    "overview": "Đoạn văn giới thiệu toàn diện 2-3 đoạn về năng lực, vị thế thị trường, quy mô sản xuất, chuỗi cung ứng và thành tựu xuất khẩu của doanh nghiệp",
    "products": ["Sản phẩm / Dịch vụ 1", "Sản phẩm 2"]
  },
  "relationship": {
    "role": "founder_ceo" hoặc "founder" hoặc "ceo" hoặc "chair" hoặc "executive",
    "title": "Chức danh cụ thể hiển thị",
    "start_year": 2018 (hoặc null)
  },
  "story": {
    "title": "Tiêu đề bài viết hấp dẫn, trang trọng, chuẩn mực báo chí kinh tế",
    "story_type": "portrait" hoặc "journey" hoặc "case_study" hoặc "event" hoặc "insight",
    "summary": "Đoạn sa-pô mở đầu (2-3 câu khái quát bối cảnh, khơi gợi và tóm lược cốt lõi)",
    "content_md": "Toàn bộ bài viết chuyên sâu dạng Markdown (có tiêu đề mục ##, trích dẫn, câu chuyện, số liệu, bài học). \n\nLƯU Ý BẮT BUỘC: Cuối bài viết PHẢI CÓ đoạn trích dẫn nguồn gốc theo mẫu:\n\n---\n> 📌 **Nguồn bài viết gốc:** [Tiêu đề bài báo](URL) — Phát hành bởi **[Tên cơ quan báo chí]**.\n> *Bản quyền nội dung thuộc về tác giả và cơ quan báo chí phát hành. Doanhnhan.wiki trích dẫn và biên tập phục vụ mục đích thông tin và học thuật.*"
  },
  "source": {
    "title": "Tiêu đề bài viết gốc",
    "publisher": "Tên cơ quan báo chí",
    "published_on": "YYYY-MM-DD hoặc null"
  }
}
"""


def _fallback_rule_based_extraction(article_data: dict, hints: str = "") -> dict:
    """Engine bóc tách dữ liệu nội bộ nâng cao (hoạt động thông minh ngay cả khi chưa có API Key)."""
    text = article_data.get("text", "")
    title = article_data.get("title", "")
    combined = f"{title}\n\n{text}"

    # 1. Tìm tên công ty & thương hiệu
    company_name = ""
    brand_name = ""
    # Tìm tên có tiền tố pháp lý
    m_comp = re.search(r'((?:Tổng công ty|Tập đoàn|Công ty)\s+(?:Cổ phần|TNHH|Trách nhiệm hữu hạn)?\s*[A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-&]{3,60}?)(?=[,\.\(\n\r]|\s+(?:do|được|có|là|vừa|đang))', combined)
    if m_comp:
        company_name = m_comp.group(1).strip()
        # Tìm thương hiệu viết tắt trong ngoặc đơn ngay sau tên công ty (ví dụ: (PVCFC), (THACO), (FPT)...)
        m_brand = re.search(re.escape(company_name) + r'\s*\(([A-Z0-9\.\-&]{2,15})\)', combined)
        if m_brand:
            brand_name = m_brand.group(1).strip()

    if not company_name and "công ty" in title.lower():
        m_t_comp = re.search(r'((?:Tổng công ty|Tập đoàn|Công ty)\s+[A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-&]{3,50})', title)
        if m_t_comp:
            company_name = m_t_comp.group(1).strip()

    # 2. Tìm tên doanh nhân thực tế (chỉ khi có người thật, tuyệt đối không tạo người mẫu)
    person_name = ""
    if hints:
        # Nếu gợi ý là tên người (không chứa công ty/tập đoàn)
        if not re.search(r'(?:công ty|tập đoàn|tổng công ty)', hints, re.I):
            person_name = hints.strip()
    if not person_name:
        m_name = re.search(r'(?:ông|bà|doanh nhân|anh|chị)\s+([A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+){1,3})', combined, re.I)
        if m_name:
            candidate = m_name.group(1).strip()
            # Loại bỏ nếu nhầm với địa danh/cơ quan
            if candidate not in ["Việt Nam", "Australia", "Hà Nội", "Hồ Chí Minh", "Cà Mau", "Bộ Nông"]:
                person_name = candidate

    # 3. Tìm mã số thuế
    tax_code = ""
    m_tax = re.search(r'(?:MST|mã số thuế|mã doanh nghiệp)[:\s]*([0-9]{10}(?:-[0-9]{3})?)', combined, re.I)
    if m_tax:
        tax_code = m_tax.group(1).strip()

    # 4. Tìm năm thành lập
    founded_year = None
    m_found = re.search(r'(?:thành lập|ra đời|khởi sự|thành lập năm)[^\d]*([12][90]\d{2})', combined, re.I)
    if m_found:
        founded_year = int(m_found.group(1))

    # 5. Tìm tỉnh thành
    province_name = None
    if company_name:
        prov = find_matching_province(company_name)
        if prov:
            province_name = prov.name
    if not province_name:
        for p in Province.objects.all():
            if p.name in title or f"tại {p.name}" in text or f"ở {p.name}" in text:
                province_name = p.name
                break

    # 6. Tìm ngành nghề từ từ khóa
    sector_name = None
    text_lower = combined.lower()
    if any(k in text_lower for k in ["phân bón", "urê", "npk", "nông nghiệp", "thủy sản", "lúa", "cây trồng"]):
        s_obj = Sector.objects.filter(name__icontains="nông").first()
        if s_obj:
            sector_name = s_obj.name
    elif any(k in text_lower for k in ["công nghệ", "phần mềm", "ai", "chuyển đổi số"]):
        s_obj = Sector.objects.filter(name__icontains="công nghệ").first()
        if s_obj:
            sector_name = s_obj.name
    elif any(k in text_lower for k in ["bất động sản", "đô thị", "xây dựng", "dự án"]):
        s_obj = Sector.objects.filter(name__icontains="bất động sản").first()
        if s_obj:
            sector_name = s_obj.name

    # 7. Bóc tách nội dung tóm tắt thật từ các đoạn văn của bài báo
    raw_paras = [p.strip() for p in text.splitlines() if len(p.strip()) > 35]
    # Bỏ qua đoạn trùng tiêu đề
    clean_paras = [p for p in raw_paras if p.lower() not in title.lower()]
    real_overview = "\n\n".join(clean_paras[:3]) if clean_paras else (text[:600] if text else "")

    # 8. Bóc tách mốc thời gian thực tế
    milestones = []
    for m in re.finditer(r'(?:năm\s+|tháng\s+\d+[\s/]+(?:năm\s+)?|ngày\s+\d+[\s/]+\d+[\s/]+)([12][90]\d{2})[,\s:]+([^\.\n]{15,140})', combined, re.I):
        try:
            yr = int(m.group(1))
            ms_title = m.group(2).strip()
            ms_title = re.sub(r'^[,\s\-:]+', '', ms_title).strip()
            if ms_title and len(ms_title) >= 10 and not any(ms["title"] == ms_title for ms in milestones):
                milestones.append({"year": yr, "title": ms_title, "kind": "award" if ("công nhận" in ms_title.lower() or "giải" in ms_title.lower()) else "product"})
        except Exception:
            pass
    milestones = milestones[:5]

    has_person = bool(person_name)
    has_company = bool(company_name)

    return {
        "has_person": has_person,
        "person": {
            "full_name": person_name,
            "headline": f"Đại diện lãnh đạo {company_name}" if (person_name and company_name) else "",
            "gender": "male",
            "birth_year": None,
            "hometown": None,
            "current_province": province_name,
            "education": None,
            "summary": clean_paras[0] if (has_person and clean_paras) else "",
            "biography": "",
            "journey": clean_paras[1] if (has_person and len(clean_paras) > 1) else "",
            "philosophy": "",
            "milestones": milestones if has_person else [],
        },
        "has_company": has_company,
        "company": {
            "legal_name": company_name or "Doanh nghiệp",
            "brand_name": brand_name,
            "tax_code": tax_code or None,
            "founded_year": founded_year,
            "province": province_name,
            "address": "",
            "website": "",
            "sector": sector_name or "",
            "size_band": None,
            "overview": real_overview,
            "products": [],
        },
        "relationship": {
            "role": "founder_ceo",
            "title": "Chủ tịch / Tổng Giám đốc",
            "start_year": founded_year,
        },
        "story": {
            "title": article_data.get("title", ""),
            "story_type": "portrait" if has_person else ("journey" if has_company else "portrait"),
            "summary": clean_paras[0] if clean_paras else article_data.get("title", ""),
            "content_md": "\n\n".join(clean_paras[:5]) if clean_paras else text[:2500],
        },
        "source": {
            "title": article_data.get("title", ""),
            "publisher": article_data.get("publisher", "Báo chí"),
            "published_on": article_data.get("published_on", ""),
        }
    }


def extract_entities_with_ai(article_data: dict, hints: str = "") -> dict:
    """Sử dụng Google Gemini AI để trích xuất dữ liệu có cấu trúc từ bài viết."""
    cfg = get_ai_config()
    api_key = cfg["api_key"]
    model_name = cfg["model"]

    article_text = article_data.get("text", "")
    title = article_data.get("title", "")
    url = article_data.get("url", "")
    publisher = article_data.get("publisher", "")

    user_prompt = (
        f"TIÊU ĐỀ BÀI BÁO: {title}\n"
        f"NGUỒN / CƠ QUAN XUẤT BẢN: {publisher}\n"
        f"ĐƯỜNG DẪN URL: {url}\n"
    )
    if hints:
        user_prompt += f"GỢI Ý / ĐỐI TƯỢNG TRỌNG TÂM CỦA ADMIN: {hints}\n"
    user_prompt += f"\nNỘI DUNG VĂN BẢN BÀI BÁO CẦN PHÂN TÍCH:\n{article_text}\n"

    parsed_result = None

    if api_key:
        try:
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            payload = {
                "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                "systemInstruction": {"parts": [{"text": AI_EXTRACTION_SYSTEM_PROMPT}]},
                "generationConfig": {
                    "temperature": 0.2,  # Thấp để giữ tính khách quan cao nhất
                    "maxOutputTokens": 3000,
                    "responseMimeType": "application/json",
                }
            }
            resp = requests.post(gemini_url, json=payload, timeout=25)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                raw_reply = "".join(p.get("text", "") for p in candidates[0].get("content", {}).get("parts", []))
                # Gỡ bỏ code block nếu có
                clean_json_str = re.sub(r'^```(?:json)?\s*', '', raw_reply.strip())
                clean_json_str = re.sub(r'\s*```$', '', clean_json_str.strip())
                parsed_result = json.loads(clean_json_str)
        except Exception as exc:
            logger.warning("Lỗi gọi Gemini API bóc tách dữ liệu: %s — Sử dụng Engine dự phòng", exc)

    if not parsed_result:
        parsed_result = _fallback_rule_based_extraction(article_data, hints)

    # Đảm bảo source có đủ dữ liệu từ bài viết gốc
    if "source" not in parsed_result:
        parsed_result["source"] = {}
    parsed_result["source"]["url"] = url
    if not parsed_result["source"].get("title"):
        parsed_result["source"]["title"] = title
    if not parsed_result["source"].get("publisher"):
        parsed_result["source"]["publisher"] = publisher
    if article_data.get("published_on") and not parsed_result["source"].get("published_on"):
        parsed_result["source"]["published_on"] = article_data["published_on"]

    # Đảm bảo khối story bài viết hoàn chỉnh và BẮT BUỘC DẪN NGUỒN RÕ RÀNG
    if "story" not in parsed_result or not isinstance(parsed_result["story"], dict):
        parsed_result["story"] = {}
    story_dict = parsed_result["story"]
    if not story_dict.get("title"):
        story_dict["title"] = title or "Câu chuyện doanh nhân"
    if not story_dict.get("story_type"):
        story_dict["story_type"] = "portrait" if parsed_result.get("has_person") else ("journey" if parsed_result.get("has_company") else "portrait")

    person_data = parsed_result.get("person", {}) or {}
    comp_data = parsed_result.get("company", {}) or {}

    if not story_dict.get("summary"):
        story_dict["summary"] = (person_data.get("summary") or comp_data.get("overview") or article_text[:300])[:350]

    s_content = (story_dict.get("content_md") or "").strip()
    if not s_content:
        parts = []
        if person_data.get("journey"):
            parts.append(f"## Hành trình & Dấu ấn sự nghiệp\n\n{person_data['journey']}")
        if comp_data.get("overview"):
            parts.append(f"## Năng lực & Vị thế trên thương trường\n\n{comp_data['overview']}")
        if person_data.get("philosophy"):
            parts.append(f"## Triết lý kinh doanh & Bản lĩnh doanh nhân\n\n{person_data['philosophy']}")
        s_content = "\n\n".join(parts) if parts else (story_dict["summary"] or article_text[:2500])

    # Luôn đính kèm khối trích dẫn nguồn chuẩn báo chí vào cuối bài viết
    if url and url not in s_content:
        citation_box = (
            f"\n\n---\n\n"
            f"> 📌 **Nguồn bài viết gốc:** [{title}]({url})  \n"
            f"> **Cơ quan phát hành:** {publisher or 'Báo chí'}  \n"
            f"> *Bản quyền nội dung và hình ảnh thuộc về tác giả và cơ quan báo chí phát hành. "
            f"Bách khoa Doanh nhân (doanhnhan.wiki) trích dẫn và biên tập phục vụ mục đích thông tin và học thuật.*"
        )
        s_content += citation_box
    story_dict["content_md"] = s_content

    # Tra cứu đối soát xem đã có trùng lặp trong hệ thống chưa
    person_data = parsed_result.get("person", {})
    comp_data = parsed_result.get("company", {})

    existing_person = None
    if person_data and person_data.get("full_name"):
        existing_person = Person.objects.filter(full_name__iexact=person_data["full_name"].strip()).first()
        if not existing_person:
            # Tra cứu mờ
            p_norm = normalize(person_data["full_name"])
            existing_person = Person.objects.filter(search_text__icontains=p_norm).first()

    existing_company = None
    if comp_data:
        tax = (comp_data.get("tax_code") or "").strip()
        if tax and TAX_CODE_RE.match(tax):
            existing_company = Company.objects.filter(tax_code=tax).first()
        if not existing_company and comp_data.get("legal_name"):
            existing_company = Company.objects.filter(legal_name__iexact=comp_data["legal_name"].strip()).first()
        if not existing_company and comp_data.get("brand_name"):
            existing_company = Company.objects.filter(brand_name__iexact=comp_data["brand_name"].strip()).first()

    # Khớp Province và Sector
    if person_data.get("hometown"):
        prov_obj = find_matching_province(person_data["hometown"])
        person_data["hometown_id"] = prov_obj.pk if prov_obj else None
    if person_data.get("current_province"):
        prov_obj = find_matching_province(person_data["current_province"])
        person_data["current_province_id"] = prov_obj.pk if prov_obj else None

    if comp_data.get("province"):
        prov_obj = find_matching_province(comp_data["province"])
        comp_data["province_id"] = prov_obj.pk if prov_obj else None
    if comp_data.get("sector"):
        sec_obj = find_matching_sector(comp_data["sector"])
        comp_data["primary_sector_id"] = sec_obj.pk if sec_obj else None

    parsed_result["duplicates"] = {
        "person": {
            "id": existing_person.pk if existing_person else None,
            "name": existing_person.full_name if existing_person else None,
            "url": existing_person.get_absolute_url() if existing_person else None,
        } if existing_person else None,
        "company": {
            "id": existing_company.pk if existing_company else None,
            "name": existing_company.display_name if existing_company else None,
            "tax_code": existing_company.tax_code if existing_company else None,
            "url": existing_company.get_absolute_url() if existing_company else None,
        } if existing_company else None,
    }

    return parsed_result


@transaction.atomic
def save_crawled_data(post_data: dict, user) -> dict:
    """Lưu dữ liệu Doanh nhân & Doanh nghiệp đã được AI bóc tách và Admin phê duyệt."""
    def _clean(val, default="") -> str:
        if val is None:
            return default
        return str(val).strip()

    save_person = post_data.get("save_person") in ("1", "true", "on", True)
    save_company = post_data.get("save_company") in ("1", "true", "on", True)
    status_choice = post_data.get("status", Status.DRAFT)
    if status_choice not in Status.values:
        status_choice = Status.DRAFT

    person_obj = None
    company_obj = None
    created_person = False
    created_company = False

    source_title = _clean(post_data.get("source_title")) or "Bài báo giới thiệu"
    source_url = _clean(post_data.get("source_url"))
    source_pub = _clean(post_data.get("source_publisher")) or "Báo chí"

    # 1. Lưu Doanh nhân
    p_name = _clean(post_data.get("person_full_name"))
    if save_person and p_name:
        person_id = post_data.get("person_id")
        if person_id and str(person_id).isdigit():
            person_obj = Person.objects.filter(pk=int(person_id)).first()

        if not person_obj:
            person_obj = Person(full_name=p_name)
            created_person = True

        person_obj.full_name = p_name
        person_obj.headline = _clean(post_data.get("person_headline"))
        if post_data.get("person_birth_year") and str(post_data["person_birth_year"]).isdigit():
            person_obj.birth_year = int(post_data["person_birth_year"])
        if post_data.get("person_hometown_id") and str(post_data["person_hometown_id"]).isdigit():
            person_obj.hometown_id = int(post_data["person_hometown_id"])
        if post_data.get("person_current_province_id") and str(post_data["person_current_province_id"]).isdigit():
            person_obj.current_province_id = int(post_data["person_current_province_id"])

        person_obj.status = status_choice
        if status_choice == Status.PUBLISHED and not person_obj.published_at:
            person_obj.published_at = timezone.now()
        person_obj.save()

        # Không tự động tải ảnh mạng không rõ bản quyền. Chỉ tải nếu biên tập viên chủ động chọn và URL an toàn.
        download_portrait = post_data.get("download_portrait") in ("1", "true", "on", True)
        image_url = _clean(post_data.get("image_url") or post_data.get("person_image_url"))
        if download_portrait and image_url and (created_person or not person_obj.portrait):
            safe_img, _ = is_safe_url(image_url)
            if safe_img:
                try:
                    img_headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                        "Referer": source_url or "https://google.com",
                    }
                    img_resp = requests.get(image_url, headers=img_headers, timeout=10)
                    if img_resp.status_code == 200 and len(img_resp.content) > 1024:
                        ct = img_resp.headers.get("content-type", "").lower()
                        ext = "jpg"
                        if "png" in ct:
                            ext = "png"
                        elif "webp" in ct:
                            ext = "webp"
                        fname = f"{person_obj.slug or 'person'}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                        person_obj.portrait.save(fname, ContentFile(img_resp.content), save=True)
                except Exception as img_err:
                    logger.warning("Không thể tải ảnh chân dung tự động từ %s: %s", image_url, img_err)

        # Lưu các phần bài viết (ArticleSection)
        sections = [
            ("summary", _clean(post_data.get("person_summary")), 0),
            ("biography", _clean(post_data.get("person_biography")), 1),
            ("journey", _clean(post_data.get("person_journey")), 2),
            ("philosophy", _clean(post_data.get("person_philosophy")), 3),
        ]
        for key, body, s_order in sections:
            if body:
                ArticleSection.objects.update_or_create(
                    person=person_obj, key=key,
                    defaults={"body_md": body, "word_count": word_count(body), "sort_order": s_order}
                )

        # Lưu nguồn (Source)
        if source_url:
            Source.objects.get_or_create(
                person=person_obj, url=source_url,
                defaults={"title": source_title, "kind": Source.Kind.PRESS}
            )

        # Lưu mốc thời gian (Milestones)
        milestone_years = post_data.getlist("milestone_year") if hasattr(post_data, "getlist") else []
        milestone_titles = post_data.getlist("milestone_title") if hasattr(post_data, "getlist") else []
        milestone_kinds = post_data.getlist("milestone_kind") if hasattr(post_data, "getlist") else []

        for yr, m_title, m_kind in zip(milestone_years, milestone_titles, milestone_kinds):
            if yr and str(yr).isdigit() and _clean(m_title):
                Milestone.objects.create(
                    person=person_obj,
                    year=int(yr),
                    title=_clean(m_title),
                    kind=m_kind if m_kind in Milestone.Kind.values else Milestone.Kind.OTHER,
                    source_url=source_url,
                )

    # 2. Lưu Doanh nghiệp
    c_legal = _clean(post_data.get("company_legal_name"))
    c_brand = _clean(post_data.get("company_brand_name"))
    c_name = c_legal or c_brand
    if save_company and c_name:
        company_id = post_data.get("company_id")
        tax = _clean(post_data.get("company_tax_code"))

        if company_id and str(company_id).isdigit():
            company_obj = Company.objects.filter(pk=int(company_id)).first()

        if not company_obj and tax and TAX_CODE_RE.match(tax):
            company_obj = Company.objects.filter(tax_code=tax).first()

        if not company_obj and c_legal:
            company_obj = Company.objects.filter(legal_name__iexact=c_legal).first()

        if not company_obj and c_brand:
            company_obj = Company.objects.filter(brand_name__iexact=c_brand).first()

        if not company_obj:
            company_obj = Company(legal_name=c_name)
            created_company = True

        company_obj.legal_name = c_name
        company_obj.brand_name = c_brand
        if tax and TAX_CODE_RE.match(tax):
            if not Company.objects.filter(tax_code=tax).exclude(pk=company_obj.pk).exists():
                company_obj.tax_code = tax

        if post_data.get("company_founded_year") and str(post_data["company_founded_year"]).isdigit():
            company_obj.founded_year = int(post_data["company_founded_year"])
        if post_data.get("company_province_id") and str(post_data["company_province_id"]).isdigit():
            company_obj.province_id = int(post_data["company_province_id"])
        if post_data.get("company_primary_sector_id") and str(post_data["company_primary_sector_id"]).isdigit():
            company_obj.primary_sector_id = int(post_data["company_primary_sector_id"])

        company_obj.address = _clean(post_data.get("company_address"))
        company_obj.website = _clean(post_data.get("company_website"))
        company_obj.size_band = _clean(post_data.get("company_size_band"))
        company_obj.short_intro = _clean(post_data.get("company_overview"))[:500]
        company_obj.status = status_choice
        company_obj.save()

        # Tự động tải ảnh/logo cho công ty nếu không có người và có ảnh bài báo
        image_url = _clean(post_data.get("image_url") or post_data.get("person_image_url"))
        if image_url and not person_obj and (created_company or not company_obj.logo):
            try:
                img_headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Referer": source_url or "https://google.com",
                }
                img_resp = requests.get(image_url, headers=img_headers, timeout=10)
                if img_resp.status_code == 200 and len(img_resp.content) > 1024:
                    ct = img_resp.headers.get("content-type", "").lower()
                    ext = "jpg"
                    if "png" in ct:
                        ext = "png"
                    elif "webp" in ct:
                        ext = "webp"
                    fname = f"{company_obj.slug or 'company'}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                    company_obj.logo.save(fname, ContentFile(img_resp.content), save=True)
            except Exception as img_err:
                logger.warning("Không thể tải logo công ty tự động từ %s: %s", image_url, img_err)

        # Lưu nội dung chi tiết công ty
        c_overview = _clean(post_data.get("company_overview"))
        if c_overview:
            ArticleSection.objects.update_or_create(
                company=company_obj, key="overview",
                defaults={"body_md": c_overview, "word_count": word_count(c_overview), "sort_order": 0}
            )

        # Lưu nguồn (Source)
        if source_url:
            Source.objects.get_or_create(
                company=company_obj, url=source_url,
                defaults={"title": source_title, "kind": Source.Kind.PRESS}
            )

    # 3. Tạo liên kết Doanh nhân ⟷ Doanh nghiệp
    if person_obj and company_obj:
        role_choice = post_data.get("relationship_role", "founder_ceo")
        if role_choice not in PersonCompany.Role.values:
            role_choice = "founder_ceo"
        title_custom = _clean(post_data.get("relationship_title")) or "Chủ tịch / Giám đốc"
        start_yr = None
        if post_data.get("relationship_start_year") and str(post_data["relationship_start_year"]).isdigit():
            start_yr = int(post_data["relationship_start_year"])

        PersonCompany.objects.update_or_create(
            person=person_obj, company=company_obj, role=role_choice,
            defaults={"title": title_custom, "start_year": start_yr, "is_primary": True}
        )

    # 4. Lưu / Đăng bài viết (Story) - Lên bài ngay với trích dẫn nguồn đầy đủ
    story_obj = None
    created_story = False
    save_story = post_data.get("save_story") in ("1", 1, True, "true", "on") or post_data.get("create_story") in ("1", 1, True, "true", "on")
    story_title = _clean(post_data.get("story_title")) or source_title

    # Mặc định: Nếu có tiêu đề và URL nguồn thì luôn lưu bài viết Story
    if (save_story or post_data.get("auto_publish") in ("1", 1, True, "true")) and story_title:
        story_id = post_data.get("story_id")
        if story_id and str(story_id).isdigit():
            story_obj = Story.objects.filter(pk=int(story_id)).first()

        # Kiểm tra trùng bài qua URL nguồn gốc
        if not story_obj and source_url:
            story_obj = Story.objects.filter(source_url=source_url).first()

        if not story_obj:
            story_obj = Story(title=story_title)
            created_story = True

        story_obj.title = story_title
        story_type = _clean(post_data.get("story_type"))
        if story_type in Story.StoryType.values:
            story_obj.story_type = story_type
        elif person_obj:
            story_obj.story_type = Story.StoryType.PORTRAIT
        elif company_obj:
            story_obj.story_type = Story.StoryType.JOURNEY
        else:
            story_obj.story_type = Story.StoryType.PORTRAIT

        story_obj.summary = _clean(post_data.get("story_summary")) or _clean(post_data.get("person_summary")) or _clean(post_data.get("company_overview"))[:300]

        # Nội dung markdown bài viết có kèm khối dẫn nguồn trang trọng
        content_md = _clean(post_data.get("story_content_md"))
        if not content_md:
            parts = []
            if person_obj and post_data.get("person_journey"):
                parts.append(f"## Hành trình & Dấu ấn sự nghiệp\n\n{post_data['person_journey']}")
            if company_obj and post_data.get("company_overview"):
                parts.append(f"## Năng lực & Vị thế trên thương trường\n\n{post_data['company_overview']}")
            if person_obj and post_data.get("person_philosophy"):
                parts.append(f"## Triết lý kinh doanh & Bản lĩnh doanh nhân\n\n{post_data['person_philosophy']}")
            content_md = "\n\n".join(parts) if parts else (story_obj.summary or story_title)

        # BẮT BUỘC DẪN NGUỒN GỐC RÕ RÀNG
        if source_url and source_url not in content_md:
            source_box = (
                f"\n\n---\n\n"
                f"> 📌 **Nguồn bài viết gốc:** [{source_title}]({source_url})  \n"
                f"> **Cơ quan phát hành:** {source_pub}  \n"
                f"> *Bản quyền nội dung và hình ảnh thuộc về tác giả và cơ quan báo chí phát hành. "
                f"Bách khoa Doanh nhân (doanhnhan.wiki) trích dẫn và biên tập phục vụ mục đích thông tin và học thuật.*"
            )
            content_md += source_box

        story_obj.content_md = content_md
        story_obj.source_name = source_pub
        story_obj.source_url = source_url
        story_obj.cover_caption = _clean(post_data.get("cover_caption")) or source_title
        story_obj.author_name = _clean(post_data.get("author_name")) or "Ban Biên tập doanhnhan.wiki"
        if person_obj:
            story_obj.featured_person = person_obj
        if company_obj:
            story_obj.featured_company = company_obj

        story_obj.status = status_choice
        if status_choice == Status.PUBLISHED and not story_obj.published_at:
            story_obj.published_at = timezone.now()
        story_obj.save()

        # Tự động tải ảnh bìa cho Story từ image_url
        image_url = _clean(post_data.get("image_url") or post_data.get("person_image_url"))
        if image_url and (created_story or not story_obj.cover_image):
            try:
                img_headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Referer": source_url or "https://google.com",
                }
                img_resp = requests.get(image_url, headers=img_headers, timeout=10)
                if img_resp.status_code == 200 and len(img_resp.content) > 1024:
                    ct = img_resp.headers.get("content-type", "").lower()
                    ext = "jpg"
                    if "png" in ct:
                        ext = "png"
                    elif "webp" in ct:
                        ext = "webp"
                    fname = f"story_{story_obj.slug or 'cover'}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                    story_obj.cover_image.save(fname, ContentFile(img_resp.content), save=True)
            except Exception as img_err:
                logger.warning("Không thể tải ảnh bìa Story tự động từ %s: %s", image_url, img_err)

    # 5. Ghi log kiểm toán (AuditLog)
    details = {
        "person": person_obj.full_name if person_obj else None,
        "company": company_obj.display_name if company_obj else None,
        "story": story_obj.title if story_obj else None,
        "source_url": source_url,
        "status": status_choice,
    }
    target_obj = story_obj or person_obj or company_obj
    log(user, "ai.crawler_import", target_obj,
        f"Thu thập dữ liệu AI & Lên bài: {story_obj or person_obj or company_obj or ''}".strip(),
        details)

    return {
        "person": person_obj,
        "company": company_obj,
        "story": story_obj,
        "created_person": created_person,
        "created_company": created_company,
        "created_story": created_story,
    }
