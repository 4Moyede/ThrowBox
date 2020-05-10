from django.db import models


class File(models.Model):
    isFile = models.BooleanField()
    author = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    path = models.TextField()
    s3Link = models.TextField(null=True)
    fileSize = models.IntegerField()
    createdDate = models.TextField()
    deletedDate = models.DateField(default=None, null=True)
