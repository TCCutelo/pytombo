"""Extract manuscript metadata from a filename or image URL.

Archive filenames encode the reference, e.g.
``PT-ADVIS-AC-GCVIS-H-D-001-01016_m0003.jpg`` ->
  reference      = PT-ADVIS-AC-GCVIS-H-D-001-01016_m0003
  reference_code = PT-ADVIS-AC-GCVIS-H-D-001-01016   (the unit/book)
  image_no       = m0003
  source         = Arquivo Distrital de Viseu        (from the PT-ADVIS prefix)
"""

import os
import re
from urllib.parse import unquote, urlparse

# "<code>_m0003" / "<code>-m0003" -> code + image number
REFERENCE_RE = re.compile(r"^(?P<code>.+?)[_-](?P<img>m\d+)$", re.IGNORECASE)

# Archive code (2nd token of an ISAD reference) -> human name.
ARCHIVES = {
    "TT": "Arquivo Nacional Torre do Tombo",
    "ADAVR": "Arquivo Distrital de Aveiro",
    "ADBJA": "Arquivo Distrital de Beja",
    "ADBRG": "Arquivo Distrital de Braga",
    "ADBGC": "Arquivo Distrital de Bragança",
    "ADCTB": "Arquivo Distrital de Castelo Branco",
    "ADCBR": "Arquivo Distrital de Coimbra",
    "ADEVR": "Arquivo Distrital de Évora",
    "ADFAR": "Arquivo Distrital de Faro",
    "ADGRD": "Arquivo Distrital da Guarda",
    "ADLRA": "Arquivo Distrital de Leiria",
    "ADLSB": "Arquivo Distrital de Lisboa",
    "ADPTG": "Arquivo Distrital de Portalegre",
    "ADPRT": "Arquivo Distrital do Porto",
    "ADSTR": "Arquivo Distrital de Santarém",
    "ADSTB": "Arquivo Distrital de Setúbal",
    "ADVCT": "Arquivo Distrital de Viana do Castelo",
    "ADVRL": "Arquivo Distrital de Vila Real",
    "ADVIS": "Arquivo Distrital de Viseu",
    "ABM": "Arquivo Regional e Biblioteca Pública da Madeira",
}


def basename_of(filename_or_url):
    """Return the filename stem from a path or URL (no directory, no extension)."""
    value = (filename_or_url or "").strip()
    if not value:
        return ""
    parsed = urlparse(value)
    path = parsed.path if parsed.scheme else value
    base = unquote(os.path.basename(path))
    return os.path.splitext(base)[0]


def parse_reference(value):
    """Return (reference_code, image_no) from a reference string."""
    value = (value or "").strip()
    if not value:
        return "", ""
    match = REFERENCE_RE.match(value)
    if match:
        return match.group("code"), match.group("img").lower()
    return value, ""


def archive_name(reference_code):
    """Human archive name from an ISAD reference code, or '' if unknown."""
    parts = re.split(r"[-/]", reference_code or "")
    if len(parts) >= 2 and parts[0].upper() == "PT":
        return ARCHIVES.get(parts[1].upper(), "")
    return ""


def looks_archival(base):
    """True when the stem looks like an archival reference worth parsing."""
    if not base:
        return False
    if REFERENCE_RE.match(base):
        return True
    return base.upper().startswith(("PT-", "PT_", "PT/"))


def extract_metadata(filename_or_url):
    """Parse a filename/URL into manuscript metadata.

    Returns {} when the input does not look like an archival reference (so we
    never pollute records from generic URLs like '.../download?id=1').
    """
    base = basename_of(filename_or_url)
    if not looks_archival(base):
        return {}
    code, image_no = parse_reference(base)
    return {
        "reference": base,
        "reference_code": code,
        "image_no": image_no,
        "source": archive_name(code),
    }
