from django.views.generic import TemplateView, View
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.core.cache import cache
from django.http import Http404
from braces.views import JSONResponseMixin, AjaxResponseMixin
from app.repos.mixins import LoginRequiredMixin
from app.repos.models import Repository
from app.services.models import Service
from app.repos.tasks import import_repos, unlink_hook
from app.utils import is_cached


class AppTemplateView(LoginRequiredMixin, TemplateView):
    menu_selected = 'repositories'

    def get_context_data(self, **kwargs):
        context = super(AppTemplateView, self).get_context_data(**kwargs)
        context.update(menu_selected=self.menu_selected)
        return context


class AppJSONView(
    LoginRequiredMixin,
    AjaxResponseMixin,
    JSONResponseMixin,
    View
):
    pass


class HomeView(AppTemplateView):
    template_name = 'app/repos/home.html'

    def get(self, request, *args, **kwargs):
        if not request.user.repositories.count():
            return redirect('app_import')
        return super(HomeView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update(repos=self.request.user.repositories.all())
        return context


class DetailView(AppTemplateView):
    template_name = 'app/repos/detail.html'

    def get(self, request, *args, **kwargs):
        try:
            self.repo = self.request.user.repositories.get(
                slug=self.kwargs['slug']
            )
        except Repository.DoesNotExist:
            raise Http404()
        return super(DetailView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get('_method', False) == 'delete':
            repo = get_object_or_404(
                Repository,
                slug=self.kwargs['slug'],
                user=request.user
            )
            repo.delete()
            unlink_hook.delay(request.user.id, repo.name, repo.hook_id)
            messages.success(request, _(u'Unlinked selected repository.'))
            return redirect('app')
        raise Http404()

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context.update(services=Service.objects.enabled())
        context.update(repo=self.repo)
        return context


class ImportView(AppTemplateView):
    template_name = 'app/repos/import.html'

    def dispatch(self, request, *args, **kwargs):
        key = 'repos:%s' % self.request.user.id
        self.repos = cache.get(key)

        if self.repos:
            cache.set(key, self.repos)
        return super(ImportView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.repos:
            messages.success(
                request,
               _(u'Cache has expired, please try again.')
            )
            return redirect('app_import')

        repo_selected = request.POST.getlist('repos_selected', [])
        repo_linked = Repository.objects.values_list('full_name', flat=True)

        if not len(repo_selected):
            return redirect('app_import')

        repos = [
            Repository.create(request.user, repo) for repo in self.repos
            if repo['full_name'] in repo_selected
            and repo['full_name'] not in repo_linked
        ]

        Repository.objects.bulk_create(repos)
        import_repos.delay(
            request.user.id,
            [repo.full_name for repo in repos]
        )
        return redirect('app')

    def get_context_data(self, **kwargs):
        context = super(ImportView, self).get_context_data(**kwargs)
        context.update(repos=self.repos)
        return context


class ImportCheckView(AppJSONView):
    def get_ajax(self, request, *args, **kwargs):
        return self.render_json_response(
            is_cached(request.user.id, 'app.repos.tasks.cache_repos')
        )


class AddonsView(AppTemplateView):
    template_name = 'app/addons.html'
    menu_selected = 'addons'

