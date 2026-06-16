import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'litloop_project.settings.dev')
django.setup()

from photos.models import Photo
from videos.models import Video
from tracks.models import Track

def inspect_models():
    print("Inspecting Photo gcs_key...")
    for p in Photo.objects.exclude(gcs_key=None)[:3]:
        print(f"Photo {p.id}: {p.gcs_key}")

    print("\nInspecting Video gcs_key...")
    for v in Video.objects.exclude(gcs_key=None)[:3]:
        print(f"Video {v.id}: {v.gcs_key}")

    print("\nInspecting Track gcs_key...")
    for t in Track.objects.exclude(gcs_key=None)[:3]:
        print(f"Track {t.id}: {t.gcs_key}")

if __name__ == "__main__":
    inspect_models()
