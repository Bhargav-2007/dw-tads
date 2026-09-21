"""MinIO client with SHA-256 verification on upload and download."""

import hashlib
import io

from minio import Minio

from .logging import get_logger

log = get_logger("minio")


class MinioClient:
    def __init__(self, endpoint: str, access_key: str, secret_key: str,
                 secure: bool = False):
        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def ensure_bucket(self, bucket: str) -> None:
        """Create bucket if it does not exist."""
        if not self._client.bucket_exists(bucket):
            self._client.make_bucket(bucket)
            log.info("minio.bucket.created", bucket=bucket)

    def upload_with_hash(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload bytes to MinIO and return SHA-256 hex digest."""
        sha = hashlib.sha256(data).hexdigest()
        self._client.put_object(
            bucket, key, io.BytesIO(data),
            length=len(data), content_type=content_type,
        )
        log.info("minio.upload", bucket=bucket, key=key, sha256=sha[:16] + "…")
        return sha

    def download_with_verify(self, bucket: str, key: str,
                             expected_sha: str) -> bytes:
        """Download from MinIO and verify SHA-256. Raises ValueError on mismatch."""
        resp = self._client.get_object(bucket, key)
        try:
            data = resp.read()
        finally:
            resp.close()
            resp.release_conn()
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected_sha:
            raise ValueError(
                f"MinIO hash mismatch for {bucket}/{key}: "
                f"expected {expected_sha[:16]}…, got {actual[:16]}…"
            )
        return data

    def object_exists(self, bucket: str, key: str) -> bool:
        """Return True if the object exists in the bucket."""
        try:
            self._client.stat_object(bucket, key)
            return True
        except Exception:
            return False
