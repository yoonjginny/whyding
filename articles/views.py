from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Article, Comment, Tag
from .serializers import ArticleSerializer, CommentSerializer, TagSerializer
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as django_filters
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(article_id=self.kwargs['article_pk'], parent=None)

    def perform_create(self, serializer):
        article = Article.objects.get(pk=self.kwargs['article_pk'])
        parent_id = self.request.data.get('parent')
        parent = Comment.objects.get(pk=parent_id) if parent_id else None
        serializer.save(author=self.request.user, article=article, parent=parent)

class ArticleFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(field_name='tags__name')
    created_at = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = Article
        fields = ['tags', 'created_at', 'is_public']

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ['title', 'content', 'tags__name']
    ordering_fields = ['created_at', 'view_count', 'likes']

    def get_queryset(self):
        queryset = Article.objects.all()
        if self.action == 'list':
            # 공개된 게시물만 표시
            queryset = queryset.filter(is_public=True)
        elif self.action == 'my_articles':
            # 내 게시물만 표시
            queryset = queryset.filter(author=self.request.user)
        return queryset

    def perform_create(self, serializer):
        try:
            serializer.save(author=self.request.user)
        except Exception as e:
            raise ValidationError(detail=str(e))

    @action(detail=False, methods=['get'])
    def my_articles(self, request):
        articles = self.get_queryset()
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        try:
            article = self.get_object()
            if request.user in article.likes.all():
                article.likes.remove(request.user)
                message = "좋아요가 취소되었습니다."
            else:
                article.likes.add(request.user)
                message = "좋아요가 추가되었습니다."
            return Response({'message': message}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        article = self.get_object()
        if request.user in article.bookmarks.all():
            article.bookmarks.remove(request.user)
            return Response({'status': 'bookmark removed'})
        else:
            article.bookmarks.add(request.user)
            return Response({'status': 'bookmark added'})

    @action(detail=False, methods=['get'])
    def bookmarked(self, request):
        bookmarked = Article.objects.filter(bookmarks=request.user)
        serializer = self.get_serializer(bookmarked, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def tags(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

    @method_decorator(cache_page(60 * 15))  # 15분 캐시
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
