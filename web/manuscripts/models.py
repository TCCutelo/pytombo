from django.conf import settings
from django.db import models


class Manuscript(models.Model):
    """A single manuscript image to be transcribed."""

    reference = models.CharField(
        "referencia",
        max_length=200,
        unique=True,
        help_text="Referencia do arquivo, ex.: PT-ADVIS-AC-GCVIS-H-D-001-01016_m0003",
    )
    title = models.CharField("titulo", max_length=200, blank=True)
    image = models.ImageField("imagem", upload_to="manuscripts/")
    source = models.CharField(
        "fonte", max_length=200, blank=True, help_text="Arquivo ou coleccao de origem."
    )
    source_url = models.URLField("URL de origem", blank=True)
    notes = models.TextField("notas", blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "manuscrito"
        verbose_name_plural = "manuscritos"
        ordering = ["reference"]

    def __str__(self):
        return self.title or self.reference


class Transcription(models.Model):
    """An expert's transcription of a manuscript.

    Each approved transcription is a labeled (image -> text) pair that feeds the
    HTR training pipeline described in docs/plan.md.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        REVIEW = "review", "Em revisao"
        APPROVED = "approved", "Aprovada"

    manuscript = models.ForeignKey(
        Manuscript,
        on_delete=models.CASCADE,
        related_name="transcriptions",
        verbose_name="manuscrito",
    )
    text = models.TextField("transcricao")
    transcriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transcriptions",
        verbose_name="transcritor",
    )
    status = models.CharField(
        "estado", max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    notes = models.TextField("notas do transcritor", blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "transcricao"
        verbose_name_plural = "transcricoes"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.manuscript} ({self.get_status_display()})"

    @property
    def is_training_ready(self):
        """Approved transcriptions are usable as HTR ground truth."""
        return self.status == self.Status.APPROVED
