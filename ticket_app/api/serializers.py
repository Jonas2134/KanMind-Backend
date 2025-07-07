from rest_framework import serializers

from ticket_app.models import Ticket
from .serializer_mixins import TicketReadUsersMixin, TicketWriteUsersMixin, CommentCountMixin, BoardIdMixin


class TicketBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for Ticket, covering core fields.

    Fields:
        id (int): Ticket primary key, read‑only.
        title (str): Title of the ticket.
        description (str): Detailed description, optional.
        status (str): Workflow status (e.g., 'to-do', 'in-progress', etc.).
        priority (str): Priority level (e.g., 'low', 'medium', 'high').
        due_date (date): Optional deadline for the ticket.
    """
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
        """
        Count number of comments related to this ticket.

        Args:
            obj (Ticket): The Ticket instance being serialized.

        Returns:
            int: Number of Comment instances linked to this ticket.
        """
        return obj.comments.count()


class TicketSerializer(TicketBaseSerializer, TicketReadUsersMixin, BoardIdMixin, CommentCountMixin):
    """
    Full serializer for Ticket, including related users and board link.

    Inherits:
        - Base fields from TicketBaseSerializer
        - assignee and reviewer read fields
        - board ID
        - comments_count via CommentCountMixin

    Fields:
        id, title, description, status, priority, due_date (from base)
        assignee (UserNested): Read-only user assigned to the ticket.
        reviewer (UserNested): Read-only user reviewing the ticket.
        board (int): Board ID this ticket belongs to.
        comments_count (int): Count of comments on the ticket.
    """
    class Meta(TicketBaseSerializer.Meta):
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['assignee', 'reviewer', 'board', 'comments_count']
        read_only_fields = TicketBaseSerializer.Meta.read_only_fields + ['assignee', 'reviewer']


class TicketCreateSerializer(TicketBaseSerializer, TicketWriteUsersMixin, BoardIdMixin):
    """
    Serializer for creating a new Ticket.

    Inherits:
        - Base fields from TicketBaseSerializer
        - assignee_id and reviewer_id write fields from TicketWriteUsersMixin
        - board ID input via BoardIdMixin

    Fields:
        id, title, description, status, priority, due_date (from base)
        assignee_id (int): User ID to assign the ticket to, optional.
        reviewer_id (int): User ID to review the ticket, optional.
        board (int): Board ID to attach this ticket to.
    """
    class Meta:
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['assignee_id', 'reviewer_id', 'board']
        read_only_fields = TicketBaseSerializer.Meta.read_only_fields


class TicketPatchSerializer(TicketBaseSerializer, TicketWriteUsersMixin):
    """
    Serializer for patching (partial update) a Ticket.

    Inherits:
        - Base fields from TicketBaseSerializer
        - assignee_id and reviewer_id write fields from TicketWriteUsersMixin

    Fields:
        id, title, description, status, priority, due_date (from base)
        assignee_id (int): New assignee user ID, optional.
        reviewer_id (int): New reviewer user ID, optional.
    """
    class Meta:
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['assignee_id', 'reviewer_id']
        read_only_fields = TicketBaseSerializer.Meta.read_only_fields


class TicketPatchSuccessSerializer(TicketBaseSerializer, TicketReadUsersMixin, BoardIdMixin):
    """
    Serializer returned after a successful Ticket patch.

    Inherits:
        - Base fields from TicketBaseSerializer
        - assignee and reviewer read fields from TicketReadUsersMixin
        - board ID via BoardIdMixin

    Fields:
        id, title, description, status, priority, due_date (from base)
        assignee (UserNested): Read-only user assigned to the ticket.
        reviewer (UserNested): Read-only user reviewing the ticket.
        board (int): Board ID this ticket belongs to.
    """
    class Meta(TicketBaseSerializer.Meta):
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields + ['assignee', 'reviewer', 'board']
        read_only_fields = TicketBaseSerializer.Meta.read_only_fields + ['assignee', 'reviewer']
