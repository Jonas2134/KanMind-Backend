from rest_framework import serializers
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration input data.

    Handles:
    - Writing only the 'fullname' and 'repeated_password' fields.
    - Ensuring 'email' and 'password' fields are provided.

    Fields:
        fullname (str): Full name of the user (write-only).
        email (str): Email address, used as username.
        password (str): Raw password (write-only).
        repeated_password (str): Confirmation of the password (write-only).
    """
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
    """
    Serializer for user login.

    Validates that:
    - An email and password are provided.
    - Both fields are write-only.

    Fields:
        email (str): User's email address (write-only).
        password (str): User's password (write-only).
    """
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    

class EmailQuerySerializer(serializers.Serializer):
    """
    Serializer for email lookup via query parameters.

    Validates that:
    - A single 'email' parameter is provided.

    Fields:
        email (str): Email address to query (required).
    """
    email = serializers.EmailField(required=True)


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Serializer for nested user representation.

    Returns:
    - id: User primary key.
    - email: User email.
    - fullname: Computed full name or email if names are missing.

    Fields:
        id (int): User ID.
        email (str): User email address.
        fullname (str): Full name, capitalized; falls back to email.
    """
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        """
        Compute the full name for a User instance.

        Args:
            obj (User): The User instance being serialized.

        Returns:
            str: Capitalized \"First Last\" if available,
                 otherwise returns the email address.
        """
        full = obj.get_full_name() if hasattr(obj, 'get_full_name') else None
        if full:
            return full
        first = getattr(obj, 'first_name', '') or ''
        last = getattr(obj, 'last_name', '') or ''
        name = f"{first} {last}".strip()
        return name or obj.email
