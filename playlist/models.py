from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Playlist(models.Model):
    playlist_id = models.CharField(max_length=255, unique=True)     # 고유 플레이리스트 id
    link = models.URLField()
    save = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='playlist')
    zzim = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='zzim_playlists')
