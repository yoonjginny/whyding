#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from django.conf import settings
from config import settings as my_settings  # settings.py를 직접 import

def main():
    """Run administrative tasks."""
    # .env 파일 로드
    ENV_PATH = Path(__file__).resolve().parent / '.env'
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)
    
    # settings 직접 설정
    if not settings.configured:
        settings.configure(default_settings=my_settings)
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
