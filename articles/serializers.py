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

class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    comments_count = serializers.IntegerField(read_only=True)
    comments = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'image', 'is_public', 'created_at', 
                 'author_name', 'view_count', 'likes_count', 'comments', 'tags']

    def get_comments(self, obj):
        if self.context['request'].parser_context['kwargs'].get('pk'):
            comments = obj.comments.select_related('author')\
                .prefetch_related('replies__author')\
                .filter(parent=None)
            return CommentSerializer(comments, many=True).data
        return [] 