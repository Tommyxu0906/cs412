# Generated by Django 4.2.16 on 2024-11-19 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0004_order"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing", name="sold", field=models.BooleanField(default=False),
        ),
    ]
