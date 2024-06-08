from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    nickname = models.CharField(max_length=50)
    image = models.ImageField(upload_to='accounts/profile_pics/%Y/%m/%d/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)

class TempUser(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
