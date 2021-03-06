from django.urls import path
from api import views

urlpatterns = [
    path('signUp/', views.SignUp.as_view()),
    path('signUpConfirm/', views.SignUpConfirm.as_view()),

    path('signIn/', views.SignIn.as_view()),
    path('userDetail/', views.UserDetail.as_view()),
    path('userModify/', views.UserModify.as_view()),
    path('userDelete/', views.UserDelete.as_view()),

    path('fileList/', views.FileList.as_view()),
    path('fileUpload/', views.FileUpload.as_view()),
    path('folderUpload/', views.FolderUpload.as_view()),
    path('fileDownload/', views.FileDownload.as_view()),
    path('fileStarred/', views.FileStarred.as_view()),
    path('fileRename/', views.FileRename.as_view()),
    path('fileMove/', views.FileMove.as_view()),
    path('fileRecent/', views.FileRecent.as_view()),

    path('fileErase/', views.FileErase.as_view()),
    path('fileTrash/',views.FileTrash.as_view()),
    path('fileTrashList/',views.FileTrashList.as_view()),
    path('fileRecovery/', views.FileRecovery.as_view())
]
