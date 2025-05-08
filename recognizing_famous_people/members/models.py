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

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    SKIN_COLOR_CHOICES = [
        ('white', 'White'),
        ('black', 'Black'),
        ('asian', 'Asian'),
        ('brown', 'Brown'),
    ]

    name = models.CharField(max_length=100)
    image = models.ImageField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    skin_color = models.CharField(max_length=10, choices=SKIN_COLOR_CHOICES, default='white')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Famous People"

