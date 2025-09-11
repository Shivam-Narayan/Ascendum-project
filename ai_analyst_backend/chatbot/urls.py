# urls.py

from django.urls import path
from .views import register_user, login_user, upload_pdf, ask_pdf_question,  upload_excel_csv, ask_data_question, get_all_chat_histories_for_user, get_profile, change_password, chat_with_bot, upload_multiple_documents, ask_combined_documents, download_user_file
# from .views1 import upload_pdf1, ask_pdf_question1, upload_excel_csv1, ask_data_question1, get_all_histories_for_user1
urlpatterns = [
    path('register', register_user, name='register'),
    path('login', login_user, name='login'),
    path('upload-pdf/', upload_pdf, name='upload_pdf'),
    path('ask/<str:pdf_id>/', ask_pdf_question, name='ask_pdf_question'),
    # path('history/<str:pdf_id>/', get_chat_history, name='get_chat_history'),

    path('upload-csv/', upload_excel_csv, name='upload_excel_csv'),
    path('ask-data/<str:dataset_id>/', ask_data_question, name='ask'),
    path('histories/', get_all_chat_histories_for_user, name='get_all_chat_histories_for_user'),

    path('profile/', get_profile, name='get_profile'),
    path('changePassword/', change_password, name='change_password'),
    path('chat/', chat_with_bot, name='chat_with_bot'),

    path('multiple/', upload_multiple_documents, name='upload_document'),
    path('askm/<str:documents_id>/', ask_combined_documents, name='ask_document_question'),
    path('files/download/<str:file_id>/', download_user_file, name='download_user_file'),


     # New endpoints with '1' suffix

    # path('upload-pdf1/', upload_pdf1, name='upload_pdf1'),
    # path('ask1/<str:pdf_id>/', ask_pdf_question1, name='ask_pdf_question1'),
    # path('upload-csv1/', upload_excel_csv1, name='upload_excel_csv1'),
    # path('ask-data1/<str:dataset_id>/', ask_data_question1, name='ask1'),
    # path('histories1/', get_all_histories_for_user1, name='get_all_histories_for_user1'),
]