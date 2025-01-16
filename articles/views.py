from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Article, Comment
from .serializers import ArticleSerializer, ArticleListSerializer, ArticleDetailSerializer, CommentSerializer
from rest_framework import permissions, generics
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as django_filters
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import models


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class ArticleFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = Article
        fields = ['created_at', 'is_public']

    @property
    def qs(self):
        return super().qs.select_related('author')\
            .annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments')
            ).order_by('-created_at')

class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ArticleFilter
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'view_count', 'likes_count']
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ArticleSerializer

    def get_queryset(self):
        # 기본 쿼리셋 정의
        queryset = Article.objects.select_related('author')\
            .prefetch_related('likes', 'comments')\
            .annotate(
                likes_count=Count('likes'),
                comments_count=Count('comments')
            )
        return queryset

    def get_serializer_class(self):
            if self.action == 'list':
                return ArticleListSerializer
            elif self.action == 'retrieve':
                return ArticleDetailSerializer
            return ArticleSerializer
    
    @action(detail=False, methods=['get'])
    def my_articles(self, request):
        """사용자 본인의 게시물만 조회"""
        queryset = self.get_queryset().filter(author=request.user)
        queryset = self.filter_queryset(queryset)  # 필터 적용
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def public_articles(self, request):
        """공개된 게시물만 조회"""
        queryset = self.get_queryset().filter(is_public=True)
        queryset = self.filter_queryset(queryset)  # 필터 적용
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """기본 list 메서드를 오버라이드하여 공개된 게시물만 보이도록 수정"""
        return self.public_articles(request)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        if instance.image and request.FILES.get('image'):
            instance.image.delete()
            
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        article = self.get_object()
        user = request.user
        
        if user in article.likes.all():
            article.likes.remove(user)
            return Response({'liked': False})
        else:
            article.likes.add(user)
            return Response({'liked': True})

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        stats = Article.objects.aggregate(
            total_articles=Count('id'),
            total_comments=Count('comments'),
        )
        
        most_liked = Article.objects.select_related('author')\
            .annotate(
                like_count=Count('likes'),
                comment_count=Count('comments')
            )\
            .order_by('-like_count')[:5]

        return Response({
            'total_articles': stats['total_articles'],
            'total_comments': stats['total_comments'],
            'most_liked': ArticleListSerializer(most_liked, many=True).data,
        })

    def retrieve(self, request, *args, **kwargs):
        """
        게시글 상세 조회 시 조회수 증가
        """
        instance = self.get_object()
        # 작성자가 아닌 경우에만 조회수 증가
        if instance.author != request.user:
            instance.view_count = models.F('view_count') + 1
            instance.save()
            # F() 함수로 인해 변경된 값을 다시 가져오기 위해 refresh
            instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CommentListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self, article_id):
        return Comment.objects.filter(article_id=article_id)\
            .select_related('author')\
            .prefetch_related('replies__author')

    def get(self, request, id):
        comments = self.get_queryset(id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, id):
        article = get_object_or_404(Article, id=id)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, article=article)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, article_id, pk):
        return get_object_or_404(Comment, article_id=article_id, pk=pk)

    def get(self, request, id, pk):
        comment = self.get_object(id, pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, id, pk):
        comment = self.get_object(id, pk)
        if request.user != comment.author:
            return Response(
                {"detail": "권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CommentSerializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, id, pk):
        comment = self.get_object(id, pk)
        if request.user != comment.author:
            return Response(
                {"detail": "권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN
            )
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


