from django.urls import path

from .views import TodoListView, TaskDetailView

urlpatterns = [
    path('boards/', TodoListView, name='todo-list'),
    path('boards/<int:pk>', TaskDetailView, name='todo-detail'),
]