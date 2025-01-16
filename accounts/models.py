from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': "이미 사용 중인 이메일입니다.",
        },
        help_text='로그인에 사용할 이메일 주소를 입력하세요. (필수)'
    )
    profile_image = models.ImageField(
        upload_to='profile/',
        null=True,
        blank=True,
        help_text='프로필 이미지를 업로드하세요. (선택사항)'
    )
    introduction = models.TextField(
        blank=True,
        help_text='자기소개를 입력하세요. (선택사항)'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text='사용자 이름을 입력하세요. (필수)',
        error_messages={
            'unique': '이미 사용 중인 사용자 이름입니다.'
        }
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
