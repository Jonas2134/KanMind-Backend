from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from boards_app.models import Board
from .serializers import TicketSerializer, TicketCreateSerializer

class TicketPostView(generics.CreateAPIView):
    serializer_class = TicketCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer, board):
        user = self.request.user
        if not (board.owner_id == user.id or board.members.filter(id=user.id).exists()):
            raise PermissionDenied(detail="You are not authorized to create tickets on this board.")
        serializer.save()
    
    def create(self, request, *args, **kwargs):
        data = request.data

        board_id = data.get('board')
        if board_id is None:
            return Response(
                {'board': 'This field is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        board = get_object_or_404(Board, pk=board_id)

        assignee_id = data.get('assignee_id')
        if assignee_id is not None:
            get_object_or_404(User, pk=assignee_id)

        reviewer_id = data.get('reviewer_id')
        if reviewer_id is not None:
            get_object_or_404(User, pk=reviewer_id)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer, board=board)
        except PermissionDenied as e:
            return Response(
                {'detail': str(e.detail)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception:
            return Response(
                {'detail': 'Internal server error when creating the ticket.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        ticket = serializer.instance

        try:
            output_serializer = TicketSerializer(ticket, context={'request': request})
            return Response(
                output_serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception:
            return Response(
                {'detail': 'Internal server error when returning the ticket.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
