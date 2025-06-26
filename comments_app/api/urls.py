from django.urls import path

from .views import CommentListCreateView

urlpatterns = [
    path('tasks/<int:pk>/comments/', CommentListCreateView.as_view(), name='comment-list'),
]
