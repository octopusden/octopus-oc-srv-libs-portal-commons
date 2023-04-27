""" Base settings for both internal and external portals """

import logging
import logging.config
import os
from warnings import warn

from cdt.connections.ConnectionManager import ConnectionManager
# should set regular logging level 
from wwwcdt.logging_settings import DOCKER_LOGGING

from wwwcdt.logging_settings import LOGGING
logging.config.dictConfig(LOGGING)

def portal_parameter(name, default):
    return os.getenv(name, default)

logger = logging.getLogger('')
logger.addHandler(logging.StreamHandler())
# log verbose during startup
logger.setLevel(logging.DEBUG)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = portal_parameter("STATIC_ROOT_PATH", "/local/django/static")
MEDIA_ROOT = portal_parameter("MEDIA_ROOT_PATH", "/local/django/media")

try:
    import ldap
    from wwwcdt.ldap_settings import *
except:
    warn("No LDAP support installed!")
    AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'SECRET_KEY'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (os.environ.get("DJANGO_DEBUG_MODE", "") == "True")

ALLOWED_HOSTS = ["*"]

# ROOT_URLCONF is specified in concrete app settings

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dlmanager',
    'pagination',
    'django_static_jquery',
    'jqueryui',
    'django_filters',
    'simple_history',
    "checksums",
    "portal_commons",
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
)

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

WSGI_APPLICATION = 'wwwcdt.wsgi.application'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

CONNECTION_MANAGER = ConnectionManager()

DATABASES = CONNECTION_MANAGER.get_psql_django_configuration("PSQL")

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

EXTERNAL_PARAMETERS = {
    "jenkins_update_job": portal_parameter("JENKINS_UPDATE_JOB", "tech.update_confluence"),
}
