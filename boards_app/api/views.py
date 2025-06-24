from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q

from boards_app.models import Board
from .serializers import BoardListSerializer, BoardCreateSerializer

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
