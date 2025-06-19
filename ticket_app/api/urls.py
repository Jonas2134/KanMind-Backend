from django.urls import path

from .views import TicketView

urlpatterns = [
    path('tasks/', TicketView.as_view(), name='task-detail'),
]
