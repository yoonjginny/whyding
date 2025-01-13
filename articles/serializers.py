from rest_framework import serializers
from .models import Article, Comment
from accounts.serializers import UserSerializer

class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    image = serializers.ImageField(required=False)
    
    class Meta:
        model = Article
        fields = [
            'id', 'author', 'title', 'content', 'is_public', 'image',
            'view_count', 'like_count', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'title': {'required': False},      # 제목 필드를 선택적으로 설정
            'content': {'required': False},    # 내용 필드를 선택적으로 설정
            'is_public': {'required': False},  # 공개 여부 필드를 선택적으로 설정
            'image': {'required': False},      # 이미지 필드를 선택적으로 설정
        }
    
    def create(self, validated_data):
        article = Article.objects.create(**validated_data)
        return article

class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'author', 'title', 'is_public',
            'view_count', 'like_count', 'created_at'
        ]

class ArticleDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'author', 'title', 'content', 'image', 'is_public',
            'view_count', 'like_count', 'comments',
            'created_at', 'updated_at'
        ]
    
    def get_comments(self, obj):
        comments = obj.comments.filter(parent__isnull=True)
        return CommentSerializer(comments, many=True).data

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'comment', 'parent', 'replies',
            'created_at', 'updated_at'
        ]
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []