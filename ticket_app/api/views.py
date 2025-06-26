from rest_framework import generics, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from boards_app.models import Board
from ticket_app.models import Ticket
from .serializers import TicketSerializer, TicketCreateSerializer, TicketPatchSerializer, TicketPatchSuccessSerializer

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


class TaskAssigneeView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Ticket.objects.filter(assignee=user)
    
    def list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskReviewerView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Ticket.objects.filter(reviewer=user)
    
    def list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {'detail': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
        ticket = get_object_or_404(Ticket, pk=task_id)
        board = ticket.board
        user = self.request.user
        if not (board.owner_id == user.id or board.members.filter(id=user.id).exists()):
            raise PermissionDenied("You must be a member of the board to change or delete this task.")
        return ticket
    
    def patch(self, request, *args, **kwargs):
        ticket = self.get_object()
        board = ticket.board
        user = request.user
        data = request.data

        assignee_id = data.get('assignee_id')
        if assignee_id is not None:
            get_object_or_404(User, pk=assignee_id)
            if not (board.owner_id == assignee_id or board.members.filter(id=assignee_id).exists()):
                return Response(
                    {'assignee_id': 'Assignee must be owner or member of the board.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        reviewer_id = data.get('reviewer_id')
        if reviewer_id is not None:
            get_object_or_404(User, pk=reviewer_id)
            if not (board.owner_id == reviewer_id or board.members.filter(id=reviewer_id).exists()):
                return Response(
                    {'reviewer_id': 'Reviewer must be owner or member of the board.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(ticket, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated = serializer.save()
        except Exception:
            return Response(
                {'detail': 'Internal server error when updating the task.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            output_serializer = TicketPatchSuccessSerializer(updated, context={'request': request})
            return Response(output_serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {'detail': 'Internal server error when returning the updated task.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, *args, **kwargs):
        ticket = self.get_object()
        try:
            self.perform_destroy(ticket)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {'detail': 'Internal server error when deleting the task.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_destroy(self, instance):
        instance.delete()
