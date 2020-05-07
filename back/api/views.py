import json

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.http import Http404

from api.models import File
from api.serializers import FileSerializer, UserSerializer

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class FileList(generics.ListCreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class FileUpload(APIView):
    def post(self, request, format=None):
        serializer = FileSerializer(data=request.data)
        for file in request.FILES.getlist('file'):
            print(file)

        if serializer.is_valid():
            serializer.save(owner=self.request.user)
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
        response_data['s3Link'] = serializer.data.get('s3Link')
        return HttpResponse(json.dumps(response_data), content_type="application/json")


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# import boto3

# class FileToURL(View):
#     s3_client = boto3.client(
#             's3',
#             aws_access_key_id={aws_access_key_id},
#             aws_secret_access_key={aws_secret_access_key}
#         )
#     def post(self, request):

#         for file in request.FILES.getlist('file'): 
#             self.s3_client.upload_fileobj(
#                 file,
#                 {bucket-name},
#                 file.name,
#                 ExtraArgs={
#                     "ContentType": file.content_type
#                 }
#             )
            
#         file_urls = [f"https://s3.ap-northeast-2.amazonaws.com/{bucket-name}/{file.name}" for file in request.FILES.getlist('file')]

#         return JsonResponse({'files':file_urls}, status=200)