import io
import uuid
import logging
import requests
from chats.gcs import gcs_upload_file

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

        file_obj = io.BytesIO(resp.content)
        public_url = gcs_upload_file(file_obj, filename, content_type=ct or "image/jpeg")
        logger.info("Avatar uploaded to GCS: %s", public_url)
        return public_url

    except Exception as e:
        logger.error("Failed to download/upload avatar: %s", e)
        return image_url
