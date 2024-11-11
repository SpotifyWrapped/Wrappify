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
            name="UserProfile",
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
                ("access_token", models.CharField(max_length=255)),
                ("refresh_token", models.CharField(max_length=255)),
                ("token_expires_at", models.DateTimeField()),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DuoWrapped",
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
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("combined_top_genres", models.JSONField(blank=True, default=dict)),
                ("combined_top_artists", models.JSONField(blank=True, default=dict)),
                ("combined_top_tracks", models.JSONField(blank=True, default=dict)),
                (
                    "invitee",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="duo_wrapped_received",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "inviter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="duo_wrapped_invitations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

