#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '^1)5vh#kddfkvf(06xuf!a=3h&(d)15+t!+7r#18xn!a@%=@m+'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'rest_framework',
    'social_django',
    'authentification.apps.AuthentificationConfig',
    'django_extensions',
    'debug_toolbar',
    'feedbacks.apps.FeedbacksConfig',
    'coaches.apps.CoachesConfig',
    'students.apps.StudentsConfig',
    'courses.apps.CoursesConfig',
    'quadratic.apps.QuadraticConfig',
    'polls.apps.PollsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.google.GoogleOAuth',)

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'pybursa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'pybursa.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Yekaterinburg'

USE_I18N = True

USE_L10N = True

USE_TZ = True

EMAIL_HOST = '127.0.0.1'

EMAIL_PORT = '1025'

ADMINS = [('admin', 'admin@example.com')]

SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_USER_MODEL = 'auth.User'
SOCIAL_AUTH_GITHUB_SCOPE = ['public_repo']
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'authentification.pipeline.get_repos',
    'authentification.pipeline.get_graph',
)

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')
                            
INTERNAL_IPS = ['127.0.0.1']

LOGIN_REDIRECT_URL = '/'

LOGGING = { 'version': 1,
            'disable_existing_loggers': False,
            'loggers': { 'courses': { 'handlers': ['courses_logger'],
                                      'level': 'DEBUG', },
                         'students': { 'handlers': ['students_logger'],
                                       'level': 'WARNING' } },
            'handlers': { 'courses_logger': { 'level': 'DEBUG',
                                              'class': 'logging.FileHandler',
                                              'filename': os.path.join(BASE_DIR, 'courses_logger.log'),
                                              'formatter': 'simple' },
                          'students_logger': { 'level': 'WARNING',
                                               'class': 'logging.FileHandler',
                                               'filename': os.path.join(BASE_DIR, 'students_logger.log'),
                                               'formatter': 'verbose' } },
            'formatters': { 'simple': { 'format': 'Уровень %(levelname)s: "%(message)s"' },
                            'verbose': { 'format': 'Уровень %(levelname)s: "%(message)s", %(asctime)s, %(funcName)s, %(module)s' } } }

try:
    from pybursa.local_settings import *
except ImportError:
    print('Warning! Local settings are not defined!')
