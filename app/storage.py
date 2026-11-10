"""S3-compatible private storage. Never accept arbitrary remote URLs from clients."""
import os
import re
from urllib.parse import urlparse

import boto3
from botocore.config import Config

ASSET_ID = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")
KINDS = {"uploads", "avatars", "garments", "tryons"}

class StorageError(RuntimeError):
    pass

class PrivateStorage:
    def __init__(self, client=None):
        self.bucket = os.getenv("S3_BUCKET", "")
        self.client = client or boto3.client(
            "s3", endpoint_url=os.getenv("S3_ENDPOINT_URL") or None,
            region_name=os.getenv("S3_REGION", "auto"),
            config=Config(signature_version="s3v4"))
        if not self.bucket:
            raise StorageError("S3_BUCKET must be configured")

    @staticmethod
    def key(kind: str, asset_id: str) -> str:
        if kind not in KINDS or not ASSET_ID.fullmatch(asset_id):
            raise StorageError("Invalid asset reference")
        return f"{kind}/{asset_id}"

    def upload_url(self, kind: str, asset_id: str, content_type: str = "image/jpeg") -> str:
        if kind not in {"uploads", "garments"}:
            raise StorageError("Uploads are restricted to source asset types")
        if content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise StorageError("Unsupported image content type")
        return self.client.generate_presigned_url(
            "put_object", Params={"Bucket": self.bucket, "Key": self.key(kind, asset_id),
                                  "ContentType": content_type}, ExpiresIn=300)

    def read_url(self, kind: str, asset_id: str, expires: int = 300) -> str:
        if not 1 <= expires <= 900:
            raise StorageError("Invalid URL lifetime")
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket, "Key": self.key(kind, asset_id)},
            ExpiresIn=expires)

    def put_image(self, kind: str, asset_id: str, image: bytes, content_type: str) -> None:
        if kind not in {"avatars", "tryons"}:
            raise StorageError("Output kind required")
        if content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise StorageError("Unsupported output format")
        if len(image) > 10 * 1024 * 1024:
            raise StorageError("Image too large")
        self.client.put_object(Bucket=self.bucket, Key=self.key(kind, asset_id),
                               Body=image, ContentType=content_type,
                               ServerSideEncryption="AES256")

    def delete(self, kind: str, asset_id: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=self.key(kind, asset_id))
