from rest_meets_djongo.serializers import DjongoModelSerializer

from api.models import File


class FileSerializer(DjongoModelSerializer):
    class Meta:
        model = File
        fields = '__all__'
