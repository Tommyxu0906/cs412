# Generated by Django 4.2.16 on 2024-11-28 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0009_order_delivery_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="quantity",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
