from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields.json import JSONField
from django_extensions.db.fields import UUIDField
from slugify import slugify
from app.services.models import ServiceIntegration
import uuid


class Repository(TimeStampedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, null=True, blank=True, related_name='repositories'
    )
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=128, db_index=True)
    full_name = models.CharField(max_length=256, db_index=True, unique=True)
    html_url = models.URLField()
    description = models.TextField()
    private = models.BooleanField(default=False)
    fork = models.BooleanField(default=False)
    hook_id = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(editable=False)

    class Meta:
        db_table = 'app_repos'
        unique_together = ('user', 'full_name')
        ordering = ['full_name']

    def __unicode__(self):
        return self.full_name

    @classmethod
    def create(cls, user, data):
        instance = cls(**data)
        instance.slug = slugify(data['full_name'])
        instance.user = user
        return instance


class RepositoryBranch(TimeStampedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    repository = models.ForeignKey(Repository, related_name='branches')
    head = models.CharField(max_length=128, db_index=True)
    name = models.CharField(max_length=128, db_index=True)
    commits = JSONField(default=[])

    class Meta:
        db_table = 'app_repos_branches'
        unique_together = ('repository', 'name')
        ordering = ['repository']

    def __unicode__(self):
        return '%s > %s' % (self.repository.full_name, self.name)

    @classmethod
    def create(cls, repo, **data):
        instance = cls(**data)
        instance.repository = repo
        return instance


class RepositoryPull(TimeStampedModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    repository = models.ForeignKey(Repository, related_name='pulls')
    head = models.ForeignKey(
        RepositoryBranch, null=True, related_name='pulls_head'
    )
    base = models.ForeignKey(
        RepositoryBranch, null=True, related_name='pulls_base'
    )
    status = models.CharField(max_length=32, db_index=True)
    number = models.IntegerField(db_index=True)
    name = models.CharField(max_length=128)
    description = models.TextField()
    html_url = models.URLField()

    class Meta:
        db_table = 'app_repos_pulls'
        unique_together = ('repository', 'number')
        ordering = ['repository']

    def __unicode__(self):
        return '%s > %s' % (self.repository.full_name, self.name)


class RepositoryIntegration(TimeStampedModel):
    repository = models.ForeignKey(Repository, related_name='integrations')
    integration = models.ForeignKey(ServiceIntegration)
    config = JSONField()

    class Meta:
        db_table = 'app_repos_integrations'
        ordering = ['repository']

    def __unicode__(self):
        return self.repository.full_name

