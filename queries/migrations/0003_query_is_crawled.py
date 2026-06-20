from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queries', '0002_googlequery_created_at_googlequery_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='is_crawled',
            field=models.BooleanField(default=False),
        ),
    ]
