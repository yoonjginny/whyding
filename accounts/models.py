from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True)
    profile_image = models.ImageField(upload_to='profile/', null=True, blank=True)
    introduction = models.TextField(blank=True)
    
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        swappable = 'AUTH_USER_MODEL'
    
    def __str__(self):
        return self.email
