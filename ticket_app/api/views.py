from rest_framework import generics, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.response import Response
from django.contrib.auth.models import User

from boards_app.models import Board
from ticket_app.models import Ticket
from .serializers import TicketSerializer, TicketCreateSerializer, TicketPatchSerializer, TicketPatchSuccessSerializer
from core.decorators import handle_exceptions

class TicketPostView(generics.CreateAPIView):
    """
    API endpoint to create a new ticket on a board.

    POST:
      - Validates that 'board' is provided and exists.
      - Optionally validates 'assignee_id' and 'reviewer_id'.
      - Ensures the requesting user has permission to add tickets to the board.
      - Returns the created ticket with full details.

    Attributes:
        serializer_class (Serializer): Serializer for ticket creation.
        permission_classes (list): Requires authentication.
    """
    serializer_class = TicketCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_board(self):
        """
        Retrieve the Board from request data or raise an error.

        Raises:
            ValidationError: If 'board' field is missing.
            NotFound: If no Board with given ID exists.

        Returns:
            Board: The target board instance.
        """
        board_id = self.request.data.get('board')
        if board_id is None:
            raise ValidationError({'board': 'This field is required.'})
        try:
            return Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise NotFound('Board not found.')

    def validate_user(self, field: str, message: str):
        """
        Validate that a user ID in request data exists.

        Args:
            field (str): The field name ('assignee_id' or 'reviewer_id').
            message (str): Error message if lookup fails.

        Raises:
            NotFound: If the user does not exist.
        """
        user_id = self.request.data.get(field)
        if user_id is not None:
            try:
                User.objects.get(pk=user_id)
            except User.DoesNotExist:
                raise NotFound(message)

    def perform_create(self, serializer, board):
        """
        Save the new Ticket, ensuring permission on the board.

        Args:
            serializer (Serializer): Validated serializer instance.
            board (Board): The board to which the ticket belongs.

        Raises:
            PermissionDenied: If the user is not owner or member of the board.
        """
        user = self.request.user
        if not (board.owner_id == user.id or board.members.filter(id=user.id).exists()):
            raise PermissionDenied(detail="You are not authorized to create tickets on this board.")
        serializer.save(board=board)

    @handle_exceptions(action='creating ticket')
    def create(self, request, *args, **kwargs):
        """
        Handle POST request to create a ticket.

        Steps:
        1. Retrieve and validate the Board.
        2. Optionally validate assignee and reviewer IDs.
        3. Validate input data via serializer.
        4. Perform save and return full ticket details.

        Returns:
            Response: HTTP 201 with serialized ticket data.
        """
        board = self.get_board()
        self.validate_user('assignee_id', 'Assignee not found.')
        self.validate_user('reviewer_id', 'Reviewer not found.')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, board)

        ticket = serializer.instance
        output_serializer = TicketSerializer(ticket, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class TaskRoleListView(generics.ListAPIView):
    """
    Abstract API endpoint to list tickets for a given role.

    GET:
      - Returns tickets where the requesting user is either assignee or reviewer,
        depending on the `role` attribute.

    Attributes:
        serializer_class (Serializer): Serializer for ticket read operations.
        permission_classes (list): Requires authentication.
        role (str): Must be set to 'assignee' or 'reviewer' in subclasses.
    """
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    role: str

    def get_queryset(self):
        """
        Retrieve tickets filtered by role and requesting user.

        Raises:
            NotFound: If `role` is not 'assignee' or 'reviewer'.

        Returns:
            QuerySet: Tickets matching the user's role.
        """
        user = self.request.user
        if self.role == 'assignee':
            return Ticket.objects.filter(assignee=user)
        if self.role == 'reviewer':
            return Ticket.objects.filter(reviewer=user)
        raise NotFound('Invalid role specification.')

    @handle_exceptions(action='retrieving tasks')
    def list(self, request, *args, **kwargs):
        """
        Handle GET request to list tickets for the role.

        Returns:
            Response: HTTP 200 with serialized list of tickets.
        """
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskAssigneeView(TaskRoleListView):
    """
    API endpoint listing tickets assigned to the requesting user.
    """
    role = 'assignee'


class TaskReviewerView(TaskRoleListView):
    """
    API endpoint listing tickets awaiting review by the requesting user.
    """
    role = 'reviewer'


class TicketPatchDeleteView(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """
    API endpoint to update or delete an existing ticket.

    PATCH:
      - Validates that the user can modify the ticket (board membership).
      - Validates assignee/reviewer role assignments.
      - Returns updated ticket details.

    DELETE:
      - Deletes the ticket if the user has access.
      - Returns HTTP 204 on success.

    Attributes:
        permission_classes (list): Requires authentication.
        serializer_class (Serializer): Serializer for ticket patch.
        queryset (QuerySet): Base queryset of all tickets.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TicketPatchSerializer
    queryset = Ticket.objects.all()

    def get_object(self):
        """
        Retrieve the Ticket instance and enforce board access.

        Raises:
            NotFound: If the ticket does not exist.
            PermissionDenied: If the user is not owner or member of the board.

        Returns:
            Ticket: The requested ticket instance.
        """
        task_id = self.kwargs.get('pk')
        try:
            ticket = Ticket.objects.get(pk=task_id)
        except Ticket.DoesNotExist:
            raise NotFound('Ticket not found.')
        board = ticket.board
        user = self.request.user
        if not (board.owner_id == user.id or board.members.filter(id=user.id).exists()):
            raise PermissionDenied("You must be a member of the board to change or delete this task.")
        return ticket

    def validate_role(self, board, field: str, message: str):
        """
        Validate that a new assignee or reviewer ID is valid and has board access.

        Args:
            board (Board): Board to which the ticket belongs.
            field (str): Field name in request data ('assignee_id' or 'reviewer_id').
            message (str): Error message if validation fails.

        Raises:
            NotFound: If the user does not exist.
            ValidationError: If the user exists but lacks board membership.
        """
        user_id = self.request.data.get(field)
        if user_id is not None:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                raise NotFound(message)
            if not (board.owner_id == user.id or board.members.filter(id=user.id).exists()):
                raise ValidationError({field: message})

    @handle_exceptions(action='updating ticket')
    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH request to partially update a ticket.

        Steps:
        1. Retrieve and authorize the ticket.
        2. Validate new assignee and reviewer roles.
        3. Apply changes and return updated data.

        Returns:
            Response: HTTP 200 with serialized updated ticket.
        """
        ticket = self.get_object()
        board = ticket.board
        self.validate_role(board, 'assignee_id', 'Assignee must be owner or member of the board.')
        self.validate_role(board, 'reviewer_id', 'Reviewer must be owner or member of the board.')
        serializer = self.get_serializer(ticket, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        output_serializer = TicketPatchSuccessSerializer(updated, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions(action='deleting ticket')
    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE request to remove a ticket.

        Returns:
            Response: HTTP 204 on successful deletion.
        """
        ticket = self.get_object()
        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
