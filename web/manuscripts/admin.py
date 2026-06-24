from django import forms
from django.contrib import admin
from django.db import models
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from .models import Manuscript, Transcription

BIG_TEXTAREA = forms.Textarea(attrs={"rows": 24, "style": "width: 100%;"})

# Friendly labels for the image-metadata panel.
IMAGE_LABELS = {
    "width": "Largura (px)",
    "height": "Altura (px)",
    "format": "Formato",
    "mode": "Modo",
    "dpi": "DPI",
    "size_bytes": "Tamanho",
}
EXIF_LABELS = {
    "DateTimeOriginal": "Data original",
    "DateTimeDigitized": "Data de digitalização",
    "DateTime": "Data",
    "Make": "Equipamento (marca)",
    "Model": "Equipamento (modelo)",
    "Software": "Software",
    "Artist": "Autor",
    "Copyright": "Direitos",
    "ImageDescription": "Descrição",
    "XResolution": "Resolução X",
    "YResolution": "Resolução Y",
    "ResolutionUnit": "Unidade de resolução",
}


def _human_size(value):
    try:
        size = float(value)
    except (TypeError, ValueError):
        return value
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024


def _image_rows(image):
    rows = []
    for key, label in IMAGE_LABELS.items():
        if key not in image:
            continue
        value = image[key]
        if key == "size_bytes":
            value = _human_size(value)
        elif key == "dpi" and isinstance(value, list):
            value = " × ".join(str(v) for v in value)
        rows.append((label, value))
    exif = image.get("exif") or {}
    for key, label in EXIF_LABELS.items():
        if key in exif:
            rows.append((label, exif[key]))
    return rows

PREVIEW_HTML = mark_safe(
    """
    <div id="ms-preview">
      <span class="ms-preview-empty" style="color:#666;">
        Cole o URL do manuscrito acima para o ver aqui.
      </span>
      <img class="ms-preview-img" alt="manuscrito"
           style="display:none;max-width:700px;height:auto;border:1px solid #ccc;" />
      <a class="ms-preview-link" target="_blank" rel="noopener"
         style="display:none;padding:.4rem .8rem;background:#7a5c3e;color:#fff;
                border-radius:6px;text-decoration:none;">Abrir manuscrito ↗</a>
    </div>
    """
)


class ManuscriptForm(forms.ModelForm):
    """Manuscript form with the transcription text built in, so an expert fills
    one form: URL + text + Save."""

    transcription_text = forms.CharField(
        label="Transcrição",
        required=False,
        widget=BIG_TEXTAREA,
        help_text="Escreva aqui o conteúdo do manuscrito.",
    )
    transcription_status = forms.ChoiceField(
        label="Estado da transcrição",
        required=False,
        choices=Transcription.Status.choices,
        initial=Transcription.Status.DRAFT,
    )

    class Meta:
        model = Manuscript
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Prefill from the existing (latest) transcription when editing.
        if self.instance.pk:
            tr = self.instance.transcriptions.order_by("-updated_at").first()
            if tr:
                self.fields["transcription_text"].initial = tr.text
                self.fields["transcription_status"].initial = tr.status


@admin.register(Manuscript)
class ManuscriptAdmin(admin.ModelAdmin):
    form = ManuscriptForm
    list_display = (
        "__str__",
        "source",
        "verified",
        "transcription_count",
        "updated_at",
    )
    list_filter = ("verified", "metadata_source", "source")
    search_fields = ("reference", "reference_code", "image_no", "title", "source")
    readonly_fields = (
        "preview",
        "image_metadata_display",
        "image_sha256",
        "created_at",
        "updated_at",
    )
    formfield_overrides = {
        models.URLField: {"widget": forms.URLInput(attrs={"style": "width: 40em;"})},
    }

    class Media:
        js = ("manuscripts/preview.js",)
        css = {"all": ("manuscripts/transcribe.css",)}

    fieldsets = (
        (
            "Transcrever",
            {
                "classes": ("transcrever",),
                "fields": (
                    "source_url",
                    "preview",
                    "transcription_text",
                    "transcription_status",
                ),
                "description": "Cole o URL do manuscrito, escreva a transcrição e grave.",
            },
        ),
        (
            "Detalhes (opcional)",
            {
                "classes": ("collapse",),
                "fields": (
                    "title",
                    "verified",
                    "reference",
                    "reference_code",
                    "image_no",
                    "source",
                ),
            },
        ),
        (
            "Imagem e metadados (opcional)",
            {
                "classes": ("collapse",),
                "fields": (
                    "image",
                    "image_metadata_display",
                    "image_sha256",
                    "metadata_source",
                    "raw_metadata",
                    "notes",
                ),
            },
        ),
        ("Datas", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="pré-visualização")
    def preview(self, obj):
        return PREVIEW_HTML

    actions = ["extract_image_metadata"]

    @admin.display(description="transcrições")
    def transcription_count(self, obj):
        return obj.transcriptions.count()

    @admin.display(description="Metadados da imagem")
    def image_metadata_display(self, obj):
        image = (obj.raw_metadata or {}).get("image") if obj and obj.pk else None
        if not image:
            return "Sem metadados de imagem ainda — grave com um URL de imagem ou use a ação “Extrair metadados da imagem”."
        rows = _image_rows(image)
        if not rows:
            return "—"
        body = format_html_join(
            "",
            "<tr><th style='text-align:left;padding:2px 14px 2px 0;white-space:nowrap;'>{}</th><td>{}</td></tr>",
            rows,
        )
        return format_html("<table>{}</table>", body)

    @admin.action(description="Extrair metadados da imagem (download)")
    def extract_image_metadata(self, request, queryset):
        done = 0
        for ms in queryset:
            try:
                if ms.pull_image_metadata(fetch=True):
                    ms.save(update_fields=["raw_metadata"])
                    done += 1
            except Exception:
                pass
        self.message_user(request, f"Metadados de imagem extraídos: {done}/{queryset.count()}.")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        text = (form.cleaned_data.get("transcription_text") or "").strip()
        if not text:
            return
        status = (
            form.cleaned_data.get("transcription_status")
            or Transcription.Status.DRAFT
        )
        tr = obj.transcriptions.order_by("-updated_at").first()
        if tr is None:
            tr = Transcription(manuscript=obj, transcriber=request.user)
        tr.text = text
        tr.status = status
        if tr.transcriber_id is None:
            tr.transcriber = request.user
        tr.save()


@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ("manuscript", "status", "transcriber", "updated_at")
    list_filter = ("status", "transcriber")
    search_fields = ("manuscript__reference", "manuscript__title", "text")
    autocomplete_fields = ("manuscript",)
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if obj.transcriber_id is None:
            obj.transcriber = request.user
        super().save_model(request, obj, form, change)
