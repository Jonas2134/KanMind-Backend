from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.http import Http404

from .serializers import CommentBaseSerializer
from .mixins import TaskAccessMixin
from ticket_app.models import Ticket
from comments_app.models import Comment

class CommentListCreateView(generics.ListCreateAPIView, TaskAccessMixin):
    serializer_class = CommentBaseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        task = self.get_task()
        return Comment.objects.filter(task=task).order_by('created_at')
    
    def list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response(
                {'detail': 'Task not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied:
            return Response(
                {'detail': 'You are not allowed to comment this task.'},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception:
            return Response(
                {'detail': 'Internal server error when retrieving comments.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def perform_create(self, serializer):
        task = self.get_task()
        serializer.save(author=self.request.user, task=task)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.perform_create(serializer)
        except Http404:
            return Response(
                {'detail': 'Task not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied:
            return Response(
                {'detail': 'You are not allowed to comment this task.'},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception:
            return Response(
                {'detail': 'Internal server error when creating comment.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        comment = serializer.instance
        output  = CommentBaseSerializer(comment, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)
    

class CommentDestroyView(generics.DestroyAPIView, TaskAccessMixin):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            task = self.get_task()
        except Http404:
            return Response({'detail': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({'detail': str(e.detail)}, status=status.HTTP_403_FORBIDDEN)

        comment_id = self.kwargs.get('comment_id')

        try:
            comment = Comment.objects.get(pk=comment_id, task=task)
        except Comment.DoesNotExist:
            return Response({'detail': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {'detail': 'Internal server error when deleting comment.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
