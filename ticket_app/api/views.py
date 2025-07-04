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
    serializer_class = TicketCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_board(self):
        board_id = self.request.data.get('board')
        if board_id is None:
            raise ValidationError({'board': 'This field is required.'})
        try:
            return Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise NotFound('Board not found.')

    def validate_user(self, field: str, message: str):
        user_id = self.request.data.get(field)
        if user_id is not None:
            try:
                User.objects.get(pk=user_id)
            except User.DoesNotExist:
                raise NotFound(message)

    def perform_create(self, serializer, board):
        user = self.request.user
        if not (board.owner_id == user.id or board.members.filter(id=user.id).exists()):
            raise PermissionDenied(detail="You are not authorized to create tickets on this board.")
        serializer.save(board=board)

    @handle_exceptions(action='creating ticket')
    def create(self, request, *args, **kwargs):
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
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    role: str

    def get_queryset(self):
        user = self.request.user
        if self.role == 'assignee':
            return Ticket.objects.filter(assignee=user)
        if self.role == 'reviewer':
            return Ticket.objects.filter(reviewer=user)
        raise NotFound('Invalid role specification.')

    @handle_exceptions(action='retrieving tasks')
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskAssigneeView(TaskRoleListView):
    role = 'assignee'


class TaskReviewerView(TaskRoleListView):
    role = 'reviewer'


class TicketPatchDeleteView(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketPatchSerializer
    queryset = Ticket.objects.all()

    def get_object(self):
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
        ticket = self.get_object()
        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
