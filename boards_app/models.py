from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Board(models.Model):
    """
    Represents a Kanban board.

    A Board has a title, an owner, and zero or more members.
    Tracks creation and update timestamps automatically.

    Fields:
        title (str): The name of the board, max length 255.
        owner (User): User who created and owns the board.
        members (QuerySet[User]): Users who have access to the board (many-to-many).
        created_at (datetime): Timestamp when the board was first created.
        updated_at (datetime): Timestamp when the board was last modified.
    """
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='owned_boards', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, blank=True, related_name='boards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Return a human-readable representation of the Board.

        Returns:
            str: String in the format "Board <id>: <title>".
        """
        return f"Board {self.id}: {self.title}"
