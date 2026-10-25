import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

image_extensions = FileExtensionValidator(["jpg", "jpeg", "png", "webp"])
document_extensions = FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])

TAX_CODE_RE = re.compile(r"^\d{10}(-\d{3})?$")


def max_file_size(f):
    limit = settings.MAX_IMAGE_MB * 1024 * 1024
    if f and getattr(f, "size", 0) > limit:
        raise ValidationError(f"Tệp quá lớn (tối đa {settings.MAX_IMAGE_MB} MB).")


def validate_tax_code(value):
    if value and not TAX_CODE_RE.match(value):
        raise ValidationError("Mã số thuế gồm 10 chữ số, hoặc 10 chữ số kèm '-xxx' cho chi nhánh.")


def validate_year(value):
    if value is not None and not (1900 <= int(value) <= 2100):
        raise ValidationError("Năm không hợp lệ.")
