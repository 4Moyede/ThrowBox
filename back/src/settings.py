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
ROOT_DIR = os.path.dirname(BASE_DIR)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(260)g60q&3xnru*=5#qgvi-=^grq)zc7dt=jl!pi%vy812-bk'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

FRONTEND_DIR = os.path.join(os.path.abspath('../'), 'front')
STATICFILES_DIRS = [
    os.path.join(FRONTEND_DIR, 'dist/')
]

ALLOWED_HOSTS = ['*']
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
        'DIRS': [
             os.path.join(BASE_DIR, 'templates'),
        ],
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

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    "http://localhost:8080",
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
    'AccessToken',
    'ExpiresIn',
    'IdToken',
    'RefreshToken',
    'TokenType',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

# AWS setting file
AWS_REGION = 'ap-northeast-2'
AWS_SETTINGS_FILE = os.path.join(os.path.join(ROOT_DIR, '.aws_key'), 'aws_settings.json')
aws_secret = json.loads(open(AWS_SETTINGS_FILE).read())

# S3 Storage
S3_ACCESS_KEY_ID = aws_secret['s3']['access_key_id']
S3_SECRET_ACCESS_KEY = aws_secret['s3']['secret_access_key']
S3_STORAGE_BUCKET_NAME = aws_secret['s3']['s3_bucket_name']
S3_ACCESS_URL = aws_secret['s3']['s3_access_url']

DEFAULT_FILE_STORAGE = 'src.storages.MediaStorage'
STATICFILES_STORAGE = 'src.storages.StaticStorage'
MEDIAFILES_LOCATION = 'media'
STATICFILES_LOCATION = 'static'

# AWS Congito Access
COGNITO_ACCESS_KEY_ID = aws_secret['cognito']['access_key_id']
COGNITO_SECRET_ACCESS_KEY = aws_secret['cognito']['secret_access_key']
COGNITO_APP_CLIENT_ID = aws_secret['cognito']['app_client_id']
COGNITO_USER_POOL_ID = aws_secret['cognito']['user_pool_id']


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
        'NAME': db_dbName,
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