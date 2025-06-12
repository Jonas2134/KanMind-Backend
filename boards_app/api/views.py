from rest_framework import generics
from django.db import models

from boards_app.models import Board
from .serializers import BoardListSerializer

class BoardListView(generics.ListCreateAPIView):
    serializer_class = BoardListSerializer
    
    def get_queryset(self):
        user = self.request.user
        qs = Board.objects.filter(
            models.Q(owner_id=user) | models.Q(members=user)
        ).distinct()
        return qs
    
    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        if not board.members.filter(id=self.request.user.id).exists():
            board.members.add(self.request.user)
        
    