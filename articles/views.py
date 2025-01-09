from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Article, Comment, Tag
from .serializers import ArticleSerializer, ArticleListSerializer, ArticleDetailSerializer, CommentSerializer
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as django_filters
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Count
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.select_related('author')\
            .prefetch_related('replies__author')\
            .filter(
                article_id=self.kwargs['article_pk'],
                parent=None
            )

    def perform_create(self, serializer):
        article = Article.objects.get(pk=self.kwargs['article_pk'])
        parent_id = self.request.data.get('parent')
        parent = Comment.objects.get(pk=parent_id) if parent_id else None
        serializer.save(author=self.request.user, article=article, parent=parent)

class ArticleFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(method='filter_tags')
    created_at = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = Article
        fields = ['tags', 'created_at', 'is_public']

    def filter_tags(self, queryset, name, value):
        if value:
            return queryset.filter(tags__name=value)
        return queryset

    @property
    def qs(self):
        return super().qs.select_related('author')\
            .prefetch_related('tags')\
            .annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments')
            ).order_by('-created_at')

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.select_related('author')\
        .prefetch_related('tags', 'likes', 'comments')\
        .annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        ).order_by('-created_at')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ['title', 'content', 'tags__name']
    ordering_fields = ['created_at', 'view_count', 'likes_count']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        elif self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        article = self.get_object()
        user = request.user
        if user in article.likes.all():
            article.likes.remove(user)
            return Response({'liked': False}, status=status.HTTP_200_OK)
        else:
            article.likes.add(user)
            return Response({'liked': True}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        stats = Article.objects.aggregate(
            total_articles=Count('id'),
            total_comments=Count('comments'),
        )
        
        most_liked = Article.objects.select_related('author')\
            .prefetch_related('tags')\
            .annotate(
                like_count=Count('likes'),
                comment_count=Count('comments')
            )\
            .order_by('-like_count')[:5]

        return Response({
            'total_articles': stats['total_articles'],
            'total_comments': stats['total_comments'],
            'most_liked': ArticleSerializer(most_liked, many=True).data,
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        article_id = self.kwargs['id']
        return Comment.objects.filter(article__id=article_id, parent__isnull=True)
    
    def perform_create(self, serializer):
        article_id = self.kwargs['id']
        article = get_object_or_404(Article, id=article_id)
        serializer.save(author=self.request.user, article=article)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        article_id = self.kwargs['id']
        return Comment.objects.filter(article__id=article_id)
    
    def perform_update(self, serializer):
        comment = self.get_object()
        if self.request.user != comment.author:
            raise PermissionDenied("You cannot edit this comment.")
        serializer.save()
    
    def perform_destroy(self, instance):
        if self.request.user != instance.author:
            raise PermissionDenied("You cannot delete this comment.")
        instance.delete()
