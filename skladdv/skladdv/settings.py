from pathlib import Path

from .dbconfig import configuration

from .smtp_email_conf import email_configuration

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-f2_on8iujlkk5_q2^y*y*!^*6l*qm*4n(+_44mb-t&a@%=fz4='

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop.apps.ShopConfig',
    'mptt',
    'django_mptt_admin',
    'django_filters'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'skladdv.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [Path(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'skladdv.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'skladdv',
        'USER': configuration['user_name'],
        'PASSWORD': configuration['password'],
        'HOST': '172.19.0.2',#это внутренний ip контейнера с postgress(только так сработало)
        #данный внутр ip назначает доккер когда запускает контейнер
        'PORT': '5432',
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


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Vladivostok'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'

STATICFILES_DIRS = [
    Path(BASE_DIR, "static"),
]

MEDIA_ROOT = Path(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'

DEFAULT_FROM_EMAIL = email_configuration['DEFAULT_FROM_EMAIL']
EMAIL_HOST = email_configuration['EMAIL_HOST']
EMAIL_HOST_USER = email_configuration['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = email_configuration['EMAIL_HOST_PASSWORD']
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

CUSTOM_CART_SESSION_ID = 'custom_cart'
STAFF_CART_SESSION_ID = 'staff_cart'

