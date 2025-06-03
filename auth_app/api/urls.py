from django.urls import path

from .views import CustomLoginView, RegistrationView

urlpatterns = [
    path('login/', CustomLoginView, name='login'),
    path('registration/', RegistrationView, name='registration'),
]