from django.db import models
from django.conf import settings


class Playlist(models.Model):
    link = models.URLField()
    save = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='playlist')

class SpotifyToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=50)