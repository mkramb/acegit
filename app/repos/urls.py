from django.conf.urls import patterns, url, include
from app.services.models import Service
from app.repos.views import HomeView, DetailView, ImportView, \
    ImportCheckView, AddonsView


js_info_dict = {
    'domain': 'djangojs',
    'packages': ('app.repos',),
}

urlpatterns = patterns('')

for service in Service.objects.enabled():
    urlpatterns += patterns(
        '',
        url(
            r'^detail/(?P<slug>.+)/%s' % service.name,
            include('app.services.%s.urls' % service.name)
        )
    )

urlpatterns += patterns(
    '',
    url(
        r'^catalog.js$', 'django.views.i18n.javascript_catalog',
        js_info_dict, name='app_catalog'
    ),
    url(
        r'^logout$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='app_logout'
    ),
    url(r'^detail/(?P<slug>.+)/', DetailView.as_view(), name='app_detail'),
    url(r'^import/check$', ImportCheckView.as_view(), name='app_import_check'),
    url(r'^import/', ImportView.as_view(), name='app_import'),
    url(r'^addons/', AddonsView.as_view(), name='app_addons'),
    url(r'^$', HomeView.as_view(), name='app'),
)
