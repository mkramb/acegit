from django.db import IntegrityError
from rest_framework.generics import ListAPIView, RetrieveAPIView, \
    CreateAPIView, get_object_or_404
from rest_framework.response import Response
from app.services.trello.models import TrelloCard
from app.services.mixins import ApiServiceEnabledMixin
from app.repos.models import Repository
from app.api.settings import STATUS_CODE
from app.api.serializers import RepositorySerializer, \
    RepositoryBranchSerializer


class TrelloServiceEnabledMixin(ApiServiceEnabledMixin):
    service_name = 'trello'


class BoardView(TrelloServiceEnabledMixin, ListAPIView):
    serializer_class = RepositorySerializer

    def get_queryset(self):
        data = []

        if self.integration:
            repos = self.integration.instances.all()

            for repo in repos.select_related('integrations'):
                for integration in repo.integrations.all():
                    board = integration.config.get('board', None)
                    if board == self.kwargs['id']:
                        data.append(integration.repository)
        return data


class CardView(TrelloServiceEnabledMixin, RetrieveAPIView, CreateAPIView):
    serializer_class = RepositoryBranchSerializer

    def retrieve(self, request, *args, **kwargs):
        card = get_object_or_404(
            TrelloCard,
            pk=self.kwargs['id'],
            user=request.user
        )

        serializer = self.get_serializer(card.branch)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        branch_name = filter(
            str.isalnum, str(request.data['name'])
        )

        repo = get_object_or_404(
            Repository,
            full_name=request.data['repository'],
            user=request.user
        )

        exists = TrelloCard.objects.filter(pk=self.kwargs['id']).exists() \
            | TrelloCard.objects.filter(
                repository=repo,
                branch__name=branch_name
            ).exists()

        if exists:
            return Response(status=STATUS_CODE['CONFILCT'])

        try:
            branch = repo.branches.get(name='master')
            branch.name = branch_name
            branch.commits = None
            branch.pk = None
            branch.save()

            TrelloCard(
                pk=self.kwargs['id'],
                user=request.user,
                repository=repo,
                branch=branch
            ).save()
        except IntegrityError:
            return Response(
                status=STATUS_CODE['BAD']
            )

        return Response(
            status=STATUS_CODE['CREATED']
        )
