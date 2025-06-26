from django.urls import path

from .views import TicketPostView, TaskAssigneeView, TaskReviewerView, TicketPatchDeleteView

urlpatterns = [
    path('tasks/assigned-to-me/', TaskAssigneeView.as_view(), name='task-assignee'),
    path('tasks/reviewing/', TaskReviewerView.as_view(), name='task-reviewer'),
    path('tasks/', TicketPostView.as_view(), name='ticket-post'),
    path('tasks/<int:pk>/', TicketPatchDeleteView.as_view(), name='ticket-patch-delete'),
]
