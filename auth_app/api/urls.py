from django.urls import path

from .views import CustomLoginView, RegistrationView, EmailCheckView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('email-check/', EmailCheckView.as_view(), name='email-detail'),
]
