from django.db import models
from django.contrib.auth.models import User

from ticket_app.models import Ticket

# Create your models here.

class Comment(models.Model):
    """
    Represents a comment left by a user on a ticket task.

    Fields:
        author (User): The user who created the comment.
        task (Ticket): The ticket task this comment belongs to.
        content (str): The text content of the comment, max length 255.
        created_at (datetime): Timestamp when the comment was created.
    """
    author = models.ForeignKey(User, related_name='author_comment', on_delete=models.CASCADE)
    task = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Return a human-readable representation of the Comment instance.

        Returns:
            str: String in the format "Comment <id> on Task <task_id>".
        """
        return f"Comment {self.id} on Task {self.task_id}"
