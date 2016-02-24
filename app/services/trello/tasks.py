from __future__ import absolute_import
from django.core.cache import cache
from celery import shared_task
from libsaas.services import trello
from app.services.trello.settings import TRELLO_APPLICATION_KEY


BOARD_KEYS = [
    'id',
    'name',
    'shortUrl',
    'desc'
]


@shared_task
def get_boards(user_id, token):
    service = trello.Trello(TRELLO_APPLICATION_KEY, token)
    data = []

    for board in service.me().boards().get():
        if not board['closed']:
            data.append({
                key: value for key, value in dict(board).iteritems()
                if key in BOARD_KEYS
            })

    cache.set('services:%s:trello:get_boards' % user_id, data)
    return True
