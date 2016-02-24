from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel, ActivatorModel
from django_extensions.db.fields import UUIDField
from django_extensions.db.fields.json import JSONField
from app.services.managers import ServiceManager
import uuid


class Service(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=125, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField(default=False)
    objects = ServiceManager()

    class Meta:
        db_table = 'app_services'
        ordering = ['title']

    def __unicode__(self):
        return self.title


class ServiceIntegration(TimeStampedModel, ActivatorModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='integrations')
    service = models.ForeignKey(Service, related_name='services')
    instances = models.ManyToManyField(
        'repos.Repository', through='repos.RepositoryIntegration'
    )
    config = JSONField()

    class Meta:
        db_table = 'app_services_integrations'
        unique_together = ('user', 'service')
        ordering = ['user']

    def __unicode__(self):
        return '%s >> %s' % (self.user.username, self.service.title)

    @classmethod
    def create(cls, config, **data):
        instance = cls(**data)
        instance.config = config
        return instance
