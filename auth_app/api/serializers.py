from rest_framework import serializers

from auth_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class RegistrationSerializer():
    pass