from io import BytesIO
import pytest
from PIL import Image
from app.image_validation import InvalidImage, validate_image
from app.provider_download import _allowed

def test_image_validation():
    buffer = BytesIO()
    Image.new("RGB", (128, 128)).save(buffer, "JPEG")
    assert validate_image(buffer.getvalue()) == "image/jpeg"
    with pytest.raises(InvalidImage):
        validate_image(b"not-an-image")

def test_output_host_is_exact(monkeypatch):
    monkeypatch.setenv("FASHN_OUTPUT_HOSTS", "cdn.fashn.ai")
    assert _allowed("https://cdn.fashn.ai/result.jpg")
    assert not _allowed("https://cdn.fashn.ai.evil.test/result.jpg")
    assert not _allowed("http://cdn.fashn.ai/result.jpg")
    assert not _allowed("https://user:pass@cdn.fashn.ai/result.jpg")
