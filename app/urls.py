from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^not-found', 'django.views.defaults.page_not_found'),
    url(r'^bad-request', 'django.views.defaults.bad_request'),
    url(r'^api', include('app.api.urls')),
    url(r'^app/', include('app.repos.urls')),
    url(r'^root/', include(admin.site.urls)),
    url(r"^su/", include('django_su.urls')),
    url(r'^', include('app.web.urls')),
)
