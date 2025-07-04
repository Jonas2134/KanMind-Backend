from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from .serializers import CommentBaseSerializer
from .mixins import TaskAccessMixin
from core.decorators import handle_exceptions
from comments_app.models import Comment

class CommentListCreateView(generics.ListCreateAPIView, TaskAccessMixin):
    serializer_class = CommentBaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task = self.get_task()
        return Comment.objects.filter(task=task).order_by('created_at')

    @handle_exceptions(action='retrieving comments')
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        task = self.get_task()
        serializer.save(author=self.request.user, task=task)

    @handle_exceptions(action='creating comment')
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        comment = serializer.instance
        output  = CommentBaseSerializer(comment, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class CommentDestroyView(generics.DestroyAPIView, TaskAccessMixin):
    permission_classes = [IsAuthenticated]

    @handle_exceptions(action='deleting comment')
    def delete(self, request, *args, **kwargs):
        task = self.get_task()
        try:
            comment_id = self.kwargs.get('comment_id')
            comment = Comment.objects.get(pk=comment_id, task=task)
        except Comment.DoesNotExist:
            raise NotFound('Comment not found.')
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
