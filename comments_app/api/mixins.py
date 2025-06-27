from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from ticket_app.models import Ticket

class TaskAccessMixin:
    def get_task(self):
        task_id = self.kwargs.get('task_id') or self.kwargs.get('pk')
        task = get_object_or_404(Ticket, pk=task_id)
        board = task.board
        user  = self.request.user
        if not (board.owner_id == user.id or board.members.filter(id=user.id).exists()):
            raise PermissionDenied("You must be a member of the board to manage comments.")
        return task
