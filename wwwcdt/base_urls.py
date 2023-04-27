""" Basic url configuration to be inherited by both portals """

from django.conf.urls import include, url


def get_portal_app_urls(app_name):
    # redirect both explicit "dl" and default url
    app_urls = "%s.urls" % app_name
    return [
        url(r'^$', include(app_urls, namespace='dlmanager')),
        url(r'^dl/', include(app_urls, namespace='dlmanager')),
    ]


urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls', namespace='accounts')),
]

handler404 = "portal_commons.views_errors.http404"
handler500 = "portal_commons.views_errors.http500"
