"""S3-compatible object storage. MinIO in dev, AWS S3 + KMS in prod.

The `put_artifact` helper centralizes SSE-KMS encryption headers and SHA-256
fingerprinting so callers (uploads route, deliverable exporters, redaction
ledger) cannot accidentally skip them.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from functools import lru_cache
from typing import BinaryIO

import boto3
from botocore.client import Config

from app.settings import get_settings


@dataclass
class PutResult:
    storage_key: str
    sha256: str
    size_bytes: int


@lru_cache(maxsize=1)
def _client():  # type: ignore[no-untyped-def]
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url or None,
        aws_access_key_id=settings.s3_access_key or None,
        aws_secret_access_key=settings.s3_secret_key or None,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_bucket() -> None:
    """Idempotent bucket bootstrap. Called once on first storage touch in dev."""
    settings = get_settings()
    s3 = _client()
    try:
        s3.head_bucket(Bucket=settings.s3_bucket)
    except Exception:
        s3.create_bucket(Bucket=settings.s3_bucket)


def put_artifact(stream: BinaryIO, *, storage_key: str, content_type: str) -> PutResult:
    settings = get_settings()
    s3 = _client()

    # Stream-and-hash to avoid loading the full payload twice.
    sha = hashlib.sha256()
    data = stream.read()
    sha.update(data)
    size = len(data)

    extra: dict[str, str] = {"ContentType": content_type}
    if settings.s3_kms_key_id and settings.environment != "development":
        extra["ServerSideEncryption"] = "aws:kms"
        extra["SSEKMSKeyId"] = settings.s3_kms_key_id

    s3.put_object(Bucket=settings.s3_bucket, Key=storage_key, Body=data, **extra)
    return PutResult(storage_key=storage_key, sha256=sha.hexdigest(), size_bytes=size)


def get_artifact(storage_key: str) -> bytes:
    settings = get_settings()
    obj = _client().get_object(Bucket=settings.s3_bucket, Key=storage_key)
    return obj["Body"].read()
