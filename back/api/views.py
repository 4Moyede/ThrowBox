import boto3
from django.http import HttpResponse
from django.core import serializers
from django.core.exceptions import ValidationError, FieldDoesNotExist, ObjectDoesNotExist

from django.db.models import Sum
from api.models import File
from api.serializers import FileSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

import boto3
from boto3.session import Session
from botocore.exceptions import ClientError, NoCredentialsError
from src.settings import AWS_REGION
from src.settings import S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, S3_STORAGE_BUCKET_NAME, S3_ACCESS_URL
from src.settings import COGNITO_ACCESS_KEY_ID, COGNITO_SECRET_ACCESS_KEY, COGNITO_APP_CLIENT_ID, COGNITO_USER_POOL_ID

from datetime import datetime, timedelta
from bson import ObjectId

def auth_error_response():
    return { 'Error': { 'Message': 'Could not verify signature for Access Token', 'Code': 'NotAuthorizedException' }, 'ResponseMetadata': { 'HTTPHeaders': {'date': datetime.now() }, 'HTTPStatusCode': status.HTTP_401_UNAUTHORIZED } }
    

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
        except KeyError as error:
            return Response({ 
                'error': 'No parameter:' + str(error),
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])


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
        if serializer.is_valid(raise_exception=True):
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
        except KeyError as error:
            return Response({ 
                'error': 'No parameter:' + str(error),
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            return Response({ 
                'error': 'MongoDataBaseError',
                'date' : datetime.now()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])


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
        except KeyError as error:
            return Response({ 
                'error': 'No parameter:' + str(error),
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])


class UserDetail(APIView):
    def get(self, request, format=None):
        try:
            session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
            cognito = session.client("cognito-idp")

            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "UserDetail")
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            userDetail = {
                'ID' : user['Username'],
                'Email' : next((user_attribute for user_attribute in user['UserAttributes'] if user_attribute['Name'] == 'email'), False)['Value'],
                'ProfileImage' : ''
            }
            return Response(userDetail, status=status.HTTP_200_OK)
        except KeyError as error:
            return Response({ 
                'error': 'No parameter:' + str(error),
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])


class UserModify(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        
        try:
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "UserModify")
            if request.data['attribute'] == 'password':
                cognito.change_password(
                    PreviousPassword=request.data['preValue'],
                    ProposedPassword=request.data['postValue'],
                    AccessToken=request.headers['AccessToken']
                )
                return Response(status=status.HTTP_200_OK)
        except KeyError as error:
            return Response({ 
                'error': 'No parameter:' + str(error),
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])     
        

class UserDelete(APIView):
    def delete(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "UserDelete")
            cognito.delete_user(AccessToken=request.headers['AccessToken'])
            return Response(status=status.HTTP_200_OK)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])


class FileList(APIView):
    def totalFileSize(self, author):
        queryset = File.objects.filter(author=author).aggregate(totalSize=Sum('fileSize'))
        return queryset['totalSize'] if queryset['totalSize'] else 0

    def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "FileList")
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
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])
        

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
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "FileUpload")
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
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    
                    session = boto3.session.Session(aws_access_key_id = S3_ACCESS_KEY_ID, aws_secret_access_key = S3_SECRET_ACCESS_KEY, region_name = AWS_REGION)
                    s3 = session.resource('s3')
                    s3.Bucket(S3_STORAGE_BUCKET_NAME).put_object(Key = str(File.objects.get(name=file.name).pk), Body = file)

                    uploadedList.append(serializer.data)
            return Response(uploadedList, status=status.HTTP_201_CREATED)
        except ValidationError:
            return Response({ 
                'error': 'NoRequiredParameter',
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])


class FolderUpload(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "FolderUpload")
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
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError:
            return Response({ 
                'error': 'NoRequiredParameter',
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])
        

class FileDownload(APIView):
    def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "FileDownload")
            cognito.get_user(AccessToken=request.headers['AccessToken'])
            request_fid = request.GET.get('fid', None)
            if not request_fid:
                raise FieldDoesNotExist
            target = File.objects.get(pk=request_fid)
            download_url = S3_ACCESS_URL + request_fid
            res = { 
                'downloadUrl': download_url,
                'fileName': target.name
            }
            return Response(res, status=status.HTTP_200_OK)
        except FieldDoesNotExist as error:
            return Response({ 
                'error': "FieldDoexNotExist",
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist as error:
            return Response({ 
                'error': str(error),    
                'date' : datetime.now()
            }, status=status.HTTP_404_NOT_FOUND)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])
        

