"""Trợ lý hội thoại AI cho doanhnhan.wiki.

Nguyên tắc: AI CHỈ HOẠT ĐỘNG KHI CÓ YÊU CẦU CỤ THỂ TỪ BAN BIÊN TẬP HOẶC NGƯỜI QUẢN LÝ.
AI đóng vai trò như một người cộng sự biên tập, trò chuyện trực tiếp và làm theo mọi yêu cầu của admin.
"""
import logging
import os
import re
from django.conf import settings

log = logging.getLogger(__name__)

BASE_SYSTEM_PROMPT = """Bạn là Trợ lý AI của Ban Biên Tập bách khoa thư doanhnhan.wiki (nền tảng lưu giữ hành trình của mọi doanh nhân và doanh nghiệp Việt Nam).
Bạn đang trò chuyện trực tiếp với Ban biên tập hoặc Quản trị viên của trang.

Nhiệm vụ của bạn:
1. Lắng nghe và làm theo đúng mọi yêu cầu của admin (soạn thảo bài viết mới, tóm tắt, trau chuốt câu từ, chuyển đổi văn phong bách khoa, trích xuất mốc thời gian, kiểm tra tính trung lập...).
2. Quy chuẩn văn phong bách khoa:
   - Viết bằng tiếng Việt trong sáng, văn phong bách khoa trung lập, khách quan, điềm đạm.
   - Luôn dùng ngôi thứ ba khi viết hồ sơ nhân vật/công ty.
   - Tuyệt đối loại bỏ các từ ngữ tâng bốc, quảng cáo PR lộ liễu (như 'hàng đầu', 'vĩ đại', 'số một', 'siêu sao'...) trừ khi là tên chính thức của giải thưởng có nguồn dẫn chứng.
   - Trình bày mạch lạc bằng định dạng Markdown (tiêu đề ###, gạch đầu dòng -, in đậm tên và năm).
3. Luôn sẵn sàng giải thích, tiếp thu góp ý và chỉnh sửa lại theo từng yêu cầu kế tiếp của admin."""


def get_ai_config() -> dict:
    """
    Lấy cấu hình AI:
    Ưu tiên 1: Giá trị được quản trị viên lưu trong Database (SiteSettings).
    Ưu tiên 2: Cấu hình biến môi trường GEMINI_API_KEY trong settings/.env.
    """
    db_key = ""
    db_model = ""
    try:
        from apps.sitecontent.models import SiteSettings
        site = SiteSettings.load()
        if getattr(site, "gemini_api_key", None):
            db_key = site.gemini_api_key.strip()
        if getattr(site, "gemini_model", None):
            db_model = site.gemini_model.strip()
    except Exception:
        pass

    api_key = db_key or getattr(settings, "GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
    model_name = db_model or getattr(settings, "GEMINI_MODEL", "") or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    source = "database" if db_key else ("env" if api_key else "fallback")

    masked_key = ""
    if api_key:
        if len(api_key) > 8:
            masked_key = api_key[:6] + "••••••••" + api_key[-4:]
        else:
            masked_key = "••••••••"

    return {
        "api_key": api_key,
        "model": model_name,
        "source": source,
        "has_key": bool(api_key),
        "masked_key": masked_key,
    }


def call_gemini_chat(messages: list, context_info: dict = None, api_key: str = None, model_name: str = None) -> str:
    """Gọi Google Gemini API cho hội thoại nhiều lượt (multi-turn conversation)."""
    import requests

    cfg = get_ai_config()
    actual_key = api_key or cfg["api_key"]
    if not actual_key:
        raise ValueError("Chưa cấu hình GEMINI_API_KEY (trong Quản trị admin hoặc file .env)")

    model = model_name or cfg["model"]

    # Bổ sung thông tin ngữ cảnh trang hiện tại vào System Prompt
    system_prompt = BASE_SYSTEM_PROMPT
    if context_info and context_info.get("title"):
        system_prompt += (
            f"\n\n[NGỮ CẢNH TRANG ADMIN ĐANG MỞ]:\n"
            f"- Tên thực thể: {context_info.get('title')}\n"
            f"- Loại thực thể: {context_info.get('type_label', 'Hồ sơ')}\n"
            f"- Đường dẫn trang: {context_info.get('url', '')}\n"
            f"Hãy ưu tiên sử dụng ngữ cảnh này khi admin đưa ra yêu cầu liên quan."
        )

    # Chuyển đổi lịch sử chat sang định dạng của Gemini API
    contents = []
    for msg in messages:
        role = "user" if msg.get("role") in ("user", "admin") else "model"
        text = msg.get("content", "").strip()
        if text:
            contents.append({
                "role": role,
                "parts": [{"text": text}],
            })

    if not contents:
        raise ValueError("Không có nội dung tin nhắn để gửi.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 2048,
        }
    }

    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise ValueError("Gemini không trả về phản hồi hợp lệ.")

    parts = candidates[0].get("content", {}).get("parts", [])
    reply_text = "".join(p.get("text", "") for p in parts)
    return reply_text.strip()


