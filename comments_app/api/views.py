from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from .serializers import CommentBaseSerializer
from .mixins import TaskAccessMixin
from core.decorators import handle_exceptions
from comments_app.models import Comment

class CommentListCreateView(generics.ListCreateAPIView, TaskAccessMixin):
    """
    API endpoint to list all comments on a task or create a new comment.

    GET:
        - Returns all comments for the specified task, ordered by creation time.
    POST:
        - Creates a new comment on the specified task, setting the request user as author.

    Attributes:
        serializer_class (Serializer): Serializer for comment input/output.
        permission_classes (list): Requires authentication.
    """
    serializer_class = CommentBaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve the queryset of comments for the current task.

        Returns:
            QuerySet: Comments belonging to the task, ordered by created_at.
        """
        task = self.get_task()
        return Comment.objects.filter(task=task).order_by('created_at')

    @handle_exceptions(action='retrieving comments')
    def list(self, request, *args, **kwargs):
        """
        Handle GET request to list comments.

        Returns:
            Response: HTTP 200 with serialized list of comments.
        """
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """
        Save a new comment instance with author and task set.

        Args:
            serializer (Serializer): Initialized serializer with validated data.
        """
        task = self.get_task()
        serializer.save(author=self.request.user, task=task)

    @handle_exceptions(action='creating comment')
    def create(self, request, *args, **kwargs):
        """
        Handle POST request to create a comment.

        Returns:
            Response: HTTP 201 with serialized comment data on success; HTTP 400 on validation errors.
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        comment = serializer.instance
        output  = CommentBaseSerializer(comment, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class CommentDestroyView(generics.DestroyAPIView, TaskAccessMixin):
    """
    API endpoint to delete a specific comment from a task.

    DELETE:
        - Deletes the comment with the given comment_id under the specified task.

    Attributes:
        permission_classes (list): Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    @handle_exceptions(action='deleting comment')
    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE request to remove a comment.

        Args:
            request (Request): DRF request object.
            comment_id (int): URL parameter for comment primary key.

        Returns:
            Response: HTTP 204 on successful deletion; raises NotFound if the comment does not exist.
        """
        task = self.get_task()
        try:
            comment_id = self.kwargs.get('comment_id')
            comment = Comment.objects.get(pk=comment_id, task=task)
        except Comment.DoesNotExist:
            raise NotFound('Comment not found.')
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
