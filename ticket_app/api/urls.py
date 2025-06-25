from django.urls import path

from .views import TicketPostView

urlpatterns = [
    path('tasks/', TicketPostView.as_view(), name='ticket-post'),
]
