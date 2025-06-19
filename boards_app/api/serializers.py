from rest_framework import serializers
from django.contrib.auth.models import User

from boards_app.models import Board


class BoardListSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id',
            'members',
        ]
        read_only_fields = [
            'id',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id',
        ]

        def get_member_count(self, obj):
            return obj.members.count()
        
        def get_ticket_count(self, obj):
            return obj.tickets.count()
        
        def get_tasks_to_do_count(self, obj):
            return obj.tickets.filter(status='to-do').count()
        
        def get_tasks_high_prio_count(self, obj):
            return obj.tickets.filter(priority='high').count()
        
        def validate_members(self, value):
            users = User.objects.filter(id__in=value)
            if len(users) != len(set(value)):
                raise serializers.ValidationError("Ein oder mehrere Mitglieder existieren nicht.")
            return value
        
        def create(self, validated_data):
            members_ids = validated_data.pop('members', [])
            request = self.context.get('request')

            if request is None:
                raise serializers.ValidationError("Request-Kontext fehlt.")
            
            user = request.user

            if not user or not user.is_authenticated:
                raise serializers.ValidationError("Authentifizierung erforderlich.")
            
            title = validated_data.get('title')

            board = Board.objects.create(owner=user, title=title)

            if members_ids:
                board.members.set(members_ids)
            return board
        

class BoardCreateSerializer(serializers.ModelSerializer):
    pass
