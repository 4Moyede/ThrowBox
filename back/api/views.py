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
        session = boto3.session.Session(aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY, region_name = AWS_REGION)
        s3 = session.resource('s3')
        uploadedList = []
        uploadedFile = request.data.dict()
        for idx, file in enumerate(request.FILES.getlist('file')):
            uploadedFile['isFile'] = request.data.getlist('isFile')[idx]
            s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(Key = file.name, Body =file)
            file_urls = "https://throwbox.s3.ap-northeast-2.amazonaws.com/%s" % file.name
            uploadedFile['s3Link'] = file_urls
            
            uploadedFile['name'] = request.data.getlist('name')[idx]
            uploadedFile['author'] = request.data.getlist('author')[idx]
            
            uploadedFile['path'] = request.data.getlist('path')[idx]
            uploadedFile['fileSize'] = request.data.getlist('fileSize')[idx]
            uploadedFile['createdDate'] = request.data.getlist('createdDate')[idx]

            serializer = FileSerializer(data=uploadedFile)
            if serializer.is_valid():
                serializer.save()
                uploadedList.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(uploadedList, status=status.HTTP_201_CREATED)
            
class FolderUpload(APIView):
    def post(self, request, format=None):
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
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