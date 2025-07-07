from rest_framework import serializers

from comments_app.models import Comment

class CommentBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for Comment instances, used in list and detail views.

    Serializes:
        - id: Primary key of the comment.
        - created_at: Timestamp when the comment was created.
        - author: Display name of the comment’s author.
        - content: Text content of the comment.
    """
    author     = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'created_at',
            'author',
            'content',
        ]
    
    def get_author(self, obj):
        """
        Retrieve a display name for the comment’s author.

        Attempts to return the user’s full name if available;
        otherwise falls back to the username or the user’s ID as string.

        Args:
            obj (Comment): The Comment instance being serialized.

        Returns:
            str: Full name, username, or user ID.
        """
        user = obj.author
        if hasattr(user, 'get_full_name'):
            full = user.get_full_name()
            if full:
                return full
        return getattr(user, 'username', str(user.id))
