from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from app.web.views import HookView


urlpatterns = patterns(
    '',
    url(
        r'^$', TemplateView.as_view(template_name='web/home.html'), name='web'
    ),
    url(r'^hook/(?P<repo_id>.+)$', HookView.as_view(), name='web_hook'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
)
