from django.core.cache import cache
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from app.services.views import ServiceView
from app.services.models import ServiceIntegration
from app.services.trello.settings import TRELLO_APPLICATION_KEY
from app.services.trello.forms import ConfigForm
from app.repos.models import RepositoryIntegration
from app.repos.views import AppJSONView
from app.utils import get_or_none, is_cached


class TrelloServiceView(ServiceView, TemplateView):
    service_name = 'trello'


class HomeView(TrelloServiceView, AppJSONView):
    template_name = 'app/services/trello/home.html'

    def dispatch(self, request, *args, **kwargs):
        key = 'services:%s:trello:get_boards' % self.request.user.id
        self.boards = cache.get(key)

        if self.boards:
            cache.set(key, self.boards)

        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = request.POST.get('_token', False)

        if token:
            ServiceIntegration.create(
                {'token': token}, user=request.user, service=self.service
            ).save()
            return redirect('service_trello', self.kwargs['slug'])

        if not self.boards:
            messages.success(
                request,
                _(u'Cache has expired, please try again.')
            )
            return redirect('service_trello', self.kwargs['slug'])

        form = self._get_form()

        if form.is_bound and form.is_valid():
            repoInt = RepositoryIntegration.objects.update_or_create(
                repository=self.repo,
                integration=self.integration
            )
            repoInt[0].config = form.cleaned_data
            repoInt[0].save()
            messages.success(
                request, _(u'Integration is successfully configured.')
            )
            return redirect('service_trello', self.kwargs['slug'])
        return super(HomeView, self).get(request, *args, **kwargs)

    def get_ajax(self, request, *args, **kwargs):
        return self.render_json_response(
            is_cached(
                request.user.id, 'app.services.trello.tasks.get_boards',
                token=self.integration.config['token']
            )
         )

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update(integration=self.integration)
        context.update(key=TRELLO_APPLICATION_KEY)
        context.update(boards=self.boards)

        if self.boards:
            context.update(form=self._get_form())

        return context

    def _get_form(self):
        if not hasattr(self, 'form'):
            data = None

            if self.request.method == 'GET':
                data = get_or_none(self.repo.integrations)

            self.form = ConfigForm(
                self.boards,
                initial={'board': data.config['board'] if data else None},
                data=self.request.POST.copy() or None
            )

        return self.form
