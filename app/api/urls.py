from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from app.services.models import Service


urlpatterns = patterns('')

for service in Service.objects.enabled():
    urlpatterns += patterns(
        '',
        url(
            r'^/service/%s/' % service.name,
            include('app.services.%s.api.urls' % service.name)
        )
    )

urlpatterns = format_suffix_patterns(urlpatterns)
