"""Extract metadata from the image bytes themselves (not the filename).

Captures technical properties (dimensions, format, mode, dpi, size) and a
curated subset of EXIF (scan date, device, software, resolution, description,
copyright) when present. Results are JSON-serializable for raw_metadata.
"""

import urllib.request
from urllib.parse import urlparse

from PIL import ExifTags, Image

# EXIF tags worth keeping for archival scans.
EXIF_KEEP = {
    "DateTime",
    "DateTimeOriginal",
    "DateTimeDigitized",
    "Make",
    "Model",
    "Software",
    "Artist",
    "Copyright",
    "ImageDescription",
    "XResolution",
    "YResolution",
    "ResolutionUnit",
}

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".gif", ".bmp")
MAX_BYTES = 40 * 1024 * 1024  # cap downloads at 40 MB


def is_image_url(url):
    """True if the URL path ends in a known image extension."""
    return urlparse(url or "").path.lower().endswith(IMAGE_EXTS)


def _jsonable(value):
    if isinstance(value, bytes):
        return value.decode("latin-1", "ignore").replace("\x00", "").strip()
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    try:
        return float(value)  # e.g. EXIF IFDRational
    except (TypeError, ValueError):
        return str(value)


def _exif(im):
    out = {}
    try:
        exif = im.getexif()
    except Exception:
        return out
    items = dict(exif)
    try:
        items.update(exif.get_ifd(0x8769))  # Exif sub-IFD (DateTimeOriginal, …)
    except Exception:
        pass
    for tag_id, val in items.items():
        name = ExifTags.TAGS.get(tag_id)
        if name in EXIF_KEEP:
            cleaned = _jsonable(val)
            if cleaned not in ("", None):
                out[name] = cleaned
    return out


def extract_image_metadata(fp, size_bytes=None):
    """Return a dict of image metadata from a file-like object."""
    info = {}
    with Image.open(fp) as im:
        info["width"], info["height"] = im.size
        info["format"] = im.format
        info["mode"] = im.mode
        dpi = im.info.get("dpi")
        if dpi:
            try:
                info["dpi"] = [round(float(dpi[0])), round(float(dpi[1]))]
            except (TypeError, ValueError):
                pass
        exif = _exif(im)
        if exif:
            info["exif"] = exif
    if size_bytes is not None:
        info["size_bytes"] = size_bytes
    return info


def download_bytes(url, timeout=6):
    """Best-effort download (http/https only, size-capped). Returns bytes or None."""
    if not (url or "").lower().startswith(("http://", "https://")):
        return None
    req = urllib.request.Request(url, headers={"User-Agent": "BisaBot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        data = resp.read(MAX_BYTES + 1)
    return None if len(data) > MAX_BYTES else data
