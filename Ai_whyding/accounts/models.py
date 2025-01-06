from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    name = models.CharField(max_length=30)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    username = models.CharField(
        max_length=150,
        unique=True,
        error_messages={
            'unique': '아이디가 이미 존재합니다.',
        },
    )

    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': '이메일이 이미 존재합니다.',
        },
    )

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'

    def __str__(self):
        return self.username
