from django.contrib import admin
from django.utils.html import format_html

from .models import Manuscript, Transcription


class TranscriptionInline(admin.StackedInline):
    model = Transcription
    extra = 1
    fields = ("text", "status", "transcriber", "notes")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Manuscript)
class ManuscriptAdmin(admin.ModelAdmin):
    list_display = (
        "reference_code",
        "image_no",
        "title",
        "source",
        "verified",
        "thumbnail",
        "transcription_count",
    )
    list_filter = ("verified", "metadata_source", "source")
    search_fields = ("reference", "reference_code", "image_no", "title", "source")
    readonly_fields = ("preview", "image_sha256", "created_at", "updated_at")
    inlines = [TranscriptionInline]
    fieldsets = (
        (None, {"fields": ("title", "image", "preview", "verified")}),
        (
            "Referência / origem",
            {
                "fields": (
                    "reference",
                    "reference_code",
                    "image_no",
                    "source",
                    "source_url",
                    "image_sha256",
                )
            },
        ),
        (
            "Metadados",
            {"fields": ("metadata_source", "raw_metadata", "notes")},
        ),
        ("Datas", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="pré-visualização")
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:600px;height:auto;border:1px solid #ccc;" />',
                obj.image.url,
            )
        return "—"

    @admin.display(description="imagem")
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;width:auto;" />', obj.image.url
            )
        return "—"

    @admin.display(description="transcrições")
    def transcription_count(self, obj):
        return obj.transcriptions.count()


@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ("manuscript", "status", "transcriber", "updated_at")
    list_filter = ("status", "transcriber")
    search_fields = ("manuscript__reference", "manuscript__title", "text")
    autocomplete_fields = ("manuscript",)
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        # Default the transcriber to the logged-in expert on first save.
        if obj.transcriber_id is None:
            obj.transcriber = request.user
        super().save_model(request, obj, form, change)
