from django.urls import path

from .views import CommentListCreateView, CommentDestroyView

urlpatterns = [
    path('tasks/<int:pk>/comments/', CommentListCreateView.as_view(), name='comment-list'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', CommentDestroyView.as_view(), name='comment-delete'),
]
