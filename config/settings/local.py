from .base import *
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '52.79.162.173', 'whyding.site']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
