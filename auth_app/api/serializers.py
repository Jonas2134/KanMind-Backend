from rest_framework import serializers
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }


    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This e-mail address is already taken!")
        return value
    

    def validate(self, attrs):
        pw = attrs.get('password')
        repeated_pw = attrs.get('repeated_password')
        if pw != repeated_pw:
            raise serializers.ValidationError({"password": "The passwords don't match!"})
        return attrs

    
    def create(self, validated_data):
        fullname = validated_data.pop('fullname')
        email = validated_data.pop('email')
        raw_password = validated_data.pop('password')
        validated_data.pop('repeated_password', None)

        parts = fullname.strip().split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        username = email
        
        account = User(username=username, email=email,
                       first_name=first_name, last_name=last_name)
        account.set_password(raw_password)
        account.save()
        return account
