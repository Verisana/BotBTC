from django.db import models
from django.contrib.auth.models import AbstractUser 


class Profile(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
    api_key = models.ForeignKey('profiles.APIKeyModel', on_delete=models.CASCADE,
                                blank=True, null=True)

class APIKeyModel(models.Model):
    name = models.CharField(max_length=64)
    api_key = models.CharField(max_length=32)
    api_secret = models.CharField(max_length=64)
    username = models.ForeignKey('Profile', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
