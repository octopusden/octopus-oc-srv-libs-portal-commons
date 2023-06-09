from django.conf import settings
import django
import os

if not settings.configured:
    if not os.path.isdir('/tmp'):
        os.makedirs('/tmp')

    settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': '/tmp/test.db',
                    }},
                USE_TZ=True,
                TIME_ZONE='Etc/UTC',
                INSTALLED_APPS=[
                    'oc_delivery_apps.checksums',
                    'oc_delivery_apps.dlmanager',
                    'oc_portal_commons',
                    'simple_history',
                    'django.contrib.contenttypes',
                    'django.contrib.auth',
                    'django_filters'
                ],
    )

    django.setup()
