from django.urls import path
from api import views

urlpatterns = [
    path('fileList', views.file_list),
    path('file/<int:pk>', views.file_detail),
    path('upload', views.file_upload),
    path('download', views.file_download),
]
