from django.urls import path
from api import views

urlpatterns = [
    path('fileList/', views.FileList.as_view()),
    path('fileUpload/', views.FileUpload.as_view()),
    path('folderUpload/', views.FolderUpload.as_view()),
    path('fileDownload/', views.FileDownload.as_view()),
    path('fileTrash/',views.fileTrash.as_view()),
]
