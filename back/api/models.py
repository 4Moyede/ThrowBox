from django.db import models


class File(models.Model):
    isFile = models.BooleanField()
    user = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    path = models.TextField()
    s3Link = models.TextField()
    deletedDate = models.DateField(default=None, null=True)
