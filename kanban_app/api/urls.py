from django.urls import path

from .views import BoardListView, BoardDetailView, TodoListView, TaskDetailView

urlpatterns = [
    path('boards/', BoardListView, name='board-list'),
    path('boards/<int:pk>', BoardDetailView, name='board-detail'),
    path('tasks/', TodoListView, name='todo-list'),
    path('tasks/<int:pk>', TaskDetailView, name='todo-detail'),
]