from rest_framework import serializers
from django.contrib.auth.models import User

from auth_app.api.serializers import UserNestedSerializer
from boards_app.models import Board


class TicketReadUsersMixin(serializers.Serializer):
    """
    Mixin to include read-only user relationships for Ticket serializers.

    Provides:
        assignee (UserNestedSerializer): Read-only nested data for the user assigned to the ticket.
        reviewer (UserNestedSerializer): Read-only nested data for the user reviewing the ticket.
    """
    assignee = UserNestedSerializer(read_only=True)
    reviewer = UserNestedSerializer(read_only=True)


class TicketWriteUsersMixin(serializers.Serializer):
    """
    Mixin to accept user assignment fields for Ticket creation or update.

    Provides:
        assignee_id (int): Primary key of the user to assign to the ticket, optional.
        reviewer_id (int): Primary key of the user to review the ticket, optional.
    """
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee',
        allow_null=True, required=False
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer',
        allow_null=True, required=False
    )


class CommentCountMixin(serializers.Serializer):
    """
    Mixin to add a comments_count field to serializers.

    Provides:
        comments_count (int): Number of comments related to the object.
    """
    comments_count = serializers.SerializerMethodField()
    def get_comments_count(self, obj):
        """
        Compute the number of comments for the given object.

        Args:
            obj: The instance being serialized, expected to have a 'comments' related name.

        Returns:
            int: Total count of related Comment instances.
        """
        return obj.comments.count()


class BoardIdMixin(serializers.Serializer):
    """
    Mixin to include the board relationship by primary key.

    Provides:
        board (int): Primary key of the Board instance this object belongs to.
    """
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())
