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
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if User.objects.filter(email=data['email']).exists():
            return Response({'email': ['This e-mail address is already taken!']}, status=status.HTTP_400_BAD_REQUEST)
        if data['password'] != data['repeated_password']:
            return Response({'password': ["The passwords don't match!"]}, status=status.HTTP_400_BAD_REQUEST)

        fullname = data.get('fullname', '').strip()
        first, last = (fullname.split(" ", 1) + [""])[:2]
        first = first.capitalize()
        last = last.capitalize()

        user = User(username=data['email'], email=data['email'], first_name=first, last_name=last)
        user.set_password(data['password'])
        user.save()

        token = Token.objects.create(user=user)
        response_data = {
            "token": token.key,
            "fullname": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "user_id": user.id,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class CustomLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = authenticate(request=request, username=data['email'], password=data['password'])
        if not user:
            return Response({"detail": "Invalid e-mail or password."}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({"detail": "This account is not active."}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        response_data = {
            "token": token.key,
            "fullname": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "user_id": user.id,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class EmailCheckView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailQuerySerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = get_object_or_404(User, email=email)
        except Http404:
            return Response({"detail": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

        response_data = {
            "id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name.strip().capitalize()} {user.last_name.strip().capitalize()}",
        }
        return Response(response_data, status=status.HTTP_200_OK)
