import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'litloop_project.settings.dev')
django.setup()

from django.apps import apps
from django.db import models

def search_db(search_str):
    print(f"Searching for '{search_str}' in all models...")
    for model in apps.get_models():
        fields = [f.name for f in model._meta.fields if isinstance(f, (models.CharField, models.TextField))]
        if not fields:
            continue
        
        # Build query
        q = models.Q()
        for field in fields:
            q |= models.Q(**{f"{field}__contains": search_str})
        
        results = model.objects.filter(q)
        if results.exists():
            print(f"\nModel: {model.__name__} (Table: {model._meta.db_table})")
            for obj in results:
                found_fields = []
                for field in fields:
                    val = getattr(obj, field)
                    if val and "litloop_bucket" in str(val) and "litloop_bucket_free" not in str(val):
                        found_fields.append(f"{field}: {val}")
                if found_fields:
                    print(f"  ID {obj.pk}: {', '.join(found_fields)}")

if __name__ == "__main__":
    search_db("litloop_bucket")
