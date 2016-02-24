from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import get_object_or_404
from app.repos.views import AppTemplateView
from app.services.mixins import ServiceEnabledMixin
from app.services.models import Service
from app.utils import get_or_none


class ServiceView(ServiceEnabledMixin, AppTemplateView):
    redirect_field_name = REDIRECT_FIELD_NAME
    login_url = None

    @method_decorator(login_required(
        redirect_field_name=redirect_field_name, login_url=login_url
    ))
    def dispatch(self, request, *args, **kwargs):
        self.service = get_object_or_404(Service, name=self.service_name)
        self.integration = get_or_none(
            self.service.services,
            service__name=self.service_name
        )

        if self.kwargs['slug']:
            self.repo = request.user.repositories.get(
                slug=self.kwargs['slug']
            )

        return super(ServiceView, self). \
            dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ServiceView, self).get_context_data(**kwargs)
        context.update(service=self.service)
        context.update(services=Service.objects.enabled())
        context.update(repo=self.repo or None)
        return context
