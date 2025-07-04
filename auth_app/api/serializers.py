from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True},
        }
    

class CustomLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    

class EmailQuerySerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserNestedSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        full = obj.get_full_name() if hasattr(obj, 'get_full_name') else None
        if full:
            return full
        first = getattr(obj, 'first_name', '') or ''
        last = getattr(obj, 'last_name', '') or ''
        name = f"{first} {last}".strip()
        return name or obj.email
