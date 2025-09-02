from django.urls import path
from .views import generate_thumbnails, enhance_thumbnails, download_thumbnail
from .views1 import generate_thumbnails2, enhance_thumbnail2

urlpatterns = [
    path('generate/', generate_thumbnails, name='generate_thumbnails'),
    path('enhance/', enhance_thumbnails, name='enhance_thumbnails'),
    path('download/', download_thumbnail, name='download_thumbnail'),
    path('generat2/', generate_thumbnails2, name='generate_thumbnails2'),
    path('enhance2/', enhance_thumbnail2, name='enhance_thumbnail2'),
]