from django.db import models


class File(models.Model):
    fid = models.TextField()
    author = models.TextField()
    isFile = models.BooleanField()
    name = models.CharField(max_length=256)
    path = models.TextField()
    s3Link = models.TextField()
    createdDate = models.DateTimeField(auto_now_add=True)
    deletedDate = models.DateField(default=None)


"""
Item={
          'id': str(name)+str(createdDate),
          'name': name,
          'info': {
              'isFile':isFile,
              'path':path,
              'createdDate':str(createdDate),
              'deletedDate':None,
              'auth':auth,
              's3Link':s3Link
          }
      }
"""