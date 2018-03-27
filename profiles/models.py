from django.db import models
from django.contrib.auth.models import AbstractUser

class Profile(AbstractUser):
    email_confirmed = models.BooleanField(default=False)
