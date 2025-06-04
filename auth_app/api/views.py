from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
# from rest_framework.authtoken.views import ObtainAuthToken

from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:        
            new_user = serializer.save()
            token, _ = Token.objects.get_or_create(user=new_user)
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


class CustomLoginView():
    pass
