from django.contrib import admin
from app.services.models import Service, ServiceIntegration


admin.site.register(Service)
admin.site.register(ServiceIntegration)
