from django.urls import path
from api import views

urlpatterns = [
    path('fileList/', views.FileList.as_view()),
    path('fileUpload/', views.FileUpload.as_view()),
    path('fileDownload/<int:pk>/', views.FileDownload.as_view())
]
