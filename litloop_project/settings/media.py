
TEMP_DIRECTORY = "/tmp"  # Don't use a temp directory inside BASE_DIR!!!
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_URL = "/static/"  # where js/css files are stored on the filesystem
# MEDIA_URL = "/media/"  # URL where static files are served from the server
MEDIA_URL = "/uploaded_media/"  # URL where static files are served from the server
STATIC_ROOT = BASE_DIR + "/static/"
# where uploaded + encoded media are stored
# MEDIA_ROOT = BASE_DIR + "/media_files/"
MEDIA_ROOT = BASE_DIR + "/uploaded_media/"
# MEDIA_URL = '/posts_image/'
# MEDIA_ROOT = 'posts_image'

MEDIA_UPLOAD_DIR = "original/"
MEDIA_ENCODING_DIR = "encoded/"
THUMBNAIL_UPLOAD_DIR = f"{MEDIA_UPLOAD_DIR}/thumbnails/"
SUBTITLES_UPLOAD_DIR = f"{MEDIA_UPLOAD_DIR}/subtitles/"
HLS_DIR = os.path.join(MEDIA_ROOT, "hls/")


# for videos, after that duration get split into chunks
# and encoded independently
CHUNKIZE_VIDEO_DURATION = 60 * 5
# aparently this has to be smaller than VIDEO_CHUNKIZE_DURATION
VIDEO_CHUNKS_DURATION = 60 * 4

# always get these two, even if upscaling
MINIMUM_RESOLUTIONS_TO_ENCODE = [240, 360]

FILE_STORAGE = "django.core.files.storage.DefaultStorage"
