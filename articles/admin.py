from django.contrib import admin
from .models import Article, Comment

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_public', 'view_count', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    raw_id_fields = ('author',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content_preview', 'article', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'article__title')
    raw_id_fields = ('author', 'article', 'parent')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '내용 미리보기'