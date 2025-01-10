from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, CommentListCreateView, CommentDetailView

router = DefaultRouter()
router.register(r'', ArticleViewSet, basename='article')

urlpatterns = [
    path('<int:id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('<int:id>/comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
] + router.urls 