from django.contrib.auth.models import User

from rest_framework import serializers

from api.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'owner', 'isFile', 'name', 'path', 's3Link', 'deletedDate']

