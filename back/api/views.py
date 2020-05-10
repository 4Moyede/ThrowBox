import json
import boto3

from django.http import HttpResponse
from django.http import Http404

from api.models import File
from api.serializers import FileSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from src.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_REGION
from boto3.session import Session

class FileList(APIView):
    def get(self, request, format=None):
        path = request.GET.get('path', None)
        queryset = File.objects.filter(path=path)
        serializer = FileSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FileUpload(APIView):
    def post(self, request, format=None):
        
        for file in request.FILES.getlist('file'):
            print(file)
            session = boto3.session.Session(aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY, region_name = AWS_REGION)
            s3 = session.resource('s3')
            s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(Key = file.name, Body =file)
        file_urls = "https://throwbox.s3.ap-northeast-2.amazonaws.com/%s" % file.name
        request.data['s3Link'] = file_urls
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileDownload(APIView):
    def get_object(self, pk):
        try:
            return File.objects.get(pk=pk)
        except File.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        file = self.get_object(pk)
        serializer = FileSerializer(file)
        response_data = {}
        response_data[file.s3Link] = serializer.data.get(file.s3Link)
        return HttpResponse(json.dumps(response_data), content_type="application/json")