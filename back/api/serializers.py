from rest_framework import serializers
from api.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'fid', 'author', 'isFile', 'name', 'path', 's3Link', 'createdDate', 'deletedDate']
