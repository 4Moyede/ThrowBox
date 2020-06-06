import boto3
from django.http import HttpResponse
from django.core import serializers

from api.models import File
from api.serializers import FileSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

import boto3
from boto3.session import Session
from src.settings import AWS_REGION
from src.settings import S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, S3_STORAGE_BUCKET_NAME, S3_ACCESS_URL
from src.settings import COGNITO_ACCESS_KEY_ID, COGNITO_SECRET_ACCESS_KEY, COGNITO_APP_CLIENT_ID

from datetime import datetime
from bson import ObjectId


class SignUp(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            res = cognito.sign_up(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=request.data['username'],
                Password=request.data['password'],
                UserAttributes=[{'Name': 'email', 'Value': request.data['email']}]
            )
            return Response(status=status.HTTP_201_CREATED)
        except cognito.exceptions.InvalidPasswordException as e:
            return Response({ 'error' : str(e) }, status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.UsernameExistsException as e:
            return Response({ 'error' : str(e) }, status=status.HTTP_409_CONFLICT)


class SignUpConfirm(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            res = cognito.confirm_sign_up(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=request.data['username'],
                ConfirmationCode=request.data['confirmationCode'],
            )
            return Response(status=status.HTTP_200_OK)
        except cognito.exceptions.ExpiredCodeException as e:
            cognito.resend_confirmation_code(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=request.data['username']
            )
            return Response({ 'error' : str(e) }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.CodeMismatchException as e:
            return Response({ 'error' : str(e) }, status=status.HTTP_400_BAD_REQUEST)


class SignIn(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            response = cognito.initiate_auth(
                ClientId=COGNITO_APP_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={ 'USERNAME': request.data['username'], 'PASSWORD': request.data['password'] },
            )
            header = { 'AccessToken' : response['AuthenticationResult']['AccessToken'] }
            return Response(header, status=status.HTTP_200_OK)
        except cognito.exceptions.NotAuthorizedException as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class FileList(APIView):
    def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            user = cognito.get_user(AccessToken=request.headers['authorization'])
            path = request.GET.get('path', None)
            queryset = File.objects.filter(path=path, deletedDate=None)
            serializer = FileSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (KeyError, cognito.exceptions.NotAuthorizedException):
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class FileUpload(APIView):
    def checkDuplicate(self, name, path):
        idx = 1
        dot = name.rfind('.')
        file_name = name[:dot]
        file_ext = name[dot:]

        queryset = File.objects.filter(name=name, path=path)
        while queryset.values_list(): 
            name = file_name + " (" + str(idx) + ")" + file_ext
            idx += 1
            queryset = File.objects.filter(name=name, path=path)
        
        return name

    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            user = cognito.get_user(AccessToken=request.headers['authorization'])
            uploadedList = []
            
            for idx, file in enumerate(request.FILES.getlist('file')):
                uploadedFile = {}
                file_path = str(request.data.getlist('path')[idx])
                file.name = self.checkDuplicate(file.name, file_path)
                uploadedFile['name'] = file.name
                uploadedFile['path'] = file_path
                uploadedFile['isFile'] = request.data.getlist('isFile')[idx]
                uploadedFile['author'] = request.data.getlist('author')[idx]
                uploadedFile['fileSize'] = request.data.getlist('fileSize')[idx]

                serializer = FileSerializer(data=uploadedFile)
                if serializer.is_valid():
                    serializer.save()
                    
                    session = boto3.session.Session(aws_access_key_id = S3_ACCESS_KEY_ID, aws_secret_access_key = S3_SECRET_ACCESS_KEY, region_name = AWS_REGION)
                    s3 = session.resource('s3')
                    s3.Bucket(S3_STORAGE_BUCKET_NAME).put_object(Key = str(File.objects.get(name=file.name).pk), Body = file)

                    uploadedList.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(uploadedList, status=status.HTTP_201_CREATED)
        except (KeyError, cognito.exceptions.NotAuthorizedException):
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class FolderUpload(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            user = cognito.get_user(AccessToken=request.headers['authorization'])
            serializer = FileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, cognito.exceptions.NotAuthorizedException):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        

class FileDownload(APIView):
    def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            user = cognito.get_user(AccessToken=request.headers['authorization'])
            request_fid = request.GET.get('fid', None)
            target = File.objects.get(pk=request_fid)
            download_url = S3_ACCESS_URL + request_fid
            res = { 
                'download_url': download_url,
                'file_name': target.name
            }
            return Response(res, status=status.HTTP_200_OK)
        except File.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, cognito.exceptions.NotAuthorizedException):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        
class FileErase(APIView):
    def delete(self, request, format=None):
        # quaryset = File.objects.filter(deletedDate < datetime.now() - 30)    # 날짜체크 수정해야함

        s3 = boto3.client('s3', aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY,)
        # s3.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=file_key)  # s3에서 삭제, 여러파일 동시에 삭제하도록 수정해야함

        # quaryset.delete()   # DB에서 삭제, deletedDate부터 30일 지난 날짜 체크
        

class FileStarred(APIView) :
    def get(self, request, format=None):
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
