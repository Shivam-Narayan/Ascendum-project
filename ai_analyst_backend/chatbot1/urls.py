# urls.py in your Django app
from django.urls import path
from . import views, views1

urlpatterns = [
    # path('api/upload_document/', views.upload_document, name='upload_document'),
    # path('api/query_document/', views.query_document, name='query_document'),
    path('api/upload_document/', views1.upload_document, name='upload_document'),
    path('api/query_document/', views1.query_document, name='query_document'),
    path('api/uploaded_documents/', views1.list_documents, name='list_documents')
]
