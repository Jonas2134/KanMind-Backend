from django.urls import path

from .views import CustomLoginView, RegistrationView

urlpatterns = [
    path('', CustomLoginView, name='login'),
    path('login/', CustomLoginView, name='login'),
    path('registration/', RegistrationView, name='registration'),
]