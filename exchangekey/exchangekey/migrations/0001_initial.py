# Generated by Django 4.2.13 on 2024-06-17 08:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Channel",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("accepted", models.BooleanField(default=False)),
                ("initial_sender_secret", models.TextField()),
                ("initial_recipient_secret", models.TextField()),
                (
                    "recipient_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_channels",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sender_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_channels",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SecretExchange",
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
                ("sender_secret", models.CharField(max_length=512)),
                (
                    "recipient_secret",
                    models.CharField(blank=True, max_length=512, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "channel",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="exchangekey.channel",
                    ),
                ),
            ],
        ),
    ]
