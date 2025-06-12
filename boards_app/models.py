from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Board(models.Model):
    title = models.CharField(max_length=100)
    members = models.ManyToManyField(User, blank=True, related_name='boards')
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')

    def __str__(self):
        return self.title
