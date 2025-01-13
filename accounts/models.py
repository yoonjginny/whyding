from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': "이미 사용 중인 이메일입니다.",
        }
    )
    profile_image = models.ImageField(
        upload_to='profile/',
        null=True,
        blank=True
    )
    introduction = models.TextField(
        blank=True,
        help_text='자기소개를 입력하세요.'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
