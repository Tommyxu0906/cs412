# Generated by Django 4.2.16 on 2024-11-28 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0011_order_quantity_order_total_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="cartitem",
            name="quantity",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
