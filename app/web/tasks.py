from __future__ import absolute_import
from django.db import transaction
from celery import shared_task
from app.repos.models import Repository, RepositoryBranch, RepositoryPull
from app.repos.settings import REPO_COMMITS_LIMIT
from app.utils import get_or_none


@shared_task
@transaction.atomic()
def log_commits(repo_id, git_branch, git_head, git_commits):
    repo = Repository.objects.get(pk=repo_id)
    commits = []

    for item in reversed(git_commits):
        commits.append({
            'sha': item['id'],
            'html_url': item['url'],
            'message': item['message'],
            'timestamp': item['timestamp'],
            'committer': item['committer'],
            'author': item['author']
        })

    branch = RepositoryBranch.objects.get_or_create(
        repository=repo,
        name=git_branch
    )

    branch[0].commits = (commits + branch[0].commits)[:REPO_COMMITS_LIMIT]
    branch[0].head = git_head

    if len(branch[0].commits):
        last_commit = branch[0].commits[0]
        repo.updated_at = last_commit['timestamp']
        branch[0].sha = last_commit['sha']

    repo.save()
    branch[0].save()
    return True


@shared_task
@transaction.atomic()
def update_branch(repo_id, branch_name, git_head):
    repo = Repository.objects.get(pk=repo_id)

    if not git_head:
        repo.branches.all().filter(name=branch_name).delete()
    else:
        RepositoryBranch.create(
            repo,
            name=branch_name,
            head=git_head
        ).save()

    return True


@shared_task
@transaction.atomic()
def update_pull(repo_id, status, request):
    repo = Repository.objects.get(pk=repo_id)
    pull = RepositoryPull.objects.update_or_create(
        repository=repo,
        number=request['number']
    )

    pull[0].head = get_or_none(
        repo.branches.all(),
        name=request['head']['ref']
    )
    pull[0].base = get_or_none(
        repo.branches.all(),
        name=request['base']['ref']
    )

    pull[0].html_url = request['html_url']
    pull[0].name = request['title']
    pull[0].description = request['body']
    pull[0].status = status
    pull[0].save()
    return True
