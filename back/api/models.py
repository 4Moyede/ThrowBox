from djongo import models


class File(models.Model):
    isFile = models.BooleanField()
    fid = models.ObjectIdField(db_column='_id', primary_key=True)
    author = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    path = models.TextField()
    fileSize = models.IntegerField()
    createdDate = models.CharField(max_length=20)
    deletedDate = models.CharField(max_length=20, null=True)
    fav=models.BooleanField(default=False)