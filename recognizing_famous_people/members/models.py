from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CustomUser(User):
    score = models.IntegerField(default=0)

class FamousPerson(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='famous_people/')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Famous People"

