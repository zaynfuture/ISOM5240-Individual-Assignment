"""Image decoding shared by the upload interfaces."""

import warnings
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 10 * 1024 * 1024


def load_image(data: bytes) -> Image.Image:
    """Validate one upload and return an oriented RGB image for a pipeline."""
    if len(data) > MAX_BYTES:
        raise ValueError("That picture is too large. Please choose one under 10 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as source:
                if source.format not in {"JPEG", "PNG", "WEBP"}:
                    raise ValueError("Please choose a JPG, PNG, or WebP picture.")
                if source.width * source.height > 16_000_000:
                    raise ValueError("That picture has too many pixels. Please choose one under 16 megapixels.")
                source.load()
                image = ImageOps.exif_transpose(source).convert("RGB")
                image.thumbnail((1024, 1024))
                return image
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as exc:
        raise ValueError("We couldn't open that picture. Please try another image.") from exc
