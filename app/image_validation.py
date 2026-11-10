"""Validate image bytes before storing or sending to the AI provider."""
from io import BytesIO
from PIL import Image, UnidentifiedImageError

class InvalidImage(ValueError):
    pass

FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}

def validate_image(data: bytes, max_bytes: int = 10 * 1024 * 1024) -> str:
    if not data or len(data) > max_bytes:
        raise InvalidImage("Invalid image size")
    try:
        with Image.open(BytesIO(data)) as image:
            if image.format not in FORMATS:
                raise InvalidImage("Unsupported image format")
            if image.width < 64 or image.height < 64 or image.width * image.height > 30_000_000:
                raise InvalidImage("Invalid image dimensions")
            mime = FORMATS[image.format]
            image.verify()
            return mime
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise InvalidImage("Corrupt or unsafe image") from exc
