from rest_framework import serializers

from boards_app.models import Board
from ticket_app.models import Ticket
from ticket_app.api.serializers import TicketBaseSerializer
from ticket_app.api.serializer_mixins import TicketReadUsersMixin, CommentCountMixin
from auth_app.api.serializers import UserNestedSerializer


class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing boards with summary counts.

    Fields:
        id (int): Board primary key, read‑only.
        title (str): Board title, read‑only.
        owner_id (int): ID of the board owner, read‑only.
        member_count (int): Number of members on the board, read‑only.
        ticket_count (int): Total tickets on the board, read‑only.
        tasks_to_do_count (int): Count of tickets with status 'todo', read‑only.
        tasks_high_prio_count (int): Count of tickets with priority 'high', read‑only.
    """
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
    """
    Nested serializer for tickets within a board detail.

    Inherits base fields and adds assignment, review, and comment count.

    Fields:
        (all from TicketBaseSerializer)
        assignee (UserNestedSerializer): User assigned to the ticket, read‑only.
        reviewer (UserNestedSerializer): User reviewing the ticket, read‑only.
        comments_count (int): Number of comments on the ticket.
    """
    class Meta(TicketBaseSerializer.Meta):
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['assignee', 'reviewer', 'comments_count']
        read_only_fields = TicketBaseSerializer.Meta.read_only_fields + ['assignee', 'reviewer']


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for full board detail view.

    Fields:
        id (int): Board primary key.
        title (str): Board title.
        owner_id (int): ID of the board owner, read‑only.
        members (list[UserNestedSerializer]): List of board members.
        tasks (list[TicketNestedSerializer]): Nested ticket data under 'tasks'.
    """
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
    """
    Serializer used after updating a board to return owner and member data.

    Fields:
        id (int): Board primary key.
        title (str): Board title.
        owner_data (UserNestedSerializer): Detailed owner info.
        members_data (list[UserNestedSerializer]): Detailed member info.
    """
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
    """
    Serializer for creating a new board.

    Fields:
        id (int): Board primary key, read‑only.
        title (str): Title for the new board (required).
        members (list[int]): List of user IDs to add, write‑only, optional.
    """
    title = serializers.CharField()
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members']
        read_only_fields = ['id']


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating board title or members.

    Fields:
        title (str): New title for the board, optional.
        members (list[int]): New list of user IDs, write‑only, optional.
    """
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    title = serializers.CharField(required=False)

    class Meta:
        model = Board
        fields = ['title', 'members']
