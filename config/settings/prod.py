from .base import *
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

DEBUG = False

ALLOWED_HOSTS = ['whyding.site']

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'db',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# # CORS settings
# CORS_ALLOWED_ORIGINS = [
#     os.getenv('CORS_ALLOWED_ORIGIN'),
# ]

CORS_ALLOW_ALL_ORIGINS = True
