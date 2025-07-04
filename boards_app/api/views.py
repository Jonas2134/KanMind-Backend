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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        allowed_ids = Board.objects.filter(Q(owner=user) | Q(members=user)).values_list('id', flat=True)
        return Board.objects.filter(id__in=allowed_ids).distinct()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BoardCreateSerializer
        return BoardListSerializer

    @handle_exceptions(action='retrieving boards')
    def list(self, request, *args, **kwargs):        
        qs = self.annotated_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions(action='creating board')
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.validate_members(request.data.get('members', []))
        board = serializer.save(owner=request.user)
        qs = self.annotated_queryset(Board.objects.filter(pk=board.pk)).first()
        output_serializer = BoardListSerializer(qs, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def validate_members(self, member_ids):
        if not isinstance(member_ids, list):
            raise ValidationError({'members': 'Must be a list of user IDs.'})
        existing = set(User.objects.filter(id__in=member_ids).values_list('id', flat=True))
        missing = set(member_ids) - existing
        if missing:
            raise ValidationError({'members':
                f'The following members do not exist: {sorted(missing)}'})
        if self.request.user.id in member_ids:
            raise ValidationError({'members': 'You cannot add yourself as a member.'})

    def annotated_queryset(self, qs):
        return qs.annotate(
            member_count=Count('members', distinct=True),
            ticket_count=Count('tickets', distinct=True),
            tasks_to_do_count=Count('tickets', filter=Q(tickets__status='todo')),
            tasks_high_prio_count=Count('tickets', filter=Q(tickets__priority='high')),
        )


class BoardDetailPatchDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        allowed_ids = Board.objects.filter(Q(owner=user) | Q(members=user)).values_list('id', flat=True)
        return Board.objects.filter(id__in=allowed_ids).distinct()

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            board = Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            raise NotFound(detail="Board not found.")
        user = self.request.user
        if not (board.owner_id == user.id or board.members.filter(id=user.id).exists()):
            raise PermissionDenied(detail="You do not have permission to view/modify this board.")
        self.check_object_permissions(self.request, board)
        return board

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BoardUpdateSerializer
        return BoardDetailSerializer

    @handle_exceptions(action='retrieving board')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @handle_exceptions(action='updating board')
    def update(self, request, *args, **kwargs):
        board = self.get_object()
        updated = self.perform_update(board, request.data)
        return Response(self.serialize_detail(updated), status=status.HTTP_200_OK)

    @handle_exceptions(action='deleting board')
    def destroy(self, request, *args, **kwargs):
        board = self.get_object()
        self.check_delete_permission(board)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, board, data):
        serializer = self.get_serializer(board, data=data, partial=True)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        return serializer.save()

    def serialize_detail(self, board):
        return BoardDetailAfterUpdateSerializer(board, context={'request': self.request}).data

    def check_delete_permission(self, board):
        if board.owner_id != self.request.user.id:
            raise PermissionDenied('Not authorized to delete this board.')
