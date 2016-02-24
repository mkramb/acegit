from django.db import transaction
from django.http import Http404
from app.services.models import Service
from django.utils.decorators import method_decorator


class ServiceEnabledMixin(object):
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        if (
            not self.service_name or
            not Service.objects.enabled().
                filter(name=self.service_name).exists()
        ):
            raise Http404()
        return super(ServiceEnabledMixin, self). \
            dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ServiceEnabledMixin, self).get_context_data(**kwargs)
        context.update(service_name=self.service_name)
        return context


class ApiServiceEnabledMixin(object):
    @method_decorator(transaction.atomic)
    def dispatch(self, request, *args, **kwargs):
        self.integration = self.request.user.integrations.get(
            service__name=self.service_name,
            service__status=True
        )
        return super(ApiServiceEnabledMixin, self). \
            dispatch(request, *args, **kwargs)
