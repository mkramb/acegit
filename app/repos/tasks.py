from __future__ import absolute_import
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db import transaction
from django.conf import settings
from celery import shared_task
from libsaas.services import github
from app.repos.models import Repository, RepositoryBranch
from app.repos.settings import REPO_COMMITS_LIMIT, REPO_KEYS


@shared_task
def cache_repos(user_id):
    user = User.objects.get(pk=user_id)
    service = github.GitHub(
        user.social_auth.get().extra_data['access_token']
    )

    data = []
    for git_repo in service.repos().get():
        data.append({
            key: value for key, value in dict(git_repo).iteritems()
            if key in REPO_KEYS
        })

    cache.set('repos:%s' % user_id, data)
    return True


@shared_task
@transaction.atomic()
def import_repos(user_id, repo_names):
    user = User.objects.get(pk=user_id)
    service = github.GitHub(
        user.social_auth.get().extra_data['access_token']
    )

    for repo in Repository.objects.filter(full_name__in=repo_names):
        git_repo = service.repo(user.username, repo.name)

        for git_branch in git_repo.branches():
            branch = RepositoryBranch.objects.get_or_create(
                repository=repo,
                name=git_branch['name']
            )

            commits = []
            git_commits = git_repo.commits().get(
                sha=git_branch['name']
            )[:REPO_COMMITS_LIMIT]

            for item in git_commits:
                commits.append({
                    'sha': item['sha'],
                    'html_url': item['html_url'],
                    'message': item['commit']['message'],
                    'timestamp': item['commit']['committer']['date'],
                    'committer': item['commit']['committer'],
                    'author': item['commit']['author']
                })

            branch[0].commits = commits
            branch[0].head = commits[0]['sha']
            branch[0].save()

        git_hook = git_repo.hooks().create({
            'name': 'web',
            'active': True,
            'events': ['push', 'pull_request'],
            'config': {
                'url': '%s/hook/%s' % (settings.PROJECT_URL, repo.id),
                'content_type': 'json'
            }
        })

        repo.hook_id = git_hook['id']
        repo.save()
    return True


@shared_task
def unlink_hook(user_id, repo_name, hook_id):
    user = User.objects.get(pk=user_id)
    service = github.GitHub(
        user.social_auth.get().extra_data['access_token']
    )

    service.repo(user.username, repo_name) \
        .hook(hook_id).delete()
    return True
