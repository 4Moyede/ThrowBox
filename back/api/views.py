import boto3
from django.http import HttpResponse
from django.core import serializers
import django.core.exceptions

from django.db.models import Sum
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

from datetime import datetime, timedelta
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
        except KeyError:
            return Response({ 'error': 'No Required Parameter' }, status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.InvalidPasswordException:
            return Response({ 'error' : "Invaild Password" }, status=status.HTTP_403_FORBIDDEN)
        except cognito.exceptions.UsernameExistsException:
            return Response({ 'error' : "Username Already Exist" }, status=status.HTTP_409_CONFLICT)


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
        except KeyError:
            return Response({ 'error': 'No Required Parameter' }, status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.ExpiredCodeException:
            cognito.resend_confirmation_code(
                ClientId=COGNITO_APP_CLIENT_ID,
                Username=request.data['username']
            )
            return Response({ 'error' : 'Code is Expired. Please check the new Code' }, status=status.HTTP_408_REQUEST_TIMEOUT)
        except cognito.exceptions.CodeMismatchException:
            return Response({ 'error' : 'Code Mismatch' }, status=status.HTTP_409_CONFLICT)
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
        except KeyError:
            return Response({ 'error': 'No Required Parameter' }, status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.InvalidPasswordException:
            return Response({ 'error' : "Invaild Password" }, status=status.HTTP_403_FORBIDDEN)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)


class UserDetail(APIView):
    def get(self, request, format=None):
        try:
            session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
            cognito = session.client("cognito-idp")

            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            userDetail = {
                'ID' : user['Username'],
                'Email' : next((user_attribute for user_attribute in user['UserAttributes'] if user_attribute['Name'] == 'email'), False)['Value'],
                'ProfileImage' : ''
            }
            return Response(userDetail, status=status.HTTP_200_OK)
        except KeyError:
            return Response({ 'error': 'No Required Parameter' }, status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.NotAuthorizedException:
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)


class UserModify(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        
        try:
            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
            if request.data['attribute'] == 'password':
                cognito.change_password(
                    PreviousPassword=request.data['preValue'],
                    ProposedPassword=request.data['postValue'],
                    AccessToken=request.headers['AccessToken']
                )
                return Response(status=status.HTTP_200_OK)
        except KeyError:
            return Response({ 'error': 'No Required Parameter' }, status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.NotAuthorizedException:
            return Response({ 'error' : 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)
        

class UserDelete(APIView):
    def delete(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
            cognito.delete_user(AccessToken=request.headers['AccessToken'])
            return Response(status=status.HTTP_200_OK)
        except cognito.exceptions.NotAuthorizedException:
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)


class FileList(APIView):
    def totalFileSize(self, author):
        queryset = File.objects.filter(author=author).aggregate(totalSize=Sum('fileSize'))
        return queryset['totalSize'] if queryset['totalSize'] else 0

    def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
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
            res = { 
                'totalSize': self.totalFileSize(user['Username']),
                'fileList': serializer.data
            }
            return Response(res, status=status.HTTP_200_OK)
        except cognito.exceptions.NotAuthorizedException:
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)


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
            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
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
                    raise KeyError
            return Response(uploadedList, status=status.HTTP_201_CREATED)
        except KeyError:
            return Response({ 'error': 'No Required Parameter' }, status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.NotAuthorizedException:
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)


class FolderUpload(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
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
            else:
                raise KeyError
        except KeyError:
            return Response({ 'error': 'No Required Parameter' }, status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.NotAuthorizedException:
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)
        

class FileDownload(APIView):
    def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
            cognito.get_user(AccessToken=request.headers['AccessToken'])
            request_fid = request.GET.get('fid', None)
            target = File.objects.get(pk=request_fid)
            download_url = S3_ACCESS_URL + request_fid
            res = { 
                'downloadUrl': download_url,
                'fileName': target.name
            }
            return Response(res, status=status.HTTP_200_OK)
        except (KeyError, File.DoesNotExist):
            return Response({ 'error': 'File Does not Exist' }, status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.NotAuthorizedException:
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        
class FileErase(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
            cognito.get_user(AccessToken=request.headers['AccessToken'])
            checkdate = datetime.now() + timedelta(days = -30)
            quaryset = File.objects.filter(deletedDate__lt = checkdate)
            
            s3 = boto3.client('s3')
            for delfile in quaryset :
                s3.delete_object(Bucket = S3_STORAGE_BUCKET_NAME, Key=str(delfile.fid))
        
            quaryset.delete()
            return Response(status = status.HTTP_200_OK)
        except cognito.exceptions.NotAuthorizedException:
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)
        

class FileStarred(APIView) :
    def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            starred = request.GET.get('starred', None)
            if not starred:
                    user = cognito.admin_get_user(
                        UserPoolId=COGNITO_USER_POOL_ID,
                        Username=user['Username']
                    )
                    starred = next((user_attribute for user_attribute in user['UserAttributes'] if user_attribute['Name'] == 'custom:baseDirID'), False)['Value']
            queryset = File.objects.filter(starred=starred)
            serializer = FileSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except cognito.exceptions.NotAuthorizedException:
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)
   
    def post(self, request, format = None) :
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            request_fid = request.data['fid']
            if not request_fid:
                user = cognito.admin_get_user(
                    UserPoolId=COGNITO_USER_POOL_ID,
                    Username=user['Username']
                )
                request_fid = next((user_attribute for user_attribute in user['UserAttributes'] if user_attribute['Name'] == 'custom:baseDirID'), False)['Value']
            queryset = File.objects.filter(fid = request_fid)
            queryset.update(starred = request.data['starred'])
            return Response(status = status.HTTP_200_OK)
        except cognito.exceptions.NotAuthorizedException:
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)


class fileTrash(APIView):
    def post(self,request,format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            File.objects.filter(fid= ObjectId(request.data['fid'])).update(deletedDate=datetime.now(), starred=False)
            return Response(status=status.HTTP_200_OK)
        except django.core.exceptions.ObjectDoesNotExist:
            return Response({'error: "Invalid Fid"'},status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.NotAuthorizedException:
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)


class fileRecovery(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
            File.objects.filter(fid= ObjectId(request.data['fid'])).update(deletedDate=None)
            return Response(status=status.HTTP_200_OK)
        except django.core.exceptions.ObjectDoesNotExist:
            return Response({'error: "Invalid Fid"'},status=status.HTTP_400_BAD_REQUEST)
        except cognito.exceptions.NotAuthorizedException:
            return Response({ 'error': 'Not Authorized' }, status=status.HTTP_401_UNAUTHORIZED)
        except cognito.exceptions.UserNotFoundException:
            return Response({ 'error': 'User Not Found' }, status=status.HTTP_404_NOT_FOUND)
        except cognito.exceptions.UserNotConfirmedException:
            return Response({ 'error': 'User Not Confirmed' }, status=status.HTTP_406_NOT_ACCEPTABLE)
