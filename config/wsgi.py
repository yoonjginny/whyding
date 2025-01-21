"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application
from django.conf import settings
from config import settings as my_settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / '.env'

# Load environment variables from .env file
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# settings 직접 설정
if not settings.configured:
    settings.configure(default_settings=my_settings)

application = get_wsgi_application()
