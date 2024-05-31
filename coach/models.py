from django.db import models
from django.conf import settings

class Coach(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    youtube_url = models.URLField()
    input_file = models.FileField(upload_to='uploads/')
    high_pitch_score = models.FloatField()
    low_pitch_score = models.FloatField()
    pitch_score = models.FloatField()
    message = models.TextField()
    graph = models.ImageField(upload_to='graphs/')
    created_at = models.DateTimeField(auto_now_add=True)