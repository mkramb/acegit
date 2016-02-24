from rest_framework import serializers
from app.repos.models import Repository, RepositoryBranch


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = (
            'full_name',
            'html_url',
            'updated_at'
        )


class RepositoryBranchSerializer(serializers.ModelSerializer):
    commits = serializers.SerializerMethodField('clean_json')

    class Meta:
        model = RepositoryBranch
        fields = (
            'name',
            'head',
            'commits'
        )

    def clean_json(self, obj):
        return obj.commits
