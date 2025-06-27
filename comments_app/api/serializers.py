from rest_framework import serializers

from comments_app.models import Comment

class CommentBaseSerializer(serializers.ModelSerializer):
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
        user = obj.author
        if hasattr(user, 'get_full_name'):
            full = user.get_full_name()
            if full:
                return full
        return getattr(user, 'username', str(user.id))