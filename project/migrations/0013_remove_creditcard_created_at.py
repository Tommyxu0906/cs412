# Generated by Django 4.2.16 on 2024-12-03 21:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0012_cartitem_quantity"),
    ]

    operations = [
        migrations.RemoveField(model_name="creditcard", name="created_at",),
    ]
