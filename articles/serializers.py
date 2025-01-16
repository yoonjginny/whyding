from rest_framework import serializers
from .models import Article, Comment
from accounts.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'content', 'parent',
            'replies', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'content': {'required': True},
            'parent': {'write_only': True, 'required': False}
        }
    
    def get_replies(self, obj):
        if hasattr(obj, 'replies'):
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    view_count = serializers.IntegerField(read_only=True)
    image = serializers.ImageField(required=False)
    
    class Meta:
        model = Article
        fields = [
            'id', 'author', 'title', 'content',
            'is_public', 'image', 'view_count',
            'like_count', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'title': {
                'required': False,
                'help_text': '제목 (선택)',
                'allow_blank': True
            },
            'content': {
                'required': True,
                'help_text': '내용 (필수)',
                'error_messages': {
                    'required': '내용을 입력해주세요.'
                }
            },
            'is_public': {
                'required': False,
                'help_text': '공개 여부 (선택, 기본값: 공개)',
                'default': True
            },
            'image': {
                'required': False,
                'help_text': '이미지 (선택)'
            }
        }

class ArticleListSerializer(ArticleSerializer):
    class Meta(ArticleSerializer.Meta):
        fields = [
            'id', 'author', 'title', 'is_public',
            'view_count', 'like_count', 'created_at'
        ]

class ArticleDetailSerializer(ArticleSerializer):
    comments = serializers.SerializerMethodField()
    
    class Meta(ArticleSerializer.Meta):
        fields = ArticleSerializer.Meta.fields + ['comments']
    
    def get_comments(self, obj):
        comments = obj.comments.filter(parent=None)
        return CommentSerializer(comments, many=True).data

class ArticleLikeResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="처리 결과 메시지")
    like_count = serializers.IntegerField(help_text="현재 좋아요 수")