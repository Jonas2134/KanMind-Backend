from django.db import models
from django.conf import settings

# Create your models here.

class Board(models.Model):
    title = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='boards')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_boards')

    def __str__(self):
        return self.title
