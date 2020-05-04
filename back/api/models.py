from django.db import models


class File(models.Model):
    _id=models.TextField()#파이썬 예약어를 사용할 수 없으므로 _id로 지정
    isFile=models.BooleanField()
    name=models.CharField(max_length=256)#파일 이름은 256자로 제한
    path=models.TextField()
    s3Link=models.TextField()
    createdDate=models.DateTimeField()
    deletedDate=models.DateField(defalut=None)
    userFavList=models.TextField()#models에는 list가 따로 없음.
    author=models.TextField()
