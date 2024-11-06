from django.db import models
from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields

# Create your models here.
class Article(models.Model):
    title = models.CharField(_('title'), max_length=100) 
    content = models.TextField(_('content'))

# class Course(TranslatableModel):
#     translations = TranslatedFields(
#         title = models.CharField(max_length=90)
#         description = models.TextField()
#         data = models.DateField()
#         price = models.DecimalField(max_digits=10, decimal_places=2)
#     )

#     def __str__(self):
#         return self.title

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SavedWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    time_range_label = models.CharField(max_length=50)
    total_playback_minutes = models.IntegerField()
    top_genres = models.JSONField()  # Store as JSON data
    top_tracks = models.JSONField()  # Store as JSON data
    avg_danceability = models.FloatField()
    avg_energy = models.FloatField()
    avg_valence = models.FloatField()
    top_artist = models.JSONField(default=dict)  # Uses an empty JSON object as default
    top_artists = models.JSONField()  # Store as JSON data
    recommendations = models.JSONField()  # Store as JSON data
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.user.username}"