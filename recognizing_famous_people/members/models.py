from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CustomUser(User):
    score = models.IntegerField(default=0)

