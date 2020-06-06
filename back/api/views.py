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
from src.settings import COGNITO_ACCESS_KEY_ID, COGNITO_SECRET_ACCESS_KEY, COGNITO_APP_CLIENT_ID, COGNITO_USER_POOL_ID

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
        except cognito.exceptions.InvalidPasswordException:
            return Response({ 'error' : "Invaild Password" }, status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.UsernameExistsException:
            return Response({ 'error' : "Username Already Exist" }, status=status.HTTP_400_BAD_REQUEST)


class SignUpConfirm(APIView):
    def mkdirRoot(self, username):
        root = {
            'isFile' : False,
            'author' : username,
            'name' : username+"_root",
            'path' : "This is a root directory",
            'fileSize' : 0,
            'starred' : False
        }
        serializer = FileSerializer(data=root)
        if serializer.is_valid():
            serializer.save()

            session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
            cognito = session.client("cognito-idp")
    
            cognito.admin_update_user_attributes(
                UserPoolId=COGNITO_USER_POOL_ID,
                Username=username,
                UserAttributes=[
                    {
                        'Name': 'custom:baseDirID', 
                        'Value': serializer.data['fid']
                    }
                ]
            )
        else:
            raise ValueError

    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            self.mkdirRoot(request.data['username'])
            res = cognito.confirm_sign_up(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=request.data['username'],
                ConfirmationCode=request.data['confirmationCode'],
            )
            return Response(status=status.HTTP_200_OK)
        except cognito.exceptions.ExpiredCodeException:
            cognito.resend_confirmation_code(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=request.data['username']
            )
            return Response({ 'error' : 'Code is Expired. Please check the new Code' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.CodeMismatchException:
            return Response({ 'error' : 'Code Mismatch' }, status=status.HTTP_406_NOT_ACCEPTABLE)
        except ValueError:
            return Response({ 'error' : 'Mongo DB Error' }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            return Response(response['AuthenticationResult'], status=status.HTTP_200_OK)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.InvalidPasswordException:
            return Response({ 'error' : "Invaild Password" }, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    def get(self, request, format=None):
        try:
            session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
            cognito = session.client("cognito-idp")
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            userDetail = {
                'ID' : user['Username'],
                'email' : next((user_attribute for user_attribute in user['UserAttributes'] if user_attribute['Name'] == 'email'), False)['Value'],
                'ProfileImage' : ''
            }
            return Response(userDetail, status=status.HTTP_200_OK)
        except (KeyError, cognito.exceptions.NotAuthorizedException):
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_400_BAD_REQUEST)


class UserModify(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        
        try:
            if request.data['attribute'] == 'password':
                cognito.change_password(
                    PreviousPassword=request.data['prePassword'],
                    ProposedPassword=request.data['proPassword'],
                    AccessToken=request.headers['AccessToken']
                )
                return Response(status=status.HTTP_200_OK)
        except (KeyError, cognito.exceptions.NotAuthorizedException):
            return Response({ 'error' : 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_400_BAD_REQUEST)


class UserDelete(APIView):
    def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            cognito.delete_user(AccessToken=request.headers['AccessToken'])
            return Response(status=status.HTTP_200_OK)
        except (KeyError, cognito.exceptions.NotAuthorizedException):
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_400_BAD_REQUEST)


class FileList(APIView):
    def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            path = request.GET.get('path', None)
            if not path:
                user = cognito.admin_get_user(
                    UserPoolId=COGNITO_USER_POOL_ID,
                    Username=user['Username']
                )
                path = next((user_attribute for user_attribute in user['UserAttributes'] if user_attribute['Name'] == 'custom:baseDirID'), False)['Value']
            queryset = File.objects.filter(path=path, deletedDate=None)
            serializer = FileSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (KeyError, cognito.exceptions.NotAuthorizedException):
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_400_BAD_REQUEST)


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
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            uploadedList = []
            
            for idx, file in enumerate(request.FILES.getlist('file')):
                uploadedFile = {}
                file_path = str(request.data.getlist('path')[idx])
                if not file_path:
                    user = cognito.admin_get_user(
                        UserPoolId=COGNITO_USER_POOL_ID,
                        Username=user['Username']
                    )
                    file_path = next((user_attribute for user_attribute in user['UserAttributes'] if user_attribute['Name'] == 'custom:baseDirID'), False)['Value']
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
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)


class FolderUpload(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            dir_path = request.data['path']
            if not dir_path:
                user = cognito.admin_get_user(
                    UserPoolId=COGNITO_USER_POOL_ID,
                    Username=user['Username']
                )
                dir_path = next((user_attribute for user_attribute in user['UserAttributes'] if user_attribute['Name'] == 'custom:baseDirID'), False)['Value']
            new_dir = { }
            new_dir['name'] = request.data['name']
            new_dir['path'] = dir_path
            new_dir['isFile'] = request.data['isFile']
            new_dir['author'] = request.data['author']
            new_dir['fileSize'] = request.data['fileSize']
            serializer = FileSerializer(data=new_dir)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, cognito.exceptions.NotAuthorizedException):
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_400_BAD_REQUEST)
        

class FileDownload(APIView):
    def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            cognito.get_user(AccessToken=request.headers['AccessToken'])
            request_fid = request.GET.get('fid', None)
            target = File.objects.get(pk=request_fid)
            download_url = S3_ACCESS_URL + request_fid
            res = { 
                'download_url': download_url,
                'file_name': target.name
            }
            return Response(res, status=status.HTTP_200_OK)
        except File.DoesNotExist:
            return Response({ 'error': 'File Does not Exist' }, status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, cognito.exceptions.NotAuthorizedException):
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_400_BAD_REQUEST)
        
        
class FileErase(APIView):
    def delete(self, request, format=None):
        # quaryset = File.objects.filter(deletedDate < datetime.now() - 30)    # 날짜체크 수정해야함

        s3 = boto3.client('s3', aws_access_key_id = S3_ACCESS_KEY_ID, aws_secret_access_key = S3_SECRET_ACCESS_KEY,)
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
