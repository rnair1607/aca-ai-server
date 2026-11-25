"""Image prep: fix rotation, resize, strip metadata, encode for the LLM."""

import base64
import io
from pathlib import Path

from PIL import Image, ImageOps

from .config import IMAGE_MAX_EDGE


def prepare(
    path: str | Path, max_edge: int = IMAGE_MAX_EDGE, quality: int = 85
) -> bytes:
    """Return JPEG bytes: EXIF-rotated, longest edge <= max_edge, metadata (incl. GPS) removed."""
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((max_edge, max_edge))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=quality)  # re-encode without exif= drops metadata
    return buf.getvalue()


def to_data_url(jpeg: bytes) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(jpeg).decode()
