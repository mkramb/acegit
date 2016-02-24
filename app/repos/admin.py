from django.contrib import admin
from app.repos.models import Repository, RepositoryBranch, \
    RepositoryPull, RepositoryIntegration


admin.site.register(Repository)
admin.site.register(RepositoryBranch)
admin.site.register(RepositoryPull)
admin.site.register(RepositoryIntegration)
