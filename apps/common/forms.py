from django import forms


class StyledFormMixin:
    """Gắn class giao diện (input/select/textarea) và chuẩn hóa kiểu calendar (date / datetime-local) cho mọi trường."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            w = field.widget
            # Tự động cấu hình widget calendar cho DateField & DateTimeField
            if isinstance(field, forms.DateTimeField):
                if not getattr(w, "input_type", None) or w.input_type in ("text", "datetime"):
                    w.input_type = "datetime-local"
                    if isinstance(w, forms.DateTimeInput):
                        w.format = "%Y-%m-%dT%H:%M"
                if not getattr(field, "input_formats", None):
                    field.input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%d"]
                else:
                    formats = list(field.input_formats)
                    for fmt in ["%Y-%m-%dT%H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M"]:
                        if fmt not in formats:
                            formats.insert(0, fmt)
                    field.input_formats = formats

            elif isinstance(field, forms.DateField):
                if not getattr(w, "input_type", None) or w.input_type == "text":
                    w.input_type = "date"
                    if isinstance(w, forms.DateInput):
                        w.format = "%Y-%m-%d"
                if not getattr(field, "input_formats", None):
                    field.input_formats = ["%Y-%m-%d", "%d/%m/%Y"]
                else:
                    formats = list(field.input_formats)
                    for fmt in ["%Y-%m-%d", "%d/%m/%Y"]:
                        if fmt not in formats:
                            formats.insert(0, fmt)
                    field.input_formats = formats

            if isinstance(w, (forms.CheckboxInput, forms.CheckboxSelectMultiple, forms.RadioSelect, forms.FileInput)):
                continue
            css = "textarea" if isinstance(w, forms.Textarea) else "select" if isinstance(w, forms.Select) else "input"
            w.attrs["class"] = (w.attrs.get("class", "") + " " + css).strip()
