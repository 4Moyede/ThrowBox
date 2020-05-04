from rest_framework import serializers
from back.api.models import File
from back.db.testPy import insertToFile
import time

class FileSerializer(serializers.Serializer):
    _id=serializers.TextField()#파이썬 예약어를 사용할 수 없으므로 _id로 지정
    isFile=serializers.BooleanField()
    name=serializers.CharField(required=True,max_length=256)#파일 이름은 256자로 제한
    path=serializers.TextField(required=True)
    s3Link=serializers.TextField()
    createdDate=serializers.DateTimeField()
    deletedDate=serializers.DateField(defalut=None)
    userFavList=serializers.TextField()
    author=serializers.TextField() 
    
    
    def upload(self):
      """
      db에 받아온 값들을 저장합니다.
      id는 insertToFile에서 name과 createdDate를 이용해 자동으로 생성합니다.

      """
      response=insertToFile(self.isFile,self.name,self.path,self.createdDate,self.author)
      return response
