import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'litloop_project.settings.dev')
django.setup()

from users.models import User
from django.conf import settings

def migrate_avatars():
    old_bucket = "litloop_bucket"
    new_bucket = settings.GCS_BUCKET_NAME
    
    if not new_bucket:
        print("Error: GCS_BUCKET_NAME not found in settings.")
        return

    print(f"Migrating avatars from {old_bucket} to {new_bucket}...")
    
    users = User.objects.filter(avatar__contains=old_bucket).exclude(avatar__contains=new_bucket)
    count = users.count()
    print(f"Found {count} users with old bucket avatar URL.")
    
    for user in users:
        old_url = user.avatar
        new_url = old_url.replace(old_bucket, new_bucket)
        user.avatar = new_url
        user.save(update_fields=['avatar'])
        print(f"Updated user {user.id}: {old_url} -> {new_url}")

    print("Migration complete.")

if __name__ == "__main__":
    migrate_avatars()
