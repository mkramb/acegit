from django.db import models


class ServiceManager(models.Manager):
    def enabled(self):
        return self.filter(status=True)
