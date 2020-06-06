"""
Django settings for src project.
Generated by 'django-admin startproject' using Django 3.0.5.
For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import os
import json
import djongo
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(260)g60q&3xnru*=5#qgvi-=^grq)zc7dt=jl!pi%vy812-bk'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'api.apps.ApiConfig',
    'storages',
    'drf_yasg',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]
ROOT_URLCONF = 'src.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'src.wsgi.application'
# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/front/'
# CORS settings
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    "http://127.0.0.1:12233",
    "http://localhost:8080",
    "http://127.0.0.1:9000",
    "mongodb://172.31.86.151",
]
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
)
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
STATIC_DIR = os.path.join(ROOT_DIR, 'front')
STATICFILES_DIRS = [
    STATIC_DIR,
]
# AWS Access
AWS_SETTINGS_FILE = os.path.join(os.path.join(ROOT_DIR, '.aws_key'), 'aws_settings.json')
aws_secret = json.loads(open(AWS_SETTINGS_FILE).read())
AWS_ACCESS_KEY_ID = aws_secret['aws']['access_key_id']
AWS_SECRET_ACCESS_KEY = aws_secret['aws']['secret_access_key']
AWS_STORAGE_BUCKET_NAME = aws_secret['aws']['s3_bucket_name']
AWS_REGION = 'ap-northeast-2'
# S3 Storage
DEFAULT_FILE_STORAGE = 'src.storages.MediaStorage'
STATICFILES_STORAGE = 'src.storages.StaticStorage'
MEDIAFILES_LOCATION = 'media'
STATICFILES_LOCATION = 'static'
#database
DATABASE_SETTINGS_FILE = os.path.join(os.path.join(ROOT_DIR, '.database_key'), 'db_settings.json')
db_info = json.loads(open(DATABASE_SETTINGS_FILE).read())
db_dbName = db_info['client']['db']
db_host = db_info['client']['host']
db_username=db_info['client']['username']
db_port=db_info['client']['port']
db_pwd=db_info['client']['password']
db_authSource=db_info['client']['authSource']
db_authMechanism=db_info['client']['authMechanism']
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'ENFORCE_SCHEMA': False,
        'NAME':db_dbName ,
        'CLIENT': {
            'host': db_host,
            'port': db_port,
            'username': db_username,
            'password': db_pwd,
            'authSource': db_authSource,
            'authMechanism': db_authMechanism,
        },
    }    
} 