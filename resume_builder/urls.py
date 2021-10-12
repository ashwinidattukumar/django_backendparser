from django.urls import path
from . import views
from .views import  fileupload

urlpatterns = [
    path('extract',views.resume_extract),
    path('file',fileupload.as_view(),name='fileupload')
]