from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404

from .serializers import RegistrationSerializer, CustomLoginSerializer, EmailQuerySerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:        
            new_user = serializer.save()
            token = Token.objects.create(user=new_user)
            response_data = {
                "token": token.key,
                "fullname": f"{new_user.first_name.capitalize()} {new_user.last_name.capitalize()}",
                "email": new_user.email,
                "user_id": new_user.id,
            }
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
        except Exception as err:
            return Response(
                {"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            response_data = {
                "token": token.key,
                "fullname": f"{user.first_name.capitalize()} {user.last_name.capitalize()}",
                "email": user.email,
                "user_id": user.id,
            }
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
        except Exception as err:
            return Response(
                {"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = EmailQuerySerializer(data=request.query_params)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = serializer.validated_data["email"]

        try:
            user = get_object_or_404(User, email=email)
        except Http404:
            return Response(
                {"detail": "Email not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as err:
            return Response(
                {"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response_data = {
            "id": user.id,
            "email": user.email,
            "fullname": f"{user.first_name.strip().capitalize()} {user.last_name.strip().capitalize()}",
        }
        return Response(
            response_data,
            status=status.HTTP_200_OK
        )
