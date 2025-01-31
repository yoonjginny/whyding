from django.db import models
from django.conf import settings

class Article(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='articles',
        on_delete=models.CASCADE
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='제목을 입력하세요 (선택사항)'
    )
    content = models.TextField(
        help_text='내용을 입력하세요 (필수사항)'
    )
    image = models.ImageField(
        upload_to='articles/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text='이미지를 업로드하세요 (선택사항)'
    )
    is_public = models.BooleanField(
        default=True,
        help_text='공개 여부를 설정하세요 (기본값: 공개)'
    )
    view_count = models.PositiveIntegerField(
        default=0,
        help_text='조회수 (자동 집계)',
        editable=False
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_articles',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or '제목 없음'
    
    def increase_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])

class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        related_name='comments',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        content = self.content[:30]
        if len(self.content) > 30:
            content += '...'
        return f'{self.author.username}: {content}'
