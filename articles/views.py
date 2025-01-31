from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Article, Comment
from .serializers import ArticleSerializer, ArticleListSerializer, ArticleDetailSerializer, CommentSerializer, ArticleLikeSerializer
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
from django.db import models
from drf_yasg.utils import swagger_auto_schema, no_body
from drf_yasg import openapi


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS 요청은 누구나 허용
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # PUT, PATCH, DELETE 요청은 작성자만 허용
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
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ArticleFilter
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'view_count', 'likes_count']
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
    
    @swagger_auto_schema(
        method='get',
        operation_summary="사용자 본인의 게시물 조회",
        operation_description="현재 로그인한 사용자가 작성한 게시물 목록을 조회합니다.",
        responses={
            200: ArticleListSerializer(many=True),
            401: "Unauthorized"
        }
    )
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

    @swagger_auto_schema(
        method='get',
        operation_summary="공개된 게시물 조회",
        operation_description="공개된 게시물 목록을 조회합니다.",
        responses={
            200: ArticleListSerializer(many=True),
            401: "Unauthorized"
        }
    )
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
    
    @swagger_auto_schema(
        method='post',
        request_body=no_body,
        responses={
            200: ArticleLikeSerializer(),
            400: "Bad Request",
            401: "Unauthorized"
        },
        operation_description="게시물 좋아요 토글 (추가/제거)"
    )
    @action(
        detail=True, 
        methods=['post'],
        permission_classes=[IsAuthenticated],
        serializer_class=ArticleLikeSerializer,
    )
    def like(self, request, pk=None):
        """게시물 좋아요 토글 (추가/제거)"""
        article = self.get_object()
        user = request.user
        
        if article.likes.filter(id=user.id).exists():
            article.likes.remove(user)
            message = "좋아요가 취소되었습니다."
        else:
            article.likes.add(user)
            message = "좋아요가 추가되었습니다."
        
        serializer = ArticleLikeSerializer({
            'message': message,
            'like_count': article.likes.count()
        })
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_summary="게시물 통계 조회",
        operation_description="전체 게시물 수, 댓글 수, 가장 많이 좋아요를 받은 게시물 목록을 조회합니다.",
        responses={
            200: openapi.Response(
                description="통계 데이터",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_articles': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_comments': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'most_liked': openapi.Schema(type=openapi.TYPE_ARRAY, items=ArticleListSerializer),
                    }
                )
            ),
            401: "Unauthorized"
        }
    )
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

class CommentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self, article_id):
        """특정 게시물의 댓글 목록을 반환하는 쿼리셋"""
        return Comment.objects.filter(article_id=article_id)\
            .select_related('author')\
            .prefetch_related('replies__author')

    def get_object(self, article_id, pk):
        """특정 댓글 객체를 반환"""
        return get_object_or_404(Comment, article_id=article_id, pk=pk)

    def get(self, request, article_id, pk=None):
        """
        댓글 목록 조회 (GET /articles/<article_id>/comments/)
        특정 댓글 조회 (GET /articles/<article_id>/comments/<pk>/)
        """
        if pk:
            # 특정 댓글 조회
            comment = self.get_object(article_id, pk)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        else:
            # 댓글 목록 조회
            comments = self.get_queryset(article_id)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

    @swagger_auto_schema(
        method='post',
        operation_summary="댓글 생성",
        operation_description="특정 게시물에 새로운 댓글을 생성합니다.",
        request_body=CommentSerializer,
        responses={
            201: CommentSerializer(),
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    def post(self, request, article_id):
        """
        댓글 생성 (POST /articles/<article_id>/comments/)
        """
        article = get_object_or_404(Article, id=article_id)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, article=article)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        method='put',
        operation_summary="댓글 수정",
        operation_description="특정 댓글을 수정합니다.",
        request_body=CommentSerializer,
        responses={
            200: CommentSerializer(),
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    def put(self, request, article_id, pk):
        """
        댓글 수정 (PUT /articles/<article_id>/comments/<pk>/)
        """
        comment = self.get_object(article_id, pk)
        if request.user != comment.author:
            return Response(
                {"detail": "권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CommentSerializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(
        method='delete',
        operation_summary="댓글 삭제",
        operation_description="특정 댓글을 삭제합니다.",
        responses={
            204: "No Content",
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    def delete(self, request, article_id, pk):
        """
        댓글 삭제 (DELETE /articles/<article_id>/comments/<pk>/)
        """
        comment = self.get_object(article_id, pk)
        if request.user != comment.author:
            return Response(
                {"detail": "권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN
            )
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


