from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404

from .serializers import RegistrationSerializer, CustomLoginSerializer, EmailQuerySerializer


class RegistrationView(generics.CreateAPIView):
    """
    API endpoint that allows new users to register.

    This view handles:
    - Validation of unique email and password match.
    - Extraction and capitalization of first and last name.
    - User creation and token generation.
    - Returning token and user info in the response.

    Attributes:
        permission_classes (list): Permissions for this view (AllowAny).
        serializer_class (Serializer): Serializer for input validation.
        queryset (QuerySet): Base queryset required by CreateAPIView.
    """
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Process POST request to register a new user.

        Steps:
        1. Validate incoming data via serializer.
        2. Check email uniqueness and password confirmation.
        3. Parse full name into first and last name.
        4. Create User instance and generate auth token.
        5. Return HTTP 201 with token and user details.

        Args:
            request (Request): DRF request object containing JSON payload.

        Returns:
            Response: DRF Response with
                - HTTP 201 and JSON {token, fullname, email, user_id} on success
                - HTTP 400 with error details if validation fails
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        error_response = self._validate_registration(data)
        if error_response:
            return error_response

        first, last = self._extract_names(data.get('fullname', ''))
        user = self._create_user(data['email'], first, last, data['password'])
        return self._build_response(user)

    def _validate_registration(self, data):
        """
        Ensure email is unique and passwords match.

        Args:
            data (dict): Validated data from serializer, includes
                - 'email'
                - 'password'
                - 'repeated_password'

        Returns:
            Response or None:
                - DRF Response with HTTP 400 if validation fails
                - None if all checks pass
        """
        if User.objects.filter(email=data['email']).exists():
            return Response({'email': ['This e-mail address is already taken!']}, status=status.HTTP_400_BAD_REQUEST)
        if data['password'] != data['repeated_password']:
            return Response({'password': ["The passwords don't match!"]}, status=status.HTTP_400_BAD_REQUEST)

    def _extract_names(self, fullname):
        """
        Split a full name into first and last name parts.

        Args:
            fullname (str): Full name string, e.g. "John Doe".

        Returns:
            tuple: (first_name, last_name) both capitalized.
        """
        parts = fullname.strip().split(" ", 1) + [""]
        return parts[0].capitalize(), parts[1].capitalize()

    def _create_user(self, email, first, last, password):
        """
        Create and save a new User instance.

        Args:
            email (str): User's email, also used as username.
            first (str): First name.
            last (str): Last name.
            password (str): Raw password to be hashed.

        Returns:
            User: The newly created Django User object.
        """
        user = User(username=email, email=email, first_name=first, last_name=last)
        user.set_password(password)
        user.save()
        return user

    def _build_response(self, user):
        """
        Generate auth token and construct response payload.

        Args:
            user (User): The saved User instance.

        Returns:
            Response: DRF Response with HTTP 201 containing:
                - token (str)
                - fullname (str)
                - email (str)
                - user_id (int)
        """
        token = Token.objects.create(user=user)
        return Response({
            "token": token.key,
            "fullname": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "user_id": user.id,
        }, status=status.HTTP_201_CREATED)


class CustomLoginView(generics.GenericAPIView):
    """
    API endpoint that allows a user to obtain an authentication token.

    This view handles:
    - Validation of email and password via serializer.
    - User authentication and active‐status check.
    - Returning an auth token and basic user info on success.

    Attributes:
        permission_classes (list): Permissions for this view (AllowAny).
        serializer_class (Serializer): Serializer for input validation.
    """
    permission_classes = [AllowAny]
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        """
        Process POST request to authenticate a user.

        Steps:
        1. Validate incoming data via serializer.
        2. Authenticate the user credentials.
        3. Return HTTP 400 if authentication fails.
        4. Generate or retrieve token and return HTTP 201 on success.

        Args:
            request (Request): DRF request object containing JSON payload.

        Returns:
            Response: DRF Response with
                - HTTP 201 and JSON {token, fullname, email, user_id} on success
                - HTTP 400 with error detail on failure
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self._authenticate_user(serializer.validated_data)
        if isinstance(user, Response):
            return user
        return self._build_response(user)

    def _authenticate_user(self, data):
        """
        Authenticate user credentials and check active status.

        Args:
            data (dict): Validated data from serializer, includes
                - 'email'
                - 'password'

        Returns:
            User or Response:
                - Django User instance if credentials are valid and active.
                - DRF Response with HTTP 400 if authentication or active check fails.
        """
        user = authenticate(request=self.request, username=data['email'], password=data['password'])
        if not user:
            return Response({"detail": "Invalid e-mail or password."}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({"detail": "This account is not active."}, status=status.HTTP_400_BAD_REQUEST)
        return user

    def _build_response(self, user):
        """
        Generate or retrieve token and construct response payload.

        Args:
            user (User): The authenticated User instance.

        Returns:
            Response: DRF Response with HTTP 201 containing:
                - token (str)
                - fullname (str)
                - email (str)
                - user_id (int)
        """
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "fullname": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "user_id": user.id,
        }, status=status.HTTP_201_CREATED)


class EmailCheckView(generics.GenericAPIView):
    """
    API endpoint that allows checking for a user by email.

    This view handles:
    - Validation of email query parameter via serializer.
    - Retrieving a User instance by email or returning 404.
    - Returning basic user info (id, email, fullname).

    Attributes:
        permission_classes (list): Permissions for this view (IsAuthenticated).
        serializer_class (Serializer): Serializer for query parameter validation.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailQuerySerializer

    def get(self, request, *args, **kwargs):
        """
        Process GET request to fetch a user by email.

        Steps:
        1. Validate 'email' in query parameters via serializer.
        2. Retrieve the User or return a 404 response.

        Args:
            request (Request): DRF request object with query params.

        Returns:
            Response: DRF Response with
                - HTTP 200 and JSON {id, email, fullname} on success
                - HTTP 404 with error detail if user not found
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return self._get_user_by_email(serializer.validated_data['email'])

    def _get_user_by_email(self, email):
        """
        Helper to retrieve a user by email or return 404.

        Args:
            email (str): The email address to look up.

        Returns:
            Response: DRF Response with user info or 404 detail.
        """
        try:
            user = get_object_or_404(User, email=email)
        except Http404:
            return Response({"detail": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name.strip().capitalize()} {user.last_name.strip().capitalize()}"
        }, status=status.HTTP_200_OK)
