from rest_framework import serializers
from .models import Article, Comment, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class RecursiveCommentSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = CommentSerializer(instance, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    replies = RecursiveCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author_name', 'created_at', 'parent', 'replies']

class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'image', 'is_public', 
            'created_at', 'author_name', 'view_count', 
            'likes_count', 'comments_count', 'tags'
        ]

class ArticleDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'image', 'is_public', 
            'created_at', 'author_name', 'view_count', 
            'likes_count', 'comments_count', 'comments', 'tags'
        ]

    def get_comments(self, obj):
        comments = obj.comments.select_related('author')\
            .prefetch_related('replies__author')\
            .filter(parent=None)
        return CommentSerializer(comments, many=True).data 

class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'author',
            'created_at', 'updated_at', 'tags',
            'likes_count', 'comments_count'
        ] 