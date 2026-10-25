"""
Tiện ích xử lý ảnh an toàn cho tòa soạn:
- Xóa sạch siêu dữ liệu EXIF / GPS / Thiết bị chụp ảnh để bảo vệ quyền riêng tư.
- Tự động xoay ảnh đúng chiều theo Orientation trước khi strip EXIF.
- Nén và chuẩn hóa định dạng ảnh.
"""
import io
import logging
from django.core.files.base import ContentFile
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def strip_image_exif(image_file, max_dimension: int = 2400, quality: int = 88) -> ContentFile:
    """
    Nhận vào file ảnh (UploadedFile, File, hoặc bytes), loại bỏ toàn bộ EXIF/GPS,
    giới hạn kích thước tối đa và trả về ContentFile sạch an toàn.
    """
    if not image_file:
        return image_file

    try:
        image_file.seek(0)
        img = Image.open(image_file)
        orig_format = (img.format or "JPEG").upper()
        if orig_format not in ("JPEG", "JPG", "PNG", "WEBP"):
            orig_format = "JPEG"

        # Tự động xoay ảnh theo EXIF orientation trước khi xóa
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # Giới hạn kích thước nếu quá lớn
        if max_dimension and (img.width > max_dimension or img.height > max_dimension):
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        # Xử lý hệ màu
        save_format = "JPEG" if orig_format in ("JPEG", "JPG") else orig_format
        if save_format == "JPEG":
            if img.mode in ("RGBA", "P", "LA"):
                # Tạo nền trắng khi chuyển từ ảnh trong suốt sang JPG
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "RGBA":
                    bg.paste(img, mask=img.split()[3])
                else:
                    bg.paste(img.convert("RGB"))
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")

        out_io = io.BytesIO()
        # Lưu mà không truyền tham số exif=... -> EXIF và GPS bị loại bỏ hoàn toàn
        save_params = {"optimize": True}
        if save_format in ("JPEG", "WEBP"):
            save_params["quality"] = quality

        img.save(out_io, format=save_format, **save_params)
        out_io.seek(0)

        ext = "jpg" if save_format == "JPEG" else save_format.lower()
        orig_name = getattr(image_file, "name", f"image.{ext}")
        name = orig_name.rsplit(".", 1)[0] + f".{ext}"
        return ContentFile(out_io.getvalue(), name=name)

    except Exception as e:
        logger.warning("Không thể xử lý EXIF cho file ảnh: %s", e)
        if hasattr(image_file, "seek"):
            image_file.seek(0)
        return image_file
