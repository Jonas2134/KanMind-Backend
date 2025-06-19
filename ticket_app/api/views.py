from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .serializers import TicketSerializer

class TicketView(generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
