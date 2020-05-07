from django.db import models


class File(models.Model):
    isFile = models.BooleanField()
    name = models.CharField(max_length=256)
    path = models.TextField()
    s3Link = models.TextField()
    deletedDate = models.DateField(default=None, null=True)
    owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)
