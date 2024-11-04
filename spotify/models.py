from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Article(models.Model):
    title = models.CharField(_('title'), max_length=100) 
    content = models.TextField(_('content'))
