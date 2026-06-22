from django import forms
from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe

from .models import Manuscript, Transcription

BIG_TEXTAREA = forms.Textarea(attrs={"rows": 18, "style": "width: 95%;"})

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


class TranscriptionInline(admin.StackedInline):
    model = Transcription
    extra = 1
    fields = ("text", "status", "notes")
    formfield_overrides = {models.TextField: {"widget": BIG_TEXTAREA}}


@admin.register(Manuscript)
class ManuscriptAdmin(admin.ModelAdmin):
    inlines = [TranscriptionInline]
    list_display = (
        "__str__",
        "source",
        "verified",
        "transcription_count",
        "updated_at",
    )
    list_filter = ("verified", "metadata_source", "source")
    search_fields = ("reference", "reference_code", "image_no", "title", "source")
    readonly_fields = ("preview", "image_sha256", "created_at", "updated_at")
    formfield_overrides = {
        models.URLField: {"widget": forms.URLInput(attrs={"style": "width: 40em;"})},
    }

    class Media:
        js = ("manuscripts/preview.js",)

    fieldsets = (
        (
            "Transcrever",
            {
                "fields": ("source_url", "preview"),
                "description": "Cole o URL do manuscrito e escreva a transcrição em baixo.",
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
                "fields": ("image", "image_sha256", "metadata_source", "raw_metadata", "notes"),
            },
        ),
        ("Datas", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="pré-visualização")
    def preview(self, obj):
        return PREVIEW_HTML

    @admin.display(description="transcrições")
    def transcription_count(self, obj):
        return obj.transcriptions.count()

    def save_formset(self, request, form, formset, change):
        # Record the logged-in expert as the transcriber on new transcriptions.
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, Transcription) and obj.transcriber_id is None:
                obj.transcriber = request.user
            obj.save()
        formset.save_m2m()
        for obj in formset.deleted_objects:
            obj.delete()


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
