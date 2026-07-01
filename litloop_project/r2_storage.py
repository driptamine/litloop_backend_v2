import io
import logging
import os
import posixpath
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_str

logger = logging.getLogger(__name__)


def _get_r2_client():
    import boto3
    account_id = getattr(settings, "R2_ACCOUNT_ID", None) or settings.R2_ACCESS_KEY_ID or "auto"
    endpoint_url = settings.R2_ENDPOINT_URL
    if not endpoint_url:
        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        region_name="auto",
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    )


def _public_url(key):
    public_url = settings.R2_PUBLIC_URL
    if public_url:
        return f"{public_url.rstrip('/')}/{key}"
    if settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY:
        client = _get_r2_client()
        return client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.R2_BUCKET_NAME, 'Key': key},
            ExpiresIn=604800,
        )
    endpoint = settings.R2_ENDPOINT_URL
    if not endpoint:
        account_id = getattr(settings, "R2_ACCOUNT_ID", None) or settings.R2_ACCESS_KEY_ID or "auto"
        endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
    return f"{endpoint}/{settings.R2_BUCKET_NAME}/{key}"


@deconstructible
class R2Storage(Storage):

    def __init__(self, *args, **kwargs):
        self._bucket = settings.R2_BUCKET_NAME
        self._access_key = settings.R2_ACCESS_KEY_ID
        self._secret_key = settings.R2_SECRET_ACCESS_KEY
        self._local_fallback = None

    def _get_backend(self):
        if self._local_fallback is not None:
            return self._local_fallback
        if self._bucket and self._access_key and self._secret_key:
            try:
                return _get_r2_client()
            except Exception as exc:
                logger.warning("R2 client init failed (%s), falling back to local storage", exc)
        else:
            logger.warning("R2 credentials not configured, falling back to local FileSystemStorage")
        self._local_fallback = FileSystemStorage()
        return self._local_fallback

    def _client(self):
        backend = self._get_backend()
        if isinstance(backend, FileSystemStorage):
            return backend
        return backend

    def _save(self, name, content):
        backend = self._get_backend()
        if isinstance(backend, FileSystemStorage):
            return backend._save(name, content)
        content.seek(0)
        backend.upload_fileobj(content, self._bucket, name)
        return name

    def _open(self, name, mode="rb"):
        backend = self._get_backend()
        if isinstance(backend, FileSystemStorage):
            return backend._open(name, mode)
        obj = backend.get_object(Bucket=self._bucket, Key=name)
        return io.BytesIO(obj["Body"].read())

    def delete(self, name):
        backend = self._get_backend()
        if isinstance(backend, FileSystemStorage):
            return backend.delete(name)
        backend.delete_object(Bucket=self._bucket, Key=name)

    def exists(self, name):
        backend = self._get_backend()
        if isinstance(backend, FileSystemStorage):
            return backend.exists(name)
        try:
            backend.head_object(Bucket=self._bucket, Key=name)
            return True
        except backend.exceptions.ClientError:
            return False

    def url(self, name):
        backend = self._get_backend()
        if isinstance(backend, FileSystemStorage):
            return backend.url(name)
        return _public_url(name)

    def size(self, name):
        backend = self._get_backend()
        if isinstance(backend, FileSystemStorage):
            return backend.size(name)
        obj = backend.head_object(Bucket=self._bucket, Key=name)
        return obj["ContentLength"]

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            dir_name, file_name = posixpath.split(name)
            file_root, file_ext = posixpath.splitext(file_name)
            name = os.path.join(dir_name, f"{file_root}_{uuid.uuid4().hex}{file_ext}")
        return force_str(name)

    def get_valid_name(self, name):
        return force_str(name).strip().replace("\\", "/")

    def listdir(self, path):
        backend = self._get_backend()
        if isinstance(backend, FileSystemStorage):
            return backend.listdir(path)
        raise NotImplementedError
