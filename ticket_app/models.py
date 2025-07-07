from django.db import models
from django.contrib.auth.models import User

from boards_app.models import Board

# Create your models here.

class Ticket(models.Model):
    """
    Represents a single task (ticket) on a Kanban board.

    Attributes:
        board (Board): The board this ticket belongs to.
        title (str): Short summary of the task.
        description (str): Detailed description of the task (optional).
        status (str): Current workflow state, one of:
            - 'to-do'
            - 'in-progress'
            - 'review'
            - 'done'
        priority (str): Priority level, one of:
            - 'low'
            - 'medium'
            - 'high'
        assignee (User): User assigned to work on the ticket (optional).
        reviewer (User): User responsible for reviewing the completed ticket (optional).
        due_date (date): Deadline for the ticket (optional).
    """
    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    board = models.ForeignKey(Board, related_name='tickets', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    assignee = models.ForeignKey(User, related_name='assigned_tickets', on_delete=models.SET_NULL, null=True, blank=True)
    reviewer = models.ForeignKey(User, related_name='review_tickets', on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        """
        Return a human-readable representation of the Ticket.

        Returns:
            str: String in the format "Task <id> on Board <board_id>".
        """
        return f"Task {self.id} on Board {self.board_id}"
