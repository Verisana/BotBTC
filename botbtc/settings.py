import os
from celery.schedules import crontab

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '^1)5vh#kddfkvf(06xuf!a=3h&(d)15+t!+7r#18xn!a@%=@m+'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django_celery_results',
    'profiles.apps.ProfilesConfig',
    'ad_bot.apps.AdBotConfig',
    'django_extensions',
    'debug_toolbar',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'botbtc.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'botbtc.wsgi.application'


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

AUTH_USER_MODEL = 'profiles.Profile'

ADMINS = [('admin', 'admin@example.com')]

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')

INTERNAL_IPS = ['127.0.0.1']

LOGIN_REDIRECT_URL = '/'

CELERY_TIMEZONE = 'Asia/Yekaterinburg'

CELERY_RESULT_BACKEND = 'rpc://'

CELERY_BEAT_SCHEDULE = {
    'adbot_runner': {
        'task': 'ad_bot.tasks.adbot_runner',
        'schedule': 1.0},
    'opentrades_cleaner': {
        'task': 'ad_bot.tasks.opentrades_cleaner',
        'schedule': 300.0},
    'calculate_report': {
        'task': 'ad_bot.tasks.calculate_report',
        'schedule': crontab(minute='00', hour='12')},
    'executing_checker': {
        'task': 'ad_bot.tasks.executing_checker',
        'schedule': 30.0},
}

CELERY_TASK_ROUTES = {'ad_bot.tasks.run_bot': {'queue': 'run_bot'},
                      'ad_bot.tasks.message_bot': {'queue': 'run_bot'},
                      'ad_bot.tasks.opentrades_cleaner': {'queue': 'run_bot'},
                      'ad_bot.tasks.calculate_report': {'queue': 'calculate_report'},
                      'ad_bot.tasks.executing_checker': {'queue': 'executing_checker'},
                    }

try:
    from botbtc.local_settings import *
except ImportError:
    print('Warning! Local settings are not defined!')
