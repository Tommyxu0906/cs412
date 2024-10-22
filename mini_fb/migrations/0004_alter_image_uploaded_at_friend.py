# Generated by Django 4.2.16 on 2024-10-22 14:23

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("mini_fb", "0003_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="uploaded_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="Friend",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "profile1",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="friends1",
                        to="mini_fb.profile",
                    ),
                ),
                (
                    "profile2",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="friends2",
                        to="mini_fb.profile",
                    ),
                ),
            ],
        ),
    ]
