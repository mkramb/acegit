from django.db import models
from django.contrib.auth.models import User
from app.repos.models import Repository, RepositoryBranch


class TrelloCard(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    user = models.ForeignKey(
        User, null=True, blank=True, related_name='trello_card'
    )
    repository = models.ForeignKey(Repository, related_name='trello_card')
    branch = models.ForeignKey(RepositoryBranch, related_name='trello_card')

    class Meta:
        db_table = 'app_trello_cards'
        unique_together = ('id', 'repository')

    def __unicode__(self):
        return '%s >> %s >> %s' % (self.user.username, self.repository, self.id)

    @classmethod
    def create(cls, card_id, repo, branch):
        instance = cls()
        instance.id = card_id
        instance.repository = repo
        instance.branch = branch
        return instance