class FileStarred(APIView) :
    def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "FileStarred")
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
        except KeyError as error:
            return Response({ 
                'error': 'No parameter:' + str(error),
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])
   
    def post(self, request, format = None) :
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "FileStarred")
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
        except KeyError as error:
            return Response({ 
                'error': 'No parameter:' + str(error),
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])


class FileRename(APIView):
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

    def put(self, request, format=None): 
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "fileRename")
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            File.objects.filter(fid= ObjectId(request.data['fid'])).update(name=self.checkDuplicate(request.data['name'], request.data['path']))
            if request.data['name']== "" or request.data['name'].strip() =="":
                return Response({ 'error': 'File name must exist' },status = status.HTTP_400_BAD_REQUEST)
            else :
                return Response(status=status.HTTP_200_OK)
        except KeyError as error:
            return Response({ 
                'error': 'No parameter:' + str(error),
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])


class FileMove(APIView):
    def put(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try: 
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "fileMove")
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            File.objects.filter(fid=ObjectId(request.data['file_id'])).update(path=request.data['path'])
            return Response(status=status.HTTP_200_OK)
        except KeyError as error:
            return Response({ 
                'error': 'No parameter:' + str(error),
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])


class FileRecent(APIView):
    def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "fileRecent")
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            queryset = File.objects.filter(author=user['Username']).order_by('-id')
            serializer = FileSerializer(queryset, many=True)
            res = {
                'fileList': serializer.data
            }
            return Response(res, status=status.HTTP_200_OK)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])

        
class FileErase(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "FileErase")
            cognito.get_user(AccessToken=request.headers['AccessToken'])
            checkdate = datetime.now() + timedelta(days = -30)
            queryset = File.objects.filter(deletedDate__lt = checkdate)
            
            session = boto3.session.Session(aws_access_key_id = S3_ACCESS_KEY_ID, aws_secret_access_key = S3_SECRET_ACCESS_KEY, region_name = AWS_REGION)
            s3 = session.client('s3')
            for delfile in queryset:
                s3.delete_object(Bucket = S3_STORAGE_BUCKET_NAME, Key=str(delfile.fid))

            queryset.delete()
            return Response(status = status.HTTP_200_OK)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])


class FileTrash(APIView):
    def post(self,request,format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "fileTrash")
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
            File.objects.filter(fid= ObjectId(request.data['fid'])).update(deletedDate=datetime.now(), starred=False)
            return Response(status=status.HTTP_200_OK)
        except KeyError as error:
            return Response({ 
                'error': 'No parameter:' + str(error),
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])


class FileTrashList(APIView):
     def get(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not request.headers['AccessToken']:
                raise cognito.exceptions.NotAuthorizedException
            user = cognito.get_user(AccessToken=request.headers['AccessToken'])
                   
            queryset = File.objects.filter(author=user['Username'] , deletedDate__isnull=False)
            serializer = FileSerializer(queryset, many=True)
            res = { 
                'fileList': serializer.data
            }
            return Response(res, status=status.HTTP_200_OK)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])


class FileRecovery(APIView):
    def post(self, request, format=None):
        session = boto3.session.Session(aws_access_key_id=COGNITO_ACCESS_KEY_ID, aws_secret_access_key=COGNITO_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        cognito = session.client("cognito-idp")
        try:
            if not 'AccessToken' in request.headers.keys():
                raise cognito.exceptions.NotAuthorizedException(auth_error_response(), "fileRecovery")
            File.objects.filter(fid= ObjectId(request.data['fid'])).update(deletedDate=None)
            return Response(status=status.HTTP_200_OK)
        except KeyError as error:
            return Response({ 
                'error': 'No parameter:' + str(error),
                'date' : datetime.now()
            }, status=status.HTTP_400_BAD_REQUEST)
        except ClientError as error:
            return Response({ 
                'error': error.response['Error']['Code'],
                'date' : error.response['ResponseMetadata']['HTTPHeaders']['date']
            }, status=error.response['ResponseMetadata']['HTTPStatusCode'])
        
