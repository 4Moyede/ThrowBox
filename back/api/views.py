import boto3
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

from datetime import datetime
from bson import ObjectId

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
            uploadedFile['createdDate'] = '2000-01-01 00:00'
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
        download_url = "https://throwbox.s3.ap-northeast-2.amazonaws.com/" + request.GET.get('fid', None)
        res = { 'download_url': download_url }
        return Response(res)
        
        
class FileErase(APIView) :
    def delete() :
        quaryset = File.objects.filter(deletedDate < datetime.now() - 30)    # 날짜체크 수정해야함

        s3 = boto3.client('s3', aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY,)
        s3.delete_object(Bucket = AWS_STORAGE_BUCKET_NAME, Key = file_key)  # s3에서 삭제, 여러파일 동시에 삭제하도록 수정해야함

        quaryset.delete()   # DB에서 삭제, deletedDate부터 30일 지난 날짜 체크
        

class FileStarred(APIView) :
    def get(self, request, format = None):
        starred = request.GET.get('starred', None)
        queryset = File.objects.filter(starred = True)
        serializer = FileSerializer(queryset, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
    def post(self, request, format = None) :
        queryset = File.objects.filter(fid = ObjectId(request.data['fid']))
        res = queryset.update(starred = request.data['starred'])
        if res > 0 :
            return Response(status = status.HTTP_200_OK)
        return Response(status = status.HTTP_400_BAD_REQUEST)
    
class fileTrash(APIView):
    #즐겨찾기 삭제 추가할 것.
    def post(self,request,format=None):#리퀘 데이터에 삭제 시간,id
        print(type(request.data))
        print(request.data['file_id'],request.data['deletedDate'])
        File.objects.filter(fid= ObjectId(request.data['file_id'])).update(deletedDate=request.data['deletedDate'])
        return Response(status=status.HTTP_200_OK)
