from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArticleViewSet,
    CommentListCreateView,
    CommentDetailView
)

app_name = 'articles'

router = DefaultRouter()
router.register('', ArticleViewSet, basename='article')

urlpatterns = [
    path('<int:id>/comments/',
         CommentListCreateView.as_view(),
         name='comment-list-create'),
    path('<int:id>/comments/<int:pk>/',
         CommentDetailView.as_view(),
         name='comment-detail'),
    path('', include(router.urls)),
] 