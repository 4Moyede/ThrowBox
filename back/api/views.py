from django.http import HttpResponse
from django.core import serializers

from api.models import File
from api.serializers import FileSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import boto3
from boto3.session import Session
from src.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_REGION


class FileList(APIView):
    def get(self, request, format=None):
        path = request.GET.get('path', None)
        queryset = File.objects.filter(path=path)
        serializer = FileSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FileUpload(APIView):
    def checkDuplicate(self, idx, name, path):
        queryset = File.objects.filter(name=name, path=path)
        if queryset.values_list():
            dot = name.rfind('.')
            new_name = ""
            if idx is 1:
                new_name = name[:dot] + " (" + str(idx) + ")" + name[dot:]
            else:
                new_name = name[:dot-4] + " (" + str(idx) + ")" + name[dot:]
            return self.checkDuplicate(idx+1, new_name, path)
        else:
            return name

    def post(self, request, format=None):
        uploadedList = []
        
        for idx, file in enumerate(request.FILES.getlist('file')):
            uploadedFile = {}
            file_path = request.data.getlist('path')[idx]
            file.name = self.checkDuplicate(1, file.name, file_path)
            uploadedFile['name'] = file.name
            uploadedFile['path'] = file_path
            uploadedFile['isFile'] = request.data.getlist('isFile')[idx]
            uploadedFile['author'] = request.data.getlist('author')[idx]
            uploadedFile['fileSize'] = request.data.getlist('fileSize')[idx]
            uploadedFile['createdDate'] = request.data.getlist('createdDate')[idx]

            serializer = FileSerializer(data=uploadedFile)
            if serializer.is_valid():
                serializer.save()

                session = boto3.session.Session(aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY, region_name = AWS_REGION)
                s3 = session.resource('s3')
                s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(Key = str(File.objects.get(name=file.name).pk), Body = file)

                uploadedList.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(uploadedList, status=status.HTTP_201_CREATED)


class FolderUpload(APIView):
    def post(self, request, format=None):
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class FileDownload(APIView):
    def get(self, request, format=None):
        try:
            request_fid = request.GET.get('fid', None)
            target = File.objects.get(pk=request_fid)
            download_url = "https://throwbox.s3.ap-northeast-2.amazonaws.com/" + request_fid
            res = { 
                'download_url': download_url,
                'file_name': target.name
            }
            return Response(res, status=status.HTTP_200_OK)
        except File.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

