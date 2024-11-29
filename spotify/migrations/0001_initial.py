# Generated by Django 5.1.1 on 2024-11-18 21:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SavedWrap",
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
                ("title", models.CharField(max_length=255)),
                ("time_range_label", models.CharField(max_length=50)),
                ("total_playback_minutes", models.IntegerField()),
                ("top_genres", models.JSONField()),
                ("top_tracks", models.JSONField()),
                ("avg_danceability", models.FloatField()),
                ("avg_energy", models.FloatField()),
                ("avg_valence", models.FloatField()),
                ("top_artist", models.JSONField(default=dict)),
                ("top_artists", models.JSONField()),
                ("recommendations", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_game", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]