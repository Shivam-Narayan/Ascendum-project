# urls.py

from django.urls import path
from .views import register_user, login_user, upload_pdf, ask_pdf_question, get_chat_history, upload_excel_csv, ask_data_question

urlpatterns = [
    path('register', register_user, name='register'),
    path('login', login_user, name='login'),
    path('upload-pdf/', upload_pdf, name='upload_pdf'),
    path('ask/<str:pdf_id>/', ask_pdf_question, name='ask_pdf_question'),
    path('history/<str:pdf_id>/', get_chat_history, name='get_chat_history'),

    path('upload-csv/', upload_excel_csv, name='upload_excel_csv'),
    path('ask-data/<str:dataset_id>/', ask_data_question, name='ask')
]
