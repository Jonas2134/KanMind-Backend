from rest_framework import generics, permissions
from django.db.models import Count, Q

from boards_app.models import Board
from .serializers import BoardSerializer

class BoardListView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Board.objects.filter(members=user).annotate(
            member_count=Count('members', distinct=True),
            ticket_count=Count('tickets', distinct=True),
            tasks_to_do_count=Count('tickets', filter=Q(tickets__status='todo')),
            tasks_high_prio_count=Count('tickets', filter=Q(tickets__priority='high')),
        )
        return qs
    
    def perform_create(self, serializer):
        serializer.save()
    