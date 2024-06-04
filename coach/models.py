from django.db import models
from django.conf import settings
import uuid
import os

def upload_to_graph(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('graphs', filename)

class Coach(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    youtube_url = models.URLField()
    youtube_title = models.TextField()
    input_file = models.FileField(upload_to='uploads/')
    high_pitch_score = models.FloatField()
    low_pitch_score = models.FloatField()
    pitch_score = models.FloatField()
    message = models.TextField()
    graph = models.ImageField(upload_to=upload_to_graph)
    created_at = models.DateTimeField(auto_now_add=True)
