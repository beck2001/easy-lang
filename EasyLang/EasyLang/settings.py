"""
Django settings for EasyLang project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-@=vpx)kauyq&g@i8cg#t*n+5f_2dura!i8lix_*gil*we1k$m('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mainApp',
    'mathfilters',
    'tgbot',
    'django_crontab',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'EasyLang.onlyauthmiddleware.onlyauthmiddleware',
]

ROOT_URLCONF = 'EasyLang.urls'

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
                'EasyLang.contexts.projects_context',
                'EasyLang.contexts.createProjectForm',
                'EasyLang.contexts.userData'
            ],
        },
    },
]

WSGI_APPLICATION = 'EasyLang.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

# ru +6 almaty
LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Asia/Almaty'
# TIME_ZONE = 'UTC +6' no need to change




# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "mainApp.User"

TELEGRAM_API_TOKEN = "6734545713:AAG33psIDtMkiYlwNmgFhWU3Giwh4-PlrrU"
TELEGRAM_BOT_URL = "https://t.me/easy_lang_translate_bot"


    # path('notify_that_project_finished', views.notify_that_project_finished, name="notify_that_project_finished"), every day in 17 30
    # path('notify_to_translate', views.notify_to_translate, name="notify_to_translate"), every day in 17 30
    # path('translator_summary', views.translator_summary, name="translator_summary"), every friday in 18 30
    # path('editor_summary', views.editor_summary, name="editor_summary"), every friday in 18 30
CRONJOBS = [
    ('30 17 * * *', 'mainApp.cron.notify_to_translate'),
    ('30 18 * * 5', 'mainApp.cron.translator_summary'),
    ('30 18 * * 5', 'mainApp.cron.editor_summary'),
]
