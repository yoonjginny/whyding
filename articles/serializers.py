from rest_framework import serializers
from .models import Article, Comment, Tag
from accounts.serializers import UserSerializer

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        source='tags'
    )
    
    class Meta:
        model = Article
        fields = [
            'id', 'author', 'title', 'content', 'image', 'is_public',
            'view_count', 'like_count', 'tags', 'tag_ids',
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        article = Article.objects.create(**validated_data)
        article.tags.set(tags)
        return article

class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'author', 'title', 'is_public',
            'view_count', 'like_count', 'tags',
            'created_at'
        ]

class ArticleDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'author', 'title', 'content', 'image', 'is_public',
            'view_count', 'like_count', 'tags', 'comments',
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