from django.db import models
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files import File

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/%Y/%m/%d/', null=True, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_articles', blank=True)
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    bookmarks = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='bookmarked_articles', blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.image:
            # 이미지 리사이징
            img = Image.open(self.image)
            if img.height > 1080 or img.width > 1920:
                output_size = (1920, 1080)
                img.thumbnail(output_size)
                # 이미지 품질 최적화
                img_io = BytesIO()
                img.save(img_io, format='JPEG', quality=85)
                self.image = File(img_io, name=self.image.name)
        super().save(*args, **kwargs)

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['created_at']
