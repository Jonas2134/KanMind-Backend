from rest_framework import serializers

from ticket_app.models import Ticket
from auth_app.api.serializers import UserNestedSerializer
from boards_app.models import Board


class TicketBaseSerializer(serializers.ModelSerializer):
    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count',
        ]
        read_only_fields = ['id', 'comments_count', 'assignee', 'reviewer']

    def get_comments_count(self, obj):
        return obj.comments.count()


class TicketSerializer(TicketBaseSerializer):
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
    class Meta(TicketBaseSerializer.Meta):
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['board']
        read_only_fields = TicketBaseSerializer.Meta.read_only_fields
