from django.urls import path

from .views import BoardListCreateView, BoardDetailPatchDeleteView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailPatchDeleteView.as_view(), name='board-detail'),
]
