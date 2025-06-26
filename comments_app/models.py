from django.db import models
from django.contrib.auth.models import User

from ticket_app.models import Ticket

# Create your models here.

class Comment(models.Model):
    author = models.ForeignKey(User, related_name='author_comment', on_delete=models.CASCADE)
    task = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(max_length=255)
    created_at = models.DateField(null=True, blank=True)
