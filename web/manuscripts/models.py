import hashlib

from django.conf import settings
from django.db import models

from . import parsing


class Manuscript(models.Model):
    """A single manuscript image to be transcribed.

    Identity is the internal surrogate ``id``. External references are mutable
    attributes (archives change reference codes/URLs on DigitARQ migrations), so
    the robust matching anchor is ``image_sha256``. See docs/metadata.md.
    """

    class MetadataSource(models.TextChoices):
        MANUAL = "manual", "Manual"
        FILENAME = "filename", "Nome do ficheiro"
        SCRAPED = "scraped", "Recolhido (scrape)"
        DIGITARQ = "digitarq", "DigitARQ"

    # Full per-image reference, e.g. PT-ADVIS-AC-GCVIS-H-D-001-01016_m0003.
    # Optional and only a soft uniqueness guard — NOT the identity.
    reference = models.CharField(
        "referencia",
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="Referencia completa por imagem, ex.: PT-ADVIS-...-01016_m0003",
    )
    # Parsed structured parts of the reference.
    reference_code = models.CharField(
        "codigo de referencia (unidade)",
        max_length=255,
        blank=True,
        db_index=True,
        help_text="Codigo ISAD da unidade/livro, sem o numero de imagem.",
    )
    image_no = models.CharField(
        "numero da imagem", max_length=50, blank=True, help_text="Ex.: m0003"
    )

    title = models.CharField("titulo", max_length=255, blank=True)
    image = models.ImageField("imagem", upload_to="manuscripts/", blank=True)

    # Robust, immutable matching anchor: SHA-256 of the original image bytes.
    image_sha256 = models.CharField(
        "SHA-256 da imagem",
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="Hash dos bytes da imagem original (deduplicacao/correspondencia).",
    )

    source = models.CharField(
        "fonte", max_length=200, blank=True, help_text="Arquivo ou coleccao de origem."
    )
    source_url = models.URLField("URL de origem", blank=True)

    # Original metadata exactly as received from the source — never overwritten.
    raw_metadata = models.JSONField("metadados originais", default=dict, blank=True)
    metadata_source = models.CharField(
        "proveniencia dos metadados",
        max_length=20,
        choices=MetadataSource.choices,
        default=MetadataSource.MANUAL,
    )
    verified = models.BooleanField(
        "verificado",
        default=False,
        help_text="Confirmado por um especialista; importacoes nao sobrescrevem.",
    )

    notes = models.TextField("notas", blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "manuscrito"
        verbose_name_plural = "manuscritos"
        ordering = ["reference_code", "image_no"]

    def __str__(self):
        return self.title or self.reference or self.reference_code or f"#{self.pk}"

    def compute_sha256(self):
        """SHA-256 of the stored image bytes, or None if there is no image."""
        if not self.image:
            return None
        h = hashlib.sha256()
        self.image.open("rb")
        try:
            for chunk in self.image.chunks():
                h.update(chunk)
        finally:
            self.image.seek(0)
        return h.hexdigest()

    def autofill_metadata(self):
        """Fill reference/reference_code/image_no/source from the image filename
        or source URL. Only fills empty fields — never overwrites what was typed
        or verified. Returns True if anything changed."""
        source = self.image.name if self.image else self.source_url
        meta = parsing.extract_metadata(source)
        if not meta:
            return False
        changed = False
        for field in ("reference", "reference_code", "image_no", "source"):
            if not getattr(self, field) and meta.get(field):
                setattr(self, field, meta[field])
                changed = True
        if changed and self.metadata_source == self.MetadataSource.MANUAL:
            self.metadata_source = self.MetadataSource.FILENAME
        return changed

    def save(self, *args, **kwargs):
        # Hash on first save with an image so admin uploads are also anchored.
        if self.image and not self.image_sha256:
            self.image_sha256 = self.compute_sha256()
        if not self.verified:
            self.autofill_metadata()
        super().save(*args, **kwargs)


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
