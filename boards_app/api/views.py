from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from django.db.models import Count, Q
from django.contrib.auth.models import User

from boards_app.models import Board
from .serializers import BoardListSerializer, BoardCreateSerializer, BoardDetailSerializer, BoardDetailAfterUpdateSerializer, BoardUpdateSerializer
from core.decorators import handle_exceptions

class BoardListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list all boards the user can access or create a new board.

    GET returns all boards where the user is owner or member.
    POST allows creating a board with a title and optional members.

    Attributes:
        permission_classes (list): Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Determine which boards the requesting user can access.

        Returns:
            QuerySet: Boards owned by or shared with the user.
        """
        user = self.request.user
        allowed_ids = Board.objects.filter(Q(owner=user) | Q(members=user)).values_list('id', flat=True)
        return Board.objects.filter(id__in=allowed_ids).distinct()

    def get_serializer_class(self):
        """
        Select serializer based on HTTP method.

        Returns:
            Serializer class for list (BoardListSerializer) or create (BoardCreateSerializer).
        """
        if self.request.method == 'POST':
            return BoardCreateSerializer
        return BoardListSerializer

    @handle_exceptions(action='retrieving boards')
    def list(self, request, *args, **kwargs):
        """
        Handle GET request to list boards.

        Returns:
            Response: HTTP 200 with serialized board list.
        """
        qs = self.annotated_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions(action='creating board')
    def create(self, request, *args, **kwargs):
        """
        Handle POST request to create a board.

        Validates members list and assigns the requesting user as owner *and* as member.

        Returns:
            Response: HTTP 201 with serialized board data, or 400 on validation error.
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.validate_members(request.data.get('members', []))
        board = serializer.save(owner=request.user)
        if request.user not in board.members.all():
            board.members.add(request.user)
        qs = self.annotated_queryset(Board.objects.filter(pk=board.pk)).first()
        output_serializer = BoardListSerializer(qs, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def validate_members(self, member_ids):
        """
        Ensure provided member IDs form a valid list of existing users, excluding self.

        Args:
            member_ids (list): List of user IDs to add as members.

        Raises:
            ValidationError: If input is not a list, contains non‑existent IDs, or includes the owner.
        """
        if not isinstance(member_ids, list):
            raise ValidationError({'members': 'Must be a list of user IDs.'})
        existing = set(User.objects.filter(id__in=member_ids).values_list('id', flat=True))
        missing = set(member_ids) - existing
        if missing:
            raise ValidationError({'members':
                f'The following members do not exist: {sorted(missing)}'})

    def annotated_queryset(self, qs):
        """
        Annotate boards with counts for members and tickets.

        Args:
            qs (QuerySet): Base Board queryset.

        Returns:
            QuerySet: Annotated with member_count, ticket_count, tasks_to_do_count, tasks_high_prio_count.
        """
        return qs.annotate(
            member_count=Count('members', distinct=True),
            ticket_count=Count('tickets', distinct=True),
            tasks_to_do_count=Count('tickets', filter=Q(tickets__status='todo')),
            tasks_high_prio_count=Count('tickets', filter=Q(tickets__priority='high')),
        )


class BoardDetailPatchDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete a single board.

    GET returns board details; PUT/PATCH updates title or members; DELETE removes the board if owned.

    Attributes:
        permission_classes (list): Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Fetch the Board instance ensuring the user has access.

        Raises:
            NotFound: If no board with given pk exists.
            PermissionDenied: If user lacks ownership or membership.

        Returns:
            Board: The requested board.
        """
        pk = self.kwargs.get('pk')
        user = self.request.user
        try:
            board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            raise NotFound(detail="Board not found.")
        if not (board.owner_id == user.id or board.members.filter(id=user.id).exists()):
            raise PermissionDenied(detail="You do not have permission to view/modify this board.")
        return board

    def get_serializer_class(self):
        """
        Select serializer based on HTTP method.

        Returns:
            Serializer class for detail/retrieve (BoardDetailSerializer) or update (BoardUpdateSerializer).
        """
        if self.request.method in ['PUT', 'PATCH']:
            return BoardUpdateSerializer
        return BoardDetailSerializer

    @handle_exceptions(action='retrieving board')
    def retrieve(self, request, *args, **kwargs):
        """
        Handle GET request to retrieve board details.

        Returns:
            Response: HTTP 200 with serialized board detail.
        """
        return super().retrieve(request, *args, **kwargs)

    @handle_exceptions(action='updating board')
    def update(self, request, *args, **kwargs):
        """
        Handle PUT/PATCH request to update a board.

        Validates and applies partial updates, then returns updated detail.

        Returns:
            Response: HTTP 200 with serialized updated board data.
        """
        board = self.get_object()
        updated = self.perform_update(board, request.data)
        return Response(self.serialize_detail(updated), status=status.HTTP_200_OK)

    @handle_exceptions(action='deleting board')
    def destroy(self, request, *args, **kwargs):
        """
        Handle DELETE request to remove a board.

        Ensures only the owner can delete.

        Returns:
            Response: HTTP 204 on successful deletion.
        """
        board = self.get_object()
        self.check_delete_permission(board)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, board, data):
        """
        Validate and apply updates to a board instance,
        then ensure the owner is also in the members list.

        Args:
            board (Board): The board to update.
            data (dict): Partial data containing updated fields.

        Returns:
            Board: The updated board instance.

        Raises:
            ValidationError: If serializer validation fails.
        """
        serializer = self.get_serializer(board, data=data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        updadet_board = serializer.save()
        owner = board.owner.id
        if owner not in updadet_board.members.all():
            updadet_board.members.add(owner)
        return updadet_board

    def serialize_detail(self, board):
        """
        Serialize a board for detailed output after update.

        Args:
            board (Board): The board instance.

        Returns:
            dict: Serialized data as Python dict.
        """
        return BoardDetailAfterUpdateSerializer(board, context={'request': self.request}).data

    def check_delete_permission(self, board):
        """
        Ensure only the board owner can delete the board.

        Args:
            board (Board): The board being deleted.

        Raises:
            PermissionDenied: If the requesting user is not the owner.
        """
        if board.owner_id != self.request.user.id:
            raise PermissionDenied('Not authorized to delete this board.')
