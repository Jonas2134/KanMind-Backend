# from rest_framework.views import APIView
from rest_framework import generics
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework.authtoken.models import Token
# from rest_framework.authtoken.views import ObtainAuthToken

from auth_app.models import UserProfile
from .serializers import UserProfileSerializer


class UserListView(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class RegistrationView():
    pass


class CustomLoginView():
    pass
