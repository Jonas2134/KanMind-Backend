from rest_framework import serializers
from django.contrib.auth.models import User

from boards_app.models import Board
from ticket_app.models import Ticket
from ticket_app.api.serializers import TicketBaseSerializer
from ticket_app.api.serializer_mixins import TicketReadUsersMixin, CommentCountMixin
from auth_app.api.serializers import UserNestedSerializer


class BoardListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'owner_id',
            'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count',
        ]


class TicketNestedSerializer(TicketBaseSerializer, TicketReadUsersMixin, CommentCountMixin):
    class Meta(TicketBaseSerializer.Meta):
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['assignee', 'reviewer', 'comments_count']
        read_only_fields = TicketBaseSerializer.Meta.read_only_fields + ['assignee', 'reviewer']


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = UserNestedSerializer(many=True, read_only=True)
    tasks = TicketNestedSerializer(many=True, read_only=True, source='tickets')

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'members',
            'tasks',
        ]


class BoardDetailAfterUpdateSerializer(serializers.ModelSerializer):
    owner_data = UserNestedSerializer(source='owner', read_only=True)
    members_data = UserNestedSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_data',
            'members_data',
        ]


class BoardCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members']
        read_only_fields = ['id']


class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    title = serializers.CharField(required=False)

    class Meta:
        model = Board
        fields = ['title', 'members']
