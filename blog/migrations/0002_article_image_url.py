# Generated by Django 4.2.16 on 2024-10-03 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="article", name="image_url", field=models.URLField(blank=True),
        ),
    ]