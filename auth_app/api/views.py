from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .serializers import RegistrationSerializer, CustomLoginSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:        
            new_user = serializer.save()
            token = Token.objects.create(user=new_user)
            response_data = {
                "token": token.key,
                "fullname": f"{new_user.first_name.capitalize()} {new_user.last_name.capitalize()}",
                "email": new_user.email,
                "user_id": new_user.id,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response(
                {"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            response_data = {
                "token": token.key,
                "fullname": f"{user.first_name.capitalize()} {user.last_name.capitalize()}",
                "email": user.email,
                "user_id": user.id,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response(
                {"detail": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
