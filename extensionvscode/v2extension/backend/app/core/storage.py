"""
Storage abstraction layer.
Soporta almacenamiento local y S3/MinIO.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageBackend:
    """Abstract storage backend."""

    async def save_file(self, path: str, data: bytes) -> str:
        """Save file and return path/URL."""
        raise NotImplementedError

    async def read_file(self, path: str) -> bytes:
        """Read file from storage."""
        raise NotImplementedError

    async def delete_file(self, path: str) -> bool:
        """Delete file from storage."""
        raise NotImplementedError

    async def list_files(self, prefix: str) -> list[str]:
        """List files with given prefix."""
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    """
    Local filesystem storage.
    Usado temporalmente hasta que MinIO esté disponible.
    """

    def __init__(self, base_path: str = "./data/storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local storage initialized at: {self.base_path.absolute()}")

    async def save_file(self, path: str, data: bytes) -> str:
        """
        Save file to local filesystem.

        Args:
            path: Relative path (e.g., "events/2025/12/28/event_001.parquet")
            data: File content as bytes

        Returns:
            Absolute path to saved file
        """
        file_path = self.base_path / path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_bytes(data)
        logger.info(f"File saved: {file_path}")

        return str(file_path.absolute())

    async def read_file(self, path: str) -> bytes:
        """Read file from local filesystem."""
        file_path = self.base_path / path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return file_path.read_bytes()

    async def delete_file(self, path: str) -> bool:
        """Delete file from local filesystem."""
        file_path = self.base_path / path

        if file_path.exists():
            file_path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True

        return False

    async def list_files(self, prefix: str = "") -> list[str]:
        """List all files with given prefix."""
        search_path = self.base_path / prefix if prefix else self.base_path

        if not search_path.exists():
            return []

        files = []
        for file_path in search_path.rglob("*"):
            if file_path.is_file():
                # Return relative path from base_path
                rel_path = file_path.relative_to(self.base_path)
                files.append(str(rel_path))

        return sorted(files)


class MinIOStorageBackend(StorageBackend):
    """
    MinIO/S3 storage backend.
    Se usará cuando MinIO esté disponible online.
    """

    def __init__(self):
        """Initialize MinIO client."""
        try:
            from minio import Minio

            self.client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )

            # Crear buckets si no existen
            self._ensure_buckets()

            logger.info(f"MinIO storage initialized: {settings.MINIO_ENDPOINT}")

        except Exception as e:
            logger.error(f"Failed to initialize MinIO: {e}")
            raise

    def _ensure_buckets(self):
        """Create buckets if they don't exist."""
        for bucket in [settings.MINIO_BUCKET_EVENTS, settings.MINIO_BUCKET_SNAPSHOTS]:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                logger.info(f"Bucket created: {bucket}")

    async def save_file(self, path: str, data: bytes) -> str:
        """Save file to MinIO."""
        from io import BytesIO

        # Determine bucket from path
        if path.startswith("events/"):
            bucket = settings.MINIO_BUCKET_EVENTS
        elif path.startswith("snapshots/"):
            bucket = settings.MINIO_BUCKET_SNAPSHOTS
        else:
            bucket = settings.MINIO_BUCKET_EVENTS

        # Upload
        self.client.put_object(
            bucket,
            path,
            BytesIO(data),
            length=len(data),
        )

        url = f"{settings.MINIO_ENDPOINT}/{bucket}/{path}"
        logger.info(f"File uploaded to MinIO: {url}")

        return url

    async def read_file(self, path: str) -> bytes:
        """Read file from MinIO."""
        # Determine bucket
        if path.startswith("events/"):
            bucket = settings.MINIO_BUCKET_EVENTS
        elif path.startswith("snapshots/"):
            bucket = settings.MINIO_BUCKET_SNAPSHOTS
        else:
            bucket = settings.MINIO_BUCKET_EVENTS

        # Download
        response = self.client.get_object(bucket, path)
        data = response.read()
        response.close()
        response.release_conn()

        return data

    async def delete_file(self, path: str) -> bool:
        """Delete file from MinIO."""
        # Determine bucket
        if path.startswith("events/"):
            bucket = settings.MINIO_BUCKET_EVENTS
        elif path.startswith("snapshots/"):
            bucket = settings.MINIO_BUCKET_SNAPSHOTS
        else:
            bucket = settings.MINIO_BUCKET_EVENTS

        try:
            self.client.remove_object(bucket, path)
            logger.info(f"File deleted from MinIO: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    async def list_files(self, prefix: str = "") -> list[str]:
        """List files in MinIO."""
        # Listar en ambos buckets
        files = []

        for bucket in [settings.MINIO_BUCKET_EVENTS, settings.MINIO_BUCKET_SNAPSHOTS]:
            objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
            for obj in objects:
                files.append(obj.object_name)

        return sorted(files)


# ==================== Storage Factory ====================


def get_storage() -> StorageBackend:
    """
    Get configured storage backend.

    Por ahora retorna LocalStorageBackend.
    Cuando MinIO esté disponible, cambiar a MinIOStorageBackend.
    """
    storage_type = getattr(settings, "STORAGE_TYPE", "local")

    if storage_type == "s3" or storage_type == "minio":
        logger.info("Using MinIO storage backend")
        return MinIOStorageBackend()
    else:
        logger.info("Using local storage backend")
        storage_path = getattr(settings, "STORAGE_LOCAL_PATH", "./data/storage")
        return LocalStorageBackend(storage_path)


# Global storage instance
storage = get_storage()
