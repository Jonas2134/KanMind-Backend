from rest_framework import serializers
from django.contrib.auth.models import User

from boards_app.models import Board
from ticket_app.models import Ticket
from ticket_app.api.serializers import TicketBaseSerializer
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


class BoardCreateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    title = serializers.CharField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'members']
        read_only_fields = ['id']

    def validate_members(self, value):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError("Request context is missing.")
        user = request.user

        users = User.objects.filter(id__in=value).values_list('id', flat=True)
        missing = set(value) - set(users)
        if missing:
            raise serializers.ValidationError(f"The following members do not exist: {sorted(missing)}")
        
        if user.id in value:
            raise serializers.ValidationError("You cannot add yourself as a member.")
        return value
    
    def create(self, validated_data):
        members_ids = validated_data.pop('members', [])
        request = self.context.get('request')

        user = request.user
        board = Board.objects.create(owner=user, title=validated_data['title'])

        if members_ids:
            board.members.set(members_ids)

        return board


class TicketNestedSerializer(TicketBaseSerializer):
    class Meta(TicketBaseSerializer.Meta):
        model = Ticket
        fields = TicketBaseSerializer.Meta.fields
        read_only_fields = TicketBaseSerializer.Meta.read_only_fields


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


class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    title = serializers.CharField(required=False)

    class Meta:
        model = Board
        fields = ['title', 'members']

    def validate_members(self, value):
        request = self.context.get('request')
        if request is None:
            raise serializers.ValidationError("Request context is missing.")
        user = request.user

        users = User.objects.filter(id__in=value).values_list('id', flat=True)
        missing = set(value) - set(users)
        if missing:
            raise serializers.ValidationError(f"The following members do not exist: {sorted(missing)}")

        if user.id in value:
            raise serializers.ValidationError("You cannot add yourself as a member.")
        return value

    def update(self, instance, validated_data):
        title = validated_data.get('title', None)
        if title is not None:
            instance.title = title
            instance.save()

        if 'members' in validated_data:
            members_ids = validated_data.get('members', [])
            instance.members.set(members_ids)
        return instance
