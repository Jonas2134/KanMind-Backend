from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from ticket_app.models import Ticket

class TaskAccessMixin:
    """
    Mixin to enforce that the requesting user has access to a specific task.

    Provides:
        get_task(): Retrieves the Ticket instance by URL kwargs and verifies board membership.

    Intended for use in views handling task-related operations (e.g., comments).
    """
    def get_task(self):
        """
        Retrieve the Ticket object specified in URL kwargs and enforce access control.

        Steps:
        1. Extract 'task_id' or 'pk' from self.kwargs.
        2. Fetch the Ticket via get_object_or_404, raising 404 if not found.
        3. Verify that the request.user is either the board owner or a board member.
        4. Raise PermissionDenied if access is not allowed.

        Returns:
            Ticket: The retrieved and authorized Ticket instance.

        Raises:
            Http404: If no Ticket with the given ID exists.
            PermissionDenied: If the user is not the board owner or a member.
        """
        task_id = self.kwargs.get('task_id') or self.kwargs.get('pk')
        task = get_object_or_404(Ticket, pk=task_id)
        board = task.board
        user  = self.request.user
        if not (board.owner_id == user.id or board.members.filter(id=user.id).exists()):
            raise PermissionDenied("You must be a member of the board to manage comments.")
        return task