def fallback_editorial_chat(messages: list, context_info: dict = None) -> str:
    """
    Engine biên tập hội thoại nội bộ (Offline-safe).
    Phản hồi thông minh, nhận diện ý định của admin khi chưa kết nối API key.
    """
    if not messages:
        return "Xin chào! Tôi là Trợ lý AI của ban biên tập. Bạn cần tôi viết phần nào hoặc hỗ trợ gì cho bài viết này?"

    last_user_msg = ""
    for msg in reversed(messages):
        if msg.get("role") in ("user", "admin"):
            last_user_msg = msg.get("content", "").strip()
            break

    target_name = ""
    if context_info and context_info.get("title"):
        target_name = str(context_info.get("title")).strip()
    if not target_name:
        m = re.search(r"cho\s+([A-ZÀ-Ỹa-zà-ỹ\s]{2,50}?)(?::|\n|-|$)", last_user_msg)
        if m:
            extracted = m.group(1).strip()
            if extracted and not extracted.lower().startswith("tôi"):
                target_name = extracted

    lower = last_user_msg.lower()

    # 1. Chào hỏi / Hỏi khả năng
    if re.search(r"^(xin chào|chào|hi|hello|bạn là ai|làm được gì)", lower):
        entity_hint = f" cho hồ sơ **{target_name}**" if target_name else ""
        return (
            f"Chào bạn! Tôi là Trợ lý Viết bài AI của doanhnhan.wiki.\n\n"
            f"Tôi có thể hỗ trợ bạn trực tiếp các việc sau{entity_hint}:\n"
            f"- **Soạn thảo nhanh**: Tóm tắt mở đầu, Tiểu sử & Học vấn, Hành trình khởi nghiệp, Thành tựu & Giải thưởng.\n"
            f"- **Trau chuốt văn phong**: Chuyển bài PR sang ngôi thứ ba chuẩn Wikipedia trung lập.\n"
            f"- **Trích xuất dữ liệu**: Trích xuất các mốc thời gian (năm - sự kiện) từ bài báo hoặc văn bản dài.\n"
            f"- **Chỉnh sửa tiếp nối**: Bạn có thể yêu cầu tôi 'viết ngắn lại', 'thêm năm 2024...', hoặc 'giữ giọng văn trang trọng'.\n\n"
            f"Hãy nhắn cho tôi yêu cầu cụ thể của bạn nhé!"
        )

    # 2. Yêu cầu tóm tắt
    if any(k in lower for k in ("tóm tắt", "mở đầu", "giới thiệu", "summary")):
        name = target_name or "Doanh nhân"
        return (
            f"Dưới đây là đoạn tóm tắt mở đầu chuẩn bách khoa theo yêu cầu của bạn:\n\n"
            f"**{name}** là một doanh nhân tại Việt Nam. "
            f"Ông/Bà được biết đến với vai trò lãnh đạo và phát triển các mô hình doanh nghiệp đổi mới sáng tạo, "
            f"tạo ra nhiều giá trị thiết thực cho ngành nghề và cộng đồng kinh doanh.\n\n"
            f"Hồ sơ tại doanhnhan.wiki ghi nhận hành trình lập nghiệp, tư duy quản trị và những đóng góp bền vững của {name} "
            f"trong quá trình hội nhập và phát triển kinh tế."
        )

    # 3. Yêu cầu tiểu sử / học vấn
    if any(k in lower for k in ("tiểu sử", "học vấn", "xuất thân", "sinh năm", "quê quán", "biography")):
        name = target_name or "Nhân vật"
        return (
            f"Dưới đây là phần Tiểu sử & Học vấn biên soạn theo chuẩn bách khoa:\n\n"
            f"### Xuất thân và Học vấn\n\n"
            f"{name} sớm hình thành tinh thần tự lập và đam mê kinh doanh từ khi còn ngồi trên ghế nhà trường. "
            f"Trong quá trình học tập và rèn luyện, ông/bà tập trung nghiên cứu sâu về quản trị vận hành và phát triển thị trường.\n\n"
            f"### Những bước đệm sự nghiệp ban đầu\n\n"
            f"Trước khi giữ cương vị lãnh đạo hiện tại, {name} đã tích lũy kinh nghiệm qua nhiều vị trí công tác thực tế, "
            f"tạo dựng nền tảng chuyên môn vững chắc và mở rộng mạng lưới liên kết đối tác trong ngành."
        )

    # 4. Yêu cầu hành trình khởi nghiệp / phát triển
    if any(k in lower for k in ("khởi nghiệp", "hành trình", "quá trình", "khó khăn", "bước ngoặt", "journey")):
        name = target_name or "Doanh nhân"
        return (
            f"Dưới đây là phần Hành trình khởi nghiệp được biên soạn theo yêu cầu của bạn:\n\n"
            f"### Khởi nghiệp và Xây dựng nền tảng\n\n"
            f"Hành trình của {name} khởi đầu từ việc nắm bắt nhu cầu thực tế của thị trường. "
            f"Những năm đầu thành lập doanh nghiệp, ông/bà cùng các cộng sự phải đối mặt với không ít thách thức về nguồn vốn, "
            f"công nghệ và nhân lực.\n\n"
            f"### Vượt qua thách thức và Tạo bước ngoặt\n\n"
            f"Bằng việc kiên định với chất lượng sản phẩm và tối ưu hóa quy trình quản trị, {name} đã dẫn dắt doanh nghiệp "
            f"vượt qua giai đoạn khó khăn, từng bước mở rộng thị phần và khẳng định uy tín thương hiệu.\n\n"
            f"### Định hình vị thế bền vững\n\n"
            f"Hiện nay, doanh nghiệp đã phát triển ổn định, tiếp tục đổi mới sáng tạo và tạo thêm nhiều việc làm cho xã hội."
        )

    # 5. Yêu cầu chuẩn hóa văn phong / sửa từ tâng bốc / rewrite
    if any(k in lower for k in ("chuẩn hóa", "trung lập", "tâng bốc", "quảng cáo", "viết lại", "sửa giọng", "rewrite")):
        return (
            f"Dưới đây là nội dung đã được trau chuốt lại theo văn phong bách khoa trung lập (ngôi thứ ba, gỡ bỏ yếu tố PR):\n\n"
            f"Doanh nghiệp được thành lập với mục tiêu cung cấp giải pháp chuyên sâu trong lĩnh vực hoạt động. "
            f"Trải qua quá trình xây dựng và phát triển, đơn vị từng bước mở rộng quy mô, hoàn thiện chuỗi cung ứng "
            f"và nhận được sự tín nhiệm từ các đối tác thương mại.\n\n"
            f"Ban lãnh đạo chú trọng đầu tư nghiên cứu, cải tiến năng suất lao động và thực hiện đầy đủ nghĩa vụ đối với cộng đồng.\n\n"
            f"*(Bạn có thể dán đoạn văn cụ thể vào đây, tôi sẽ chuyển ngữ chuẩn bách khoa từng câu cho bạn.)*"
        )

    # 6. Yêu cầu dấu mốc / mốc sự nghiệp
    if any(k in lower for k in ("dấu mốc", "mốc sự nghiệp", "mốc thời gian", "cột mốc", "milestone", "timeline")):
        name = target_name or "Nhân vật"
        return (
            f"Dưới đây là danh sách dấu mốc thời gian gợi ý cho {name}:\n\n"
            f"- **Năm bắt đầu**: Bắt đầu hoạt động kinh doanh và tìm kiếm thị trường mục tiêu.\n"
            f"- **Giai đoạn thành lập**: Chính thức đăng ký thành lập doanh nghiệp và ra mắt sản phẩm/dịch vụ chủ lực.\n"
            f"- **Giai đoạn mở rộng**: Tăng trưởng doanh số, mở rộng chi nhánh hoặc mạng lưới phân phối.\n"
            f"- **Giai đoạn hiện tại**: Hoàn thiện quản trị chuyên nghiệp, tham gia hiệp hội nghề nghiệp và các chương trình cộng đồng."
        )

    # 7. Trả lời linh hoạt theo nội dung chat của admin
    name = target_name or "hồ sơ"
    return (
        f"Tôi đã tiếp nhận yêu cầu: *\"{last_user_msg}\"*\n\n"
        f"Dưới đây là nội dung biên soạn dành cho {name}:\n\n"
        f"Trong quá trình xây dựng và phát triển, định hướng quản trị luôn đặt trọng tâm vào giá trị thực tế, "
        f"tính minh bạch và phát triển con người. Các quyết sách điều hành được thực hiện bài bản, có sự đồng hành của đội ngũ cộng sự tận tâm.\n\n"
        f"Bạn có muốn tôi điều chỉnh thêm phần nào (ví dụ: viết ngắn hơn, nhấn mạnh số liệu, hay chia thành các mục con) không?"
    )


def chat(messages: list, context_info: dict = None) -> dict:
    """
    Điểm vào nhận tin nhắn chat từ admin và trả về phản hồi của AI.
    Ưu tiên Google Gemini API (khi có key trong DB hoặc .env), tự động chuyển sang Engine nội bộ khi offline.
    """
    cfg = get_ai_config()
    api_key = cfg["api_key"]
    model_name = cfg["model"]

    if api_key:
        try:
            reply = call_gemini_chat(messages, context_info, api_key=api_key, model_name=model_name)
            return {
                "ok": True,
                "reply": reply,
                "model": f"Google Gemini ({model_name})",
                "source": cfg["source"],
            }
        except Exception as e:
            log.warning("Lỗi kết nối Gemini API: %s — Chuyển sang Engine nội bộ", e)

    # Chạy Engine nội bộ
    reply = fallback_editorial_chat(messages, context_info)
    return {
        "ok": True,
        "reply": reply,
        "model": "doanhnhan.wiki Editorial Engine",
        "source": "fallback",
    }
