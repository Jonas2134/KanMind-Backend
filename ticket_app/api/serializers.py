from rest_framework import serializers

from ticket_app.models import Ticket
from .serializer_mixins import TicketReadUsersMixin, TicketWriteUsersMixin, CommentCountMixin, BoardIdMixin


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


class TicketPatchSerializer(TicketBaseSerializer, TicketWriteUsersMixin):
    class Meta:
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['assignee_id', 'reviewer_id']
        read_only_fields = TicketBaseSerializer.Meta.read_only_fields


class TicketPatchSuccessSerializer(TicketBaseSerializer, TicketReadUsersMixin, BoardIdMixin):
    class Meta(TicketBaseSerializer.Meta):
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['assignee', 'reviewer', 'board']
        read_only_fields = TicketBaseSerializer.Meta.read_only_fields + ['assignee', 'reviewer']
