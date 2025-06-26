from rest_framework import serializers
from django.contrib.auth.models import User

from ticket_app.models import Ticket
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


class TicketBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'due_date',
        ]
        read_only_fields = ['id']

    def get_comments_count(self, obj):
        return obj.comments.count()


class TicketSerializer(TicketBaseSerializer, TicketReadUsersMixin, BoardIdMixin, CommentCountMixin):
    class Meta(TicketBaseSerializer.Meta):
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['assignee', 'reviewer', 'board', 'comments_count']
        read_only_fields = TicketBaseSerializer.Meta.read_only_fields + ['assignee', 'reviewer']


class TicketCreateSerializer(TicketBaseSerializer, TicketWriteUsersMixin, BoardIdMixin):
    class Meta:
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['assignee_id', 'reviewer_id', 'board']
        read_only_fields = TicketBaseSerializer.Meta.read_only_fields
