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
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
    

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BoardCreateSerializer
        return BoardListSerializer

    
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset().annotate(
            member_count=Count('members', distinct=True),
            ticket_count=Count('tickets', distinct=True),
            tasks_to_do_count=Count('tickets', filter=Q(tickets__status='todo')),
            tasks_high_prio_count=Count('tickets', filter=Q(tickets__priority='high')),
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()
        output_serializer = BoardSerializer(board, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
