from rest_framework import serializers
from django.contrib.auth.models import User

from auth_app.api.serializers import UserNestedSerializer
from boards_app.models import Board


class TicketReadUsersMixin(serializers.Serializer):
    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)


class TicketWriteUsersMixin(serializers.Serializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee',
        allow_null=True, required=False
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer',
        allow_null=True, required=False
    )


class CommentCountMixin(serializers.Serializer):
    comments_count = serializers.SerializerMethodField()
    def get_comments_count(self, obj):
        return obj.comments.count()


class BoardIdMixin(serializers.Serializer):
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
