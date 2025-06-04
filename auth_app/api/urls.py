from django.urls import path

from .views import CustomLoginView, RegistrationView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', CustomLoginView, name='login'),
]
