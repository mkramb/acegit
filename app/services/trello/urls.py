from django.conf.urls import patterns, url
from app.services.trello.views import HomeView


urlpatterns = patterns(
    '',
    url(r'^', HomeView.as_view(), name='service_trello'),
)
