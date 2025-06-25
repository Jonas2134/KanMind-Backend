from django.urls import path

from .views import TicketPostView, TaskAssigneeView, TaskReviewerView

urlpatterns = [
    path('tasks/', TicketPostView.as_view(), name='ticket-post'),
    path('tasks/assigned-to-me/', TaskAssigneeView.as_view(), name='task-assignee'),
    path('tasks/reviewing/', TaskReviewerView.as_view(), name='task-reviewer'),
]
