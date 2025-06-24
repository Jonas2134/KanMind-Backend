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
    

class CustomLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        email = attrs.get("email", "").strip()
        password = attrs.get("password", "")
        if not email or not password:
            raise serializers.ValidationError("E-mail and password are required.")
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid e-mail or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is not active.")
        attrs["user"] = user
        return attrs
    

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
