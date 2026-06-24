"""Backfill image hashes and extracted metadata for existing manuscripts.

For every Manuscript this command:
  * computes ``image_sha256`` (the immutable matching anchor) when missing,
    detecting collisions instead of crashing;
  * extracts reference/reference_code/image_no/source from the filename or URL
    via ``Manuscript.autofill_metadata`` (shared with the admin save path).

It is non-destructive: rows flagged ``verified`` are not re-parsed, only empty
fields are filled, and hashes that would collide are reported, not written.
See docs/metadata.md.
"""

from django.core.management.base import BaseCommand

from manuscripts.models import Manuscript


class Command(BaseCommand):
    help = "Backfill image_sha256 and extracted metadata for manuscripts."

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

            # 2) Extract metadata — never touch expert-verified rows.
            if ms.verified:
                stats["skipped_verified"] += 1
            elif ms.autofill_metadata():
                stats["parsed"] += 1
                changed = True

            if changed and not dry_run:
                ms.save(update_fields=[
                    "image_sha256",
                    "reference",
                    "reference_code",
                    "image_no",
                    "source",
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
