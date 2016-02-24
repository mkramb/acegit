from django.conf.urls import patterns, url
from app.services.trello.api.views import BoardView, CardView


urlpatterns = patterns(
    '',
    url(r'board/(?P<id>.+)$', BoardView.as_view()),
    url(r'card/(?P<id>.+)$', CardView.as_view())
)
