from django.contrib.auth.models import User

from rest_framework import serializers

from api.models import File


class FileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = File
        fields = ['id', 'owner', 'isFile', 'name', 'path', 's3Link', 'deletedDate']


class UserSerializer(serializers.ModelSerializer):
    files = serializers.PrimaryKeyRelatedField(many=True, queryset=File.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'files']
