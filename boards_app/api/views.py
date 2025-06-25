from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.db.models import Count, Q

from boards_app.models import Board
from .serializers import BoardListSerializer, BoardCreateSerializer, BoardDetailSerializer, BoardDetailAfterUpdateSerializer, BoardUpdateSerializer

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


    def list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset().annotate(
                member_count=Count('members', distinct=True),
                ticket_count=Count('tickets', distinct=True),
                tasks_to_do_count=Count('tickets', filter=Q(tickets__status='todo')),
                tasks_high_prio_count=Count('tickets', filter=Q(tickets__priority='high')),
            )
            serializer = self.get_serializer(qs, many=True)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except Exception as err:
           return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            board = serializer.save()
        except Exception as err:
            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            qs = Board.objects.filter(id__in=[board.pk]).annotate(
                member_count=Count('members', distinct=True),
                ticket_count=Count('tickets', distinct=True),
                tasks_to_do_count=Count('tickets', filter=Q(tickets__status='todo')),
                tasks_high_prio_count=Count('tickets', filter=Q(tickets__priority='high')),
            ).first()
            output_serializer = BoardListSerializer(qs, context={'request': request})
            return Response(
                output_serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as err:
            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            board = serializer.save()
        except Exception:
            return Response(
                {'detail': 'Internal server error when updating the board.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            detail_serializer = BoardDetailAfterUpdateSerializer(board, context={'request': request})
            return Response(
                detail_serializer.data,
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'detail': 'Internal server error after update.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        if instance.owner_id != user.id:
            return Response(
                {'detail': 'Not authorized to delete this board.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {'detail': 'Internal server error when deleting the board.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
