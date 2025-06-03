from django.urls import path

from .views import UserListView, CustomLoginView, RegistrationView

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('login/', CustomLoginView, name='login'),
    path('registration/', RegistrationView, name='registration'),
]
