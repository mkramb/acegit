from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from app.repos.models import Repository
from app.web.tasks import log_commits, update_branch, update_pull
import logging
import json
import re


logger = logging.getLogger(__name__)


class HookView(View):
    @method_decorator(csrf_exempt)
    @method_decorator(require_http_methods(['POST']))
    def dispatch(self, *args, **kwargs):
        if self.request.method == 'POST' \
          and self.request.META.get('CONTENT_TYPE') == 'application/json':
            try:
                event = '_%s' % self.request.META.get('HTTP_X_GITHUB_EVENT')

                if hasattr(self, event):
                    getattr(self, event)(
                        get_object_or_404(
                            Repository, pk=self.kwargs['repo_id']
                        ), json.loads(self.request.body)
                    )
            except Exception:
                logger.exception(
                    self.request.META.get('X-GitHub-Delivery', None)
                )
            return HttpResponse('OK')
        return HttpResponseNotFound()

    def _push(self, repo, payload):
        match = re.match(
            r"refs/heads/(?P<branch>.*)", payload['ref']
        )
        git_branch = match.groupdict()['branch']

        if payload['created'] or payload['deleted']:
            update_branch.delay(
                repo.id,
                git_branch,
                payload['head_commit']['id']
                if payload['head_commit'] else None
            )

        if 'commits' in payload and len(payload['commits']):
            log_commits.delay(
                repo.id,
                git_branch,
                payload['head_commit']['id'],
                payload['commits']
            )

    def _pull_request(self, repo, payload):
        update_pull.delay(
            repo.id,
            payload['action'],
            payload['pull_request']
        )
