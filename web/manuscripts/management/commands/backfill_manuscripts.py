"""Backfill image hashes and parse references for existing manuscripts.

For every Manuscript this command:
  * computes ``image_sha256`` (the immutable matching anchor) when missing,
    detecting collisions instead of crashing;
  * parses ``reference`` / image filename into ``reference_code`` + ``image_no``;
  * marks ``metadata_source`` as FILENAME for parsed values.

It is non-destructive: rows flagged ``verified`` are never re-parsed, and hashes
that would collide with another row are reported, not written. See
docs/metadata.md.
"""

import os
import re

from django.core.management.base import BaseCommand

from manuscripts.models import Manuscript

# "PT-ADVIS-...-01016_m0003" -> code="PT-ADVIS-...-01016", img="m0003"
REFERENCE_RE = re.compile(r"^(?P<code>.+?)[_-](?P<img>m\d+)$", re.IGNORECASE)


def parse_reference(value):
    """Return (reference_code, image_no) parsed from a reference string."""
    value = (value or "").strip()
    if not value:
        return "", ""
    match = REFERENCE_RE.match(value)
    if match:
        return match.group("code"), match.group("img").lower()
    return value, ""


class Command(BaseCommand):
    help = "Backfill image_sha256 and parse reference_code/image_no for manuscripts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without writing.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        stats = {
            "total": 0,
            "hashed": 0,
            "hash_conflicts": 0,
            "parsed": 0,
            "skipped_verified": 0,
            "no_image": 0,
        }

        for ms in Manuscript.objects.all().iterator():
            stats["total"] += 1
            changed = False

            # 1) Hash (immutable anchor) — safe even on verified rows.
            if ms.image and not ms.image_sha256:
                digest = ms.compute_sha256()
                clash = (
                    Manuscript.objects.filter(image_sha256=digest)
                    .exclude(pk=ms.pk)
                    .first()
                )
                if clash:
                    stats["hash_conflicts"] += 1
                    self.stderr.write(
                        f"  ! #{ms.pk} duplicate of #{clash.pk} (sha256 {digest[:12]}…) — left unset"
                    )
                else:
                    ms.image_sha256 = digest
                    stats["hashed"] += 1
                    changed = True
            elif not ms.image:
                stats["no_image"] += 1

            # 2) Parse reference parts — never touch expert-verified rows.
            if ms.verified:
                stats["skipped_verified"] += 1
            elif not ms.reference_code:
                source = ms.reference or os.path.splitext(
                    os.path.basename(ms.image.name) if ms.image else ""
                )[0]
                code, image_no = parse_reference(source)
                if code:
                    ms.reference_code = code
                    if image_no and not ms.image_no:
                        ms.image_no = image_no
                    if ms.metadata_source == Manuscript.MetadataSource.MANUAL:
                        ms.metadata_source = Manuscript.MetadataSource.FILENAME
                    stats["parsed"] += 1
                    changed = True

            if changed and not dry_run:
                ms.save(update_fields=[
                    "image_sha256",
                    "reference_code",
                    "image_no",
                    "metadata_source",
                ])

        prefix = "[dry-run] " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"{prefix}{stats['total']} manuscritos | "
                f"hashed={stats['hashed']} conflicts={stats['hash_conflicts']} "
                f"parsed={stats['parsed']} verified_skipped={stats['skipped_verified']} "
                f"no_image={stats['no_image']}"
            )
        )
