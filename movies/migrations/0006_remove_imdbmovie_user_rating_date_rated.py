# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0005_imdbmovierating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imdbmovie',
            name='date_rated',
        ),
        migrations.RemoveField(
            model_name='imdbmovie',
            name='user_rating',
        ),
    ]
