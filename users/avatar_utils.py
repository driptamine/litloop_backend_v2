import os
import io
import uuid
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def download_and_save_avatar(image_url: str, user_id: int) -> str:
    if not image_url:
        return image_url

    try:
        resp = requests.get(image_url, timeout=15)
        if resp.status_code != 200:
            logger.warning("Avatar download returned %s for %s", resp.status_code, image_url)
            return image_url

        ext = ".jpg"
        ct = resp.headers.get("content-type", "")
        if "png" in ct:
            ext = ".png"
        elif "gif" in ct:
            ext = ".gif"
        elif "webp" in ct:
            ext = ".webp"

        filename = f"avatars/{user_id}_{uuid.uuid4()}{ext}"

        if settings.DEBUG:
            abs_dir = os.path.join(settings.MEDIA_ROOT, "avatars")
            os.makedirs(abs_dir, exist_ok=True)
            abs_path = os.path.join(settings.MEDIA_ROOT, filename)
            with open(abs_path, "wb") as f:
                f.write(resp.content)
            local_url = f"{settings.MEDIA_URL}{filename}"
            logger.info("Avatar saved locally: %s", local_url)
            return local_url
        else:
            from uploader.gcs import gcs_get_client
            client = gcs_get_client()
            bucket_name = getattr(settings, "GCS_BUCKET_NAME", "litloop_bucket_free")
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_string(resp.content, content_type=ct or "image/jpeg")
            public_url = blob.public_url
            logger.info("Avatar uploaded to GCS: %s", public_url)
            return public_url

    except Exception as e:
        logger.error("Failed to download/upload avatar: %s", e)
        return image_url
