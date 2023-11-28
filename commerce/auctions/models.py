from django.contrib.auth.models import AbstractUser
from django.db import models

CATEGORIES = []
class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=100)
    price = models.FloatField()
    image_url = models.URLField(blank=True)
    active = models.CharField(max_length=64, default="yes")
    category = models.CharField(max_length=64, blank=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")

    def __str__(self):
        return f"{self.title}"
