import os
import django
from django.core.management import call_command

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'litloop_project.settings.dev')

# Initialize Django
django.setup()

def delete_all_data():
    print("WARNING: This will delete all data from all tables while keeping the schema intact.")
    try:
        # 'flush' removes all data from the database and re-executes post-migration signals.
        # It is the safest way to reset a database to an empty state.
        call_command('flush', interactive=False)
        print("Successfully deleted all data from all models.")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    delete_all_data()
