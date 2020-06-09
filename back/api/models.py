from djongo import models
from django.utils import timezone


class File(models.Model):
    isFile = models.BooleanField()
    fid = models.ObjectIdField(db_column='_id', primary_key=True)
    author = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    path = models.TextField()
    fileSize = models.IntegerField()
    starred = models.BooleanField(default = False)
    deletedDate = models.DateTimeField(blank = True, null = True)
