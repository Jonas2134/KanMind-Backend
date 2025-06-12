from rest_framework import serializers
from django.contrib.auth import get_user_model

from boards_app.models import Board


User = get_user_model()

class BoardSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, write_only=True)
    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'members',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id',
        ]
    
    def create(self, validated_data):
        members = validated_data.pop('members', [])
        board = Board.objects.create(owner=self.context['request'].user, **validated_data)
        board.members.set(members)
        return board
