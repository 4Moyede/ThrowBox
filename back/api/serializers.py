from django.contrib.auth.models import User

from rest_framework import serializers

from api.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'author', 'isFile', 'name', 'path', 's3Link', 'fileSize', 'createdDate', 'deletedDate']
