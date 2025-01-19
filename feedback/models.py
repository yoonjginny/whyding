from django.db import models
from django.conf import settings

class Feedback(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    content = models.TextField(help_text='피드백 내용')
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text='서비스 평가 (1-5점)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
