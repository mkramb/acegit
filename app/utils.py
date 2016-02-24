from __future__ import absolute_import
from django.core.cache import cache
from celery.result import AsyncResult


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.get(**kwargs)
    except:
        return None


def is_cached(user_id, task_path, **params):
    data = task_path.split('.')

    task_name = '.'.join(data[-1:])
    task_module = '.'.join(data[:-1])

    cache_key = 'tasks:%s:%s' % (user_id, task_path)
    result = cache.get(cache_key)

    if result:
        result = AsyncResult(result).ready()
    else:
        module = __import__(
            task_module,
            fromlist=[task_name]
        )
        task = getattr(module, task_name)
        cache.set(cache_key, task.delay(user_id, **params).task_id)

    if result:
        cache.delete(cache_key)

    return result
