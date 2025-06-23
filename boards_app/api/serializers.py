from rest_framework import serializers
from django.contrib.auth.models import User

from boards_app.models import Board


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
        

class BoardCreateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    title = serializers.CharField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'members']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        members_ids = validated_data.pop('members', [])
        request = self.context.get('request')

        if request is None:
            raise serializers.ValidationError("Request context is missing.")

        user = request.user
        board = Board.objects.create(owner=user, title=validated_data['title'])

        if members_ids:
            board.members.set(members_ids)

        return board
