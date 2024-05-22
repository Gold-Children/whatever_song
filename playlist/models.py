from django.db import models
from django.conf import settings


class Playlist(models.Model):
    link = models.URLField()
    save = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='playlist')

