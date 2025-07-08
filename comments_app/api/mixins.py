from rest_framework.exceptions import PermissionDenied, NotFound
from ticket_app.models import Ticket

class TaskAccessMixin:
    """
    Mixin to enforce that the requesting user has access to a specific task.

    Provides:
        get_task(): Retrieves the Ticket instance by primary key from URL kwargs
                    and enforces that the requesting user is either the board owner
                    or one of its members.
    """
    def get_task(self):
        """
        Retrieve the Ticket object specified in URL kwargs and enforce access control.

        Steps:
        1. Extract 'task_id' (or 'pk') from self.kwargs.
        2. Attempt to fetch the Ticket via Ticket.objects.get(); if not found, raise NotFound.
        3. Check that the request.user is either the board.owner or in board.members.
        4. If the check fails, raise PermissionDenied.

        Returns:
            Ticket: The retrieved and authorized Ticket instance.

        Raises:
            NotFound:         If no Ticket with the given ID exists.
            PermissionDenied: If the user is not the board owner or a member.
        """
        try:
            task_id = self.kwargs.get('task_id') or self.kwargs.get('pk')
            task = Ticket.objects.get(pk=task_id)
        except Ticket.DoesNotExist:
            raise NotFound('Task not found.')
        board = task.board
        user  = self.request.user
        if not (board.owner_id == user.id or board.members.filter(id=user.id).exists()):
            raise PermissionDenied("You must be a member of the board to manage comments.")
        return task
