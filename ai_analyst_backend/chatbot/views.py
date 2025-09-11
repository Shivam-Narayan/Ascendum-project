import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import User, UploadedFile, DocumentGroup
from .serializers import RegisterSerializer, LoginSerializer, UploadedFileSerializer
from django.contrib.auth.hashers import check_password, make_password
import uuid
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework_simplejwt.tokens import AccessToken
# from .chatbot_curerent_v3 import *
import pandas as pd
import os, json, mimetypes
from django.conf import settings
from datetime import datetime, timedelta
import numpy as np
from pymongo import MongoClient
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from .chatbot_curerent_v3 import (
    AdvancedPDFProcessor,
    AgenticTabularProcessor,
    AdvancedWordProcessor,
    AI_MODELS
)
import uuid
DOCUMENT_GROUPS = {}


import re

DOCUMENT_GROUPS = {}

import streamlit as st
import re
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .MultipleUpload import combine_knowledge_base, _process_knowledge_base_question
DOCUMENT_GROUPS = {}




# Secret key
JWT_SECRET = getattr(settings, 'SECRET_KEY', 'your_jwt_secret')
JWT_EXP_DELTA_SECONDS = 3600

USER_DATA_DIR = os.path.join(settings.BASE_DIR, "user_histories")

def get_user_history_path(email):
    filename = email.replace("@", "_at_") + ".json"
    return os.path.join(USER_DATA_DIR, filename)

def load_user_history(email):
    path = get_user_history_path(email)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"sessions": []}  # Default structure for new users

def save_user_history(email, history_data):
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    path = get_user_history_path(email)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history_data, f, indent=2)

def create_empty_user_history_file(email):
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    path = get_user_history_path(email)
    
    # Create file only if it doesn't exist to avoid overwriting existing history
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"sessions": []}, f, indent=2)

# Register api view

@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Create empty JSON history file for the new user
        create_empty_user_history_file(user.email)

        return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# login api view

@api_view(['POST'])
def login_user(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, user.password):
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        # ✅ generate JWT using simplejwt
        access_token = AccessToken.for_user(user)
        access_token.set_exp(lifetime=timedelta(days=1))  # token expiry

        # Fetch all chat history documents for this user
        user_history_cursor = history_collection.find({"user_id": str(user.id)})

        # user_history = []
        # for doc in user_history_cursor:
        #     # Try to fetch original filename from UploadedFile table
        #     uploaded_file = UploadedFile.objects.filter(file_id=doc.get("file_id")).first()
           
        #     # ✅ Always prefer stored filename from UploadedFile (PDF/Excel/Word/CSV/etc.)
        #     original_filename = (
        #         uploaded_file.filename
        #         if uploaded_file and uploaded_file.filename
        #         else doc.get("filename", "")
        #     )
 
        #     user_history.append({
        #         "type": doc.get("file_type", "chat"),
        #         "id": doc.get("file_id"),
        #         "filename": original_filename,   
        #         "metadata": doc.get("metadata", {}),
        #         "chat_history": doc.get("chat_history", []),
        #     })
        user_history = []
        for doc in user_history_cursor:
            uploaded_file = UploadedFile.objects.filter(file_id=doc.get("file_id")).first()
            if uploaded_file and uploaded_file.filename:
                original_filename = uploaded_file.filename
            else:
                # If top-level filename is missing, try to build from metadata filenames
                metadata_filenames = doc.get("metadata", {}).get("filenames", [])
                if metadata_filenames:
                    # Join multiple filenames by comma for display
                    original_filename = ", ".join(metadata_filenames)
                else:
                    original_filename = doc.get("filename", "")
        
            user_history.append({
                "type": doc.get("file_type", "chat"),
                "id": doc.get("file_id"),
                "filename": original_filename,
                "metadata": doc.get("metadata", {}),
                "chat_history": doc.get("chat_history", []),
        })


        return Response({
            'token': str(access_token),
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
            },
            # 'user_history': user_history.get('sessions', [])  # Include chat/session history here
            'user_history': user_history
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Profile view
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    # Get user's uploaded documents
    user_files = UploadedFile.objects.filter(user=user)
    files_data = UploadedFileSerializer(user_files, many=True).data
    return Response({
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'registered_at': user.created_at,
        'documents': files_data,
    }, status=status.HTTP_200_OK)


# Change Password view
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    data = request.data
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not old_password or not new_password or not confirm_password:
        return Response({'error': 'Please provide old_password, new_password and confirm_password'}, status=status.HTTP_400_BAD_REQUEST)

    if not check_password(old_password, user.password):
        return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_password:
        return Response({'error': 'New password and confirm password do not match'}, status=status.HTTP_400_BAD_REQUEST)

    user.password = make_password(new_password)
    user.save()

    return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)



def save_user_file(file_obj, user_id, file_type, unique_id, extension):
    folder = os.path.join('user_files', f'user_{user_id}', file_type)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{unique_id}.{extension}")
    with open(file_path, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)
    return file_path


# In-memory session store for demo (replace with Redis or DB in production)
PDF_SESSIONS = {}
DATASET_SESSIONS = {}
USER_SESSIONS = {} 

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @parser_classes([MultiPartParser])
# def upload_pdf(request):
#     file_obj = request.FILES.get('file')
#     if not file_obj:
#         return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

#     # Process the PDF
#     from .chatbot_curerent_v3 import extract_comprehensive_pdf_content, AdvancedPDFProcessor, AI_MODELS
#     # from .chatbot_curerent_v3 import extract_comprehensive_pdf_content, AdvancedPDFProcessor, AI_MODELS
#     # from .chatbot_curerent_v3 import extract_comprehensive_pdf_content, AdvancedPDFProcessor, AI_MODELS, AppConfig, initialize_session_state, load_ai_models, enhanced_error_handling, track_performance, validate_input, QueryIntentAgent, SmartSuggestionAgent, VisualizationAgent, PredictiveModelingAgent, SimplifiedPredictiveModelingAgent, AdvancedWordProcessor, AgenticTabularProcessor, load_and_validate_data, smart_data_type_conversion, detect_lookup_query, _parse_statistical_query_with_unlimited_filters, _extract_all_filters_enhanced, _process_statistical_lookup_with_unlimited_filters, _apply_smart_date_filter, _apply_statistical_operation_robust, _process_simple_lookup, _find_best_column_match, _apply_smart_filter, _create_error_response, find_column_match, detect_statistical_query, perform_statistical_analysis, detect_outliers, perform_clustering, perform_data_distribution_analysis, extract_comprehensive_pdf_content, handle_pdf_file_upload, display_pdf_qa_section, _process_pdf_question,  extract_comprehensive_word_content, handle_word_file_upload, display_word_qa_section, _process_word_question, _parse_visualization_query_with_unlimited_filters,  _create_enhanced_chart_with_unlimited_filters, process_enhanced_query, _detect_statistical_intent, assess_data_quality, display_data_quality_report, display_enhanced_chart,  display_performance_metrics, display_enhanced_predictive_modeling_interface, display_model_results, display_simplified_model_results, display_data_analysis_page, display_data_explorer_page, display_welcome_page, display_pdf_explorer, display_word_explorer, main
    
#     # Initialize agent here to store for session-based reference
#     agent = AdvancedPDFProcessor(
#         ollama_client=AI_MODELS.get('ollama'), 
#         ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
#     )

#     pdf_content = agent.process_pdf_fast(file_obj)
#     if not pdf_content or pdf_content.get('status') != 'success':
#         return Response({'error': 'PDF processing failed', 'details': pdf_content}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     # Create session
#     pdf_id = str(uuid.uuid4())
#     user_id = request.user.id

#     # Save file on disk
#     file_path = save_user_file(file_obj, user_id, 'pdf', pdf_id, 'pdf')

#     # Create record in MySQL
#     UploadedFile.objects.create(
#         user=request.user,
#         file_id=pdf_id,
#         file_path=file_path,
#         filename=file_obj.name,
#         metadata=pdf_content.get('metadata', {})
#     )

#     # Remove in-memory session storage for pdf_id if exists
#     PDF_SESSIONS.pop(pdf_id, None)

#     session_data = {
#         'pdf_agent': agent,
#         'pdf_content': pdf_content,
#         'chat_history': [],
#         'user_id': request.user.id
#     }
#     PDF_SESSIONS[pdf_id] = session_data

#     # Update persistent JSON file for user
#     user_email = request.user.email
#     user_history = load_user_history(user_email)
#     user_history['sessions'].append({
#         'type': 'pdf',
#         'id': pdf_id,
#         'chat_history': [],
#         'metadata': pdf_content.get('metadata', {}),
#         'tables': len(pdf_content.get('tables', [])),
#         'images': len(pdf_content.get('images', [])),
#         'chunks': len(pdf_content.get('chunks', [])),
#         'time_stamp': (datetime.utcnow() + timedelta(hours=5, minutes=30)).isoformat() + 'Z'
#     })
#     save_user_history(user_email, user_history)


#     return Response({
#         'status': 'success',
#         'pdf_id': pdf_id,
#         'metadata': pdf_content.get('metadata', {}),
#         'tables': len(pdf_content.get('tables', [])),
#         'images': len(pdf_content.get('images', [])),
#         'chunks': len(pdf_content.get('chunks', [])),
#         'time_stamp': (datetime.utcnow() + timedelta(hours=5, minutes=30)).isoformat() + 'Z'
#     }, status=status.HTTP_201_CREATED)

# Sent by Arun 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_pdf(request):
    file_obj = request.FILES.get('file')
    if not file_obj:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
 
    from .chatbot_curerent_v3 import AdvancedPDFProcessor, AI_MODELS
 
    # Initialize agent
    agent = AdvancedPDFProcessor(
        ollama_client=AI_MODELS.get('ollama'),
        ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
    )
 
    pdf_content = agent.process_pdf_fast(file_obj)
    if not pdf_content or pdf_content.get('status') != 'success':
        return Response({'error': 'PDF processing failed', 'details': pdf_content}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    pdf_id = str(uuid.uuid4())
    user_id = request.user.id
 
    # Save file to disk
    file_path = save_user_file(file_obj, user_id, 'pdf', pdf_id, 'pdf')
 
    # Save record in DB
    UploadedFile.objects.create(
        user=request.user,
        file_id=pdf_id,
        file_path=file_path,
        filename=file_obj.name,
        metadata=pdf_content.get('metadata', {})
    )
 
    # --- Store in user-specific in-memory session ---
    if user_id not in PDF_SESSIONS_BY_USER:
        PDF_SESSIONS_BY_USER[user_id] = {}
 
    PDF_SESSIONS_BY_USER[user_id][pdf_id] = {
        'pdf_agent': agent,
        'pdf_content': pdf_content,
        'chat_history': []
    }
 
    # Update persistent JSON history
    user_email = request.user.email
    user_history = load_user_history(user_email)
    user_history['sessions'].append({
        'type': 'pdf',
        'id': pdf_id,
        'chat_history': [],
        'metadata': pdf_content.get('metadata', {}),
        'tables': len(pdf_content.get('tables', [])),
        'images': len(pdf_content.get('images', [])),
        'chunks': len(pdf_content.get('chunks', [])),
        'time_stamp': (datetime.utcnow() + timedelta(hours=5, minutes=30)).isoformat() + 'Z'
    })
    save_user_history(user_email, user_history)
 
    return Response({
        'status': 'success',
        'pdf_id': pdf_id,
        'metadata': pdf_content.get('metadata', {}),
        'tables': len(pdf_content.get('tables', [])),
        'images': len(pdf_content.get('images', [])),
        'chunks': len(pdf_content.get('chunks', [])),
        'time_stamp': (datetime.utcnow() + timedelta(hours=5, minutes=30)).isoformat() + 'Z'
    }, status=status.HTTP_201_CREATED)
 

# Initialize MongoDB client once (adjust connection string)
mongo_client = MongoClient("mongodb://localhost:27017/")
history_collection = mongo_client["chatbot_db"]["user_history"]

# Utility to save chat history to MongoDB
def save_chat_history_to_mongo(user_id, file_id, question, answer, timestamp=None, file_type="PDF", metadata=None, filename=None):
    timestamp = timestamp or datetime.utcnow().isoformat()
    chat_entry = {
        "role": "user",
        "message": question,
        "timestamp": timestamp
    }
    answer_entry = {
        "role": "bot",
        "message": answer,
        "timestamp": timestamp
    }

    existing_doc = history_collection.find_one({
        "user_id": user_id,
        "file_id": file_id
    })

    if existing_doc:
        history_collection.update_one(
            {"_id": existing_doc["_id"]},
            {
                "$push": {"chat_history": {"$each": [chat_entry, answer_entry]}},
                "$set": {"last_updated": timestamp}
            }
        )
    else:
        history_collection.insert_one({
            "user_id": user_id,
            "file_id": file_id,
            "file_type": file_type,
            "filename": filename,
            "metadata": metadata or {},
            # "file_type": "PDF",
            "chat_history": [chat_entry, answer_entry],
            "last_updated": timestamp
        })


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def ask_pdf_question(request, pdf_id):
#     data = request.data
#     question = data.get('question', '').strip()
#     if not question:
#         return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

#     print("Received pdf_id:", pdf_id)
#     uploaded_file = get_object_or_404(
#         UploadedFile,
#         file_id=pdf_id,
#         user=request.user
#         # file_type='PDF'
#     )

#     file_path = uploaded_file.file_path
    

#     from .chatbot_curerent_v3 import extract_comprehensive_pdf_content, AdvancedPDFProcessor, AI_MODELS
#     agent = AdvancedPDFProcessor(
#         ollama_client=AI_MODELS.get('ollama'),
#         ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
#     )

#     try:
#         with open(file_path, 'rb') as f:
#             pdf_content = agent.process_pdf_fast(f)
#     except Exception as e:
#         return Response({'error': f"Failed to process PDF file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     if not pdf_content or pdf_content.get('status') != 'success':
#         return Response({'error': 'PDF processing failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     answer_data = agent.answer_question(question, pdf_content)

#     timestamp = (datetime.utcnow() + timedelta(hours=5, minutes=30)).isoformat() + 'Z'
#     save_chat_history_to_mongo(
#         user_id=str(request.user.id),
#         file_id=pdf_id,
#         question=question,
#         answer=answer_data.get('answer'),
#         timestamp=timestamp,
#         file_type="PDF",
#         metadata=pdf_content.get("metadata", {}),
#         filename=os.path.basename(file_path)
#     )

#     return Response({
#         'question': question,
#         'answer': answer_data.get('answer'),
#         'confidence': answer_data.get('confidence'),
#         'method': answer_data.get('method'),
#         'relevant_pages': answer_data.get('relevant_pages', []),
#         'time_stamp': timestamp
#     }, status=status.HTTP_200_OK)

# sent By Arun

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_pdf_question(request, pdf_id):
    data = request.data
    question = data.get('question', '').strip()
    if not question:
        return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)
 
    user_id = request.user.id
    user_sessions = PDF_SESSIONS_BY_USER.get(user_id, {})
 
    # --- Step 1: Check if PDF is already in user session ---
    session_data = user_sessions.get(pdf_id)
    if session_data:
        pdf_content = session_data['pdf_content']
        agent = session_data['pdf_agent']
    else:
        # --- Step 2: Load PDF from disk if not in session ---
        uploaded_file = get_object_or_404(UploadedFile, file_id=pdf_id, user=request.user)
        file_path = uploaded_file.file_path
 
        from .chatbot_curerent_v3 import AdvancedPDFProcessor, AI_MODELS
        agent = AdvancedPDFProcessor(
            ollama_client=AI_MODELS.get('ollama'),
            ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
        )
 
        try:
            with open(file_path, 'rb') as f:
                pdf_content = agent.process_pdf_fast(f)
        except Exception as e:
            return Response({'error': f"Failed to process PDF file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
        if not pdf_content or pdf_content.get('status') != 'success':
            return Response({'error': 'PDF processing failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
        # --- Step 3: Save in user session for future queries ---
        if user_id not in PDF_SESSIONS_BY_USER:
            PDF_SESSIONS_BY_USER[user_id] = {}
        PDF_SESSIONS_BY_USER[user_id][pdf_id] = {
            'pdf_agent': agent,
            'pdf_content': pdf_content,
            'chat_history': []
        }
 
    # --- Step 4: Answer the question ---
    answer_data = agent.answer_question(question, pdf_content)
 
    timestamp = (datetime.utcnow() + timedelta(hours=5, minutes=30)).isoformat() + 'Z'
    save_chat_history_to_mongo(
        user_id=str(request.user.id),
        file_id=pdf_id,
        question=question,
        answer=answer_data.get('answer'),
        timestamp=timestamp,
        file_type="PDF",
        metadata=pdf_content.get("metadata", {}),
        filename=os.path.basename(uploaded_file.file_path) if 'uploaded_file' in locals() else ""
    )
 
    return Response({
        'question': question,
        'answer': answer_data.get('answer'),
        'confidence': answer_data.get('confidence'),
        'method': answer_data.get('method'),
        'relevant_pages': answer_data.get('relevant_pages', []),
        'time_stamp': timestamp
    }, status=status.HTTP_200_OK)
 
 

PDF_SESSIONS_BY_USER = {}  # Instead of using only PDF_SESSIONS


def raw_sample_data(df, n=10):
    # Replace NaN with empty string to avoid JSON issues (don't change inf)
    df_temp = df.fillna('')

    # Convert non-serializable types if any (e.g. datetime)
    for col in df_temp.columns:
        if np.issubdtype(df_temp[col].dtype, np.datetime64):
            df_temp[col] = df_temp[col].astype(str)

    return df_temp.head(n).to_dict(orient="records")


# In-memory session store (you might want something persistent in real setups)
DATASET_SESSIONS = {}


from .models import UploadedFile  # Your new MySQL model
import uuid
from datetime import datetime, timedelta



from .chatbot_curerent_v3 import AdvancedCSVProcessor, AI_MODELS
 
# Version 3 upload_excel_csv

# Replace in upload_excel_csv
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @parser_classes([MultiPartParser])
# def upload_excel_csv(request):
#     file_obj = request.FILES.get('file')
#     if not file_obj:
#         return Response({'error': 'No file provided'}, status=400)
 
#     import pandas as pd
 
#     try:
#         if file_obj.name.endswith('.csv'):
#             df = pd.read_csv(file_obj)
#             ext = 'csv'
#         elif file_obj.name.endswith(('.xls', '.xlsx')):
#             df = pd.read_excel(file_obj)
#             ext = file_obj.name.split('.')[-1]
#         else:
#             return Response({'error': 'Unsupported file format'}, status=400)
#     except Exception as e:
#         return Response({'error': 'Failed to process file', 'details': str(e)}, status=500)
   
#     try:
#         sample_rows = raw_sample_data(df, 10)
#     except Exception as e:
#         sample_rows = []
 
#     # Use AdvancedCSVProcessor instead of AgenticTabularProcessor
#     processor = AdvancedCSVProcessor(
#         ollama_client=AI_MODELS.get('ollama'),
#         ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
#     )
#     # Process CSV for metadata, chunks, etc.
#     csv_content = processor.process_csv_fast(df, file_obj.name)
 
#     # Save file on disk as before
#     dataset_id = str(uuid.uuid4())
#     user_id = request.user.id
#     file_path = save_user_file(file_obj, user_id, 'excel', dataset_id, ext)
 
#     # Save UploadedFile record
#     UploadedFile.objects.create(
#         user=request.user,
#         file_id=dataset_id,
#         file_path=file_path,
#         filename=file_obj.name,
#         metadata={
#             'rows': len(df),
#             'columns': len(df.columns),
#             'columns_list': list(df.columns),
#         }
#     )
 
#     # Cache/store the csv_content for this dataset_id for QA later
#     DATASET_SESSIONS[dataset_id] = csv_content
 
#     return Response({
#         'status': 'success',
#         'dataset_id': dataset_id,
#         'rows': len(df),
#         'columns': len(df.columns),
#         'columns_list': list(df.columns),
#         'sample_data': sample_rows,
#         'time_stamp': (datetime.utcnow() + timedelta(hours=5, minutes=30)).isoformat() + 'Z'
#     }, status=201)
 

# Sent by Arun

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_excel_csv(request):
    file_obj = request.FILES.get('file')
    if not file_obj:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
 
    try:
        if file_obj.name.endswith('.csv'):
            df = pd.read_csv(file_obj)
            ext = 'csv'
        elif file_obj.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_obj)
            ext = file_obj.name.split('.')[-1]
        else:
            return Response({'error': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'Failed to process file', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    try:
        sample_rows = raw_sample_data(df, 10)
    except Exception:
        sample_rows = []
 
    # Initialize processor
    processor = AdvancedCSVProcessor(
        ollama_client=AI_MODELS.get('ollama'),
        ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
    )
    csv_content = processor.process_csv_fast(df, file_obj.name)
 
    # Save file to disk
    dataset_id = str(uuid.uuid4())
    user_id = request.user.id
    file_path = save_user_file(file_obj, user_id, 'excel', dataset_id, ext)
 
    # Save record in DB
    UploadedFile.objects.create(
        user=request.user,
        file_id=dataset_id,
        file_path=file_path,
        filename=file_obj.name,
        metadata={
            'rows': len(df),
            'columns': len(df.columns),
            'columns_list': list(df.columns),
        }
    )
 
    # --- Store in user-specific in-memory session ---
    if user_id not in DATASET_SESSIONS:
        DATASET_SESSIONS[user_id] = {}
 
    DATASET_SESSIONS[user_id][dataset_id] = {
        'csv_processor': processor,
        'csv_content': csv_content,
        'chat_history': []
    }
 
    return Response({
        'status': 'success',
        'dataset_id': dataset_id,
        'rows': len(df),
        'columns': len(df.columns),
        'columns_list': list(df.columns),
        'sample_data': sample_rows,
        'time_stamp': (datetime.utcnow() + timedelta(hours=5, minutes=30)).isoformat() + 'Z'
    }, status=status.HTTP_201_CREATED)
 
 
 
# Version 3  ask_data_question

# Replace in ask_data_question
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def ask_data_question(request, dataset_id):
#     data = request.data
#     question = data.get('question', '').strip()
#     if not question:
#         return Response({'error': 'No question provided'}, status=400)
 
#     uploaded_file = get_object_or_404(UploadedFile, file_id=dataset_id, user=request.user)
#     file_path = uploaded_file.file_path
 
#     # Load csv_content from cache
#     csv_content = DATASET_SESSIONS.get(dataset_id)
 
#     # If not cached, fallback to load dataframe and preprocess (optional)
#     if not csv_content:
#         try:
#             import pandas as pd
#             if file_path.lower().endswith('.csv'):
#                 df = pd.read_csv(file_path)
#             else:
#                 df = pd.read_excel(file_path)
#         except Exception as e:
#             return Response({'error': f'Failed to load dataset file: {str(e)}'}, status=500)
 
#         processor = AdvancedCSVProcessor(
#             ollama_client=AI_MODELS.get('ollama'),
#             ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
#         )
#         csv_content = processor.process_csv_fast(df, file_path)
#         DATASET_SESSIONS[dataset_id] = csv_content  # Cache
 
#     processor = AdvancedCSVProcessor(
#         ollama_client=AI_MODELS.get('ollama'),
#         ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
#     )
#     answer_data = processor.answer_question(question, csv_content)
 
#     timestamp = (datetime.utcnow() + timedelta(hours=5, minutes=30)).isoformat() + 'Z'
#     save_chat_history_to_mongo(
#         user_id=str(request.user.id),
#         file_id=dataset_id,
#         question=question,
#         answer=answer_data.get('answer') or answer_data.get('response'),
#         timestamp=timestamp,
#         file_type="EXCEL",
#         metadata = {
#             'rows': csv_content.get("data_summary", {}).get("basic_info", {}).get("rows", 0),
#             'columns': csv_content.get("data_summary", {}).get("basic_info", {}).get("column_names", [])
#         },
 
#         filename=os.path.basename(file_path)
#     )
 
#     return Response({
#         'question': question,
#         'answer': answer_data.get('answer') or answer_data.get('response'),
#         'confidence': answer_data.get('confidence', 0),
#         'method': answer_data.get('method', 'ollama_csv_rag'),
#         'analysis_data': {},  # No direct equivalent, could add csv_content['data_summary'] if useful
#         'plan_executed': {},  # No direct equivalent
#         'time_stamp': timestamp
#     }, status=200)
 
# Sent By Arun

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_data_question(request, dataset_id):
    data = request.data
    question = data.get('question', '').strip()
    if not question:
        return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)
 
    user_id = request.user.id
    user_sessions = DATASET_SESSIONS.get(user_id, {})
    session_data = user_sessions.get(dataset_id)
 
    # --- Step 1: Use existing session if available ---
    if session_data:
        csv_content = session_data['csv_content']
        processor = session_data['csv_processor']
    else:
        # --- Step 2: Fallback: load from DB + disk ---
        uploaded_file = get_object_or_404(UploadedFile, file_id=dataset_id, user=request.user)
        file_path = uploaded_file.file_path
 
        try:
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        except Exception as e:
            return Response({'error': f'Failed to load dataset file: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
        processor = AdvancedCSVProcessor(
            ollama_client=AI_MODELS.get('ollama'),
            ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
        )
        csv_content = processor.process_csv_fast(df, file_path)
 
        # --- Step 3: Save in user session for future queries ---
        if user_id not in DATASET_SESSIONS:
            DATASET_SESSIONS[user_id] = {}
        DATASET_SESSIONS[user_id][dataset_id] = {
            'csv_processor': processor,
            'csv_content': csv_content,
            'chat_history': []
        }
 
    # --- Step 4: Ask question ---
    answer_data = processor.answer_question(question, csv_content)
 
    timestamp = (datetime.utcnow() + timedelta(hours=5, minutes=30)).isoformat() + 'Z'
    save_chat_history_to_mongo(
        user_id=str(request.user.id),
        file_id=dataset_id,
        question=question,
        answer=answer_data.get('answer') or answer_data.get('response'),
        timestamp=timestamp,
        file_type="EXCEL",
        metadata={
            'rows': csv_content.get("data_summary", {}).get("basic_info", {}).get("rows", 0),
            'columns': csv_content.get("data_summary", {}).get("basic_info", {}).get("column_names", [])
        },
        filename=os.path.basename(uploaded_file.file_path) if 'uploaded_file' in locals() else ""
    )
 
    return Response({
        'question': question,
        'answer': answer_data.get('answer') or answer_data.get('response'),
        'confidence': answer_data.get('confidence', 0),
        'method': answer_data.get('method', 'ollama_csv_rag'),
        'analysis_data': {},  # Could be extended with csv_content['data_summary']
        'plan_executed': {},  # Placeholder
        'time_stamp': timestamp
    }, status=status.HTTP_200_OK)
 


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_chat_histories_for_user(request):
    user_id = request.user.id
    sessions = USER_SESSIONS.get(user_id, [])
    return Response({'sessions': sessions}, status=status.HTTP_200_OK)


# Version 1 of chat_with_bot

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def chat_with_bot(request):
#     data = request.data
#     question = data.get('question', '').strip()

#     if not question:
#         return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

#     from .chatbot_curerent_v3 import AI_MODELS

#     # Get Ollama client and model name
#     ollama_client = AI_MODELS.get('ollama')
#     ollama_model = AI_MODELS.get('ollama_model', 'llama3.2')

#     if not ollama_client or not AI_MODELS.get('ollama_available', False):
#         return Response({'error': "Ollama model not available"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

#     try:
#         # Use the Ollama client's chat API (adjust per your client's docs)
#         response = ollama_client.chat(
#             model=ollama_model,
#             messages=[{"role": "user", "content": question}]
#         )
#         answer = response['message']['content'] if 'message' in response else None

#         # LOAD user's chat history
#         user_email = request.user.email
#         user_history = load_user_history(user_email)

#         # Find or create a 'chat' session for generic bot chat (adjust as needed)
#         for sess in user_history['sessions']:
#             if sess.get('type') == 'chat':
#                 chat_session = sess
#                 break
#         else:
#             # Create a new chat session if not found
#             chat_session = {'type': 'chat', 'id': 'bot-chat', 'chat_history': []}
#             user_history['sessions'].append(chat_session)

#         # Add question and answer to chat_history
#         chat_session['chat_history'].append({'role': 'user', 'message': question})
#         chat_session['chat_history'].append({'role': 'bot', 'message': answer})

#         # SAVE updated user history
#         save_user_history(user_email, user_history)

#         return Response({
#             'question': question,
#             'answer': answer
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({'error': f"Bot failed to answer: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def save_normal_chat_history_to_mongo(user_id, session_id, question, answer, timestamp=None):
    timestamp = timestamp or datetime.utcnow().isoformat()
    chat_entry = {
        "role": "user",
        "message": question,
        "timestamp": timestamp
    }
    answer_entry = {
        "role": "bot",
        "message": answer,
        "timestamp": timestamp
    }

    existing_doc = history_collection.find_one({
        "user_id": user_id,
        "file_id": session_id  # Using session_id as file_id for generic chat
    })

    if existing_doc:
        history_collection.update_one(
            {"_id": existing_doc["_id"]},
            {
                "$push": {"chat_history": {"$each": [chat_entry, answer_entry]}},
                "$set": {"last_updated": timestamp}
            }
        )
    else:
        history_collection.insert_one({
            "user_id": user_id,
            "file_id": session_id,
            "file_type": "chat",
            "chat_history": [chat_entry, answer_entry],
            "last_updated": timestamp
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_bot(request):
    data = request.data
    question = data.get('question', '').strip()

    if not question:
        return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

    from .chatbot_curerent_v3 import AI_MODELS

    ollama_client = AI_MODELS.get('ollama')
    ollama_model = AI_MODELS.get('ollama_model', 'llama3.2')

    if not ollama_client or not AI_MODELS.get('ollama_available', False):
        return Response({'error': "Ollama model not available"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        response = ollama_client.chat(
            model=ollama_model,
            messages=[{"role": "user", "content": question}]
        )
        answer = response['message']['content'] if 'message' in response else None

        user_id = str(request.user.id)
        session_id = 'bot-chat'  # single generic chat session ID

        # Save chat history to MongoDB
        save_normal_chat_history_to_mongo(user_id=user_id, session_id=session_id,
                                   question=question, answer=answer,
                                   timestamp=datetime.utcnow().isoformat())

        return Response({
            'question': question,
            'answer': answer
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f"Bot failed to answer: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# @api_view(['POST'])
# @parser_classes([MultiPartParser])
# def upload_multiple_documents(request):
#     files = request.FILES.getlist('files')
#     if not files:
#         return Response({'error': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)
    
#     documents_id = str(uuid.uuid4())
#     document_data = {'files': {}, 'chunks': []}

#     for file_obj in files:
#         filename = file_obj.name
#         ext = filename.lower().split('.')[-1]
#         file_type = None
#         parsed_content = {}
#         try:
#             if ext == 'pdf':
#                 file_type = 'PDF'
#                 agent = AdvancedPDFProcessor(
#                     ollama_client=AI_MODELS.get('ollama'),
#                     ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
#                 )
#                 parsed_content = agent.process_pdf_fast(file_obj)
#                 if parsed_content.get('status') == 'success' and parsed_content.get('chunks'):
#                     for chunk in parsed_content['chunks']:
#                         chunk['source_file'] = filename
#                     document_data['chunks'].extend(parsed_content['chunks'])
#             elif ext in ('xls', 'xlsx', 'csv'):
#                 file_type = 'EXCEL'
#                 if ext == 'csv':
#                     df = pd.read_csv(file_obj)
#                 else:
#                     df = pd.read_excel(file_obj)
#                 parsed_content = {
#                     'file_type': 'csv_qa',
#                     'status': 'success',
#                     'text_content': df.to_csv(index=False),
#                     'data_summary': {
#                         'basic_info': {
#                             'rows': df.shape[0],
#                             'column_names': list(df.columns)
#                         }
#                     },
#                     'chunks': [{
#                         'content': df.to_csv(index=False),
#                         'source_file': filename
#                     }]
#                 }
#                 document_data['chunks'].extend(parsed_content['chunks'])
#             elif ext in ('doc', 'docx'):
#                 file_type = 'WORD'
#                 agent = AdvancedWordProcessor(
#                     ollama_client=AI_MODELS.get('ollama'),
#                     ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
#                 )
#                 parsed_content = agent.process_word_fast(file_obj)
#                 if parsed_content.get('status') == 'success' and parsed_content.get('chunks'):
#                     for chunk in parsed_content['chunks']:
#                         chunk['source_file'] = filename
#                     document_data['chunks'].extend(parsed_content['chunks'])
#             else:
#                 continue

#             parsed_content['file_type'] = file_type
#             parsed_content['status'] = parsed_content.get('status', 'success')
#             document_data['files'][filename] = parsed_content
#         except Exception as e:
#             document_data['files'][filename] = {
#                 'file_type': file_type or 'unknown',
#                 'status': 'error',
#                 'error': str(e)
#             }
    
#     DOCUMENT_GROUPS[documents_id] = document_data

#     return Response({
#         'documents_id': documents_id,
#         'details': [
#             {'filename': fn, 'status': fc.get('status'), 'file_type': fc.get('file_type')}
#             for fn, fc in document_data['files'].items()
#         ]
#     }, status=status.HTTP_201_CREATED)



# @api_view(['POST'])
# def ask_combined_documents(request, documents_id):
#     question = request.data.get('question', '').strip()
#     if not question:
#         return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

#     document_data = DOCUMENT_GROUPS.get(documents_id)
#     if not document_data:
#         return Response({'error': 'Invalid documents_id'}, status=status.HTTP_404_NOT_FOUND)

#     # Mock Streamlit session_state for knowledge_base with your stored files
#     if not hasattr(st, 'session_state'):
#         st.session_state = {}
#     st.session_state['knowledge_base'] = {'files': document_data['files']}

#     try:
#         combined_content = combine_knowledge_base()
#         result = _process_knowledge_base_question(question, combined_content)
#     except Exception as e:
#         return Response({'error': f'Error processing question: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     return Response(result, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_multiple_documents(request):
    files = request.FILES.getlist('files')
    if not files:
        return Response({'error': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)

    user_id = str(request.user.id)
    user = request.user
    documents_id = str(uuid.uuid4())
    document_data = {'files': {}, 'chunks': []}

    # Create DocumentGroup instance
    document_group = DocumentGroup.objects.create(
        documents_id=documents_id,
        user=user
    )

    for file_obj in files:
        filename = file_obj.name
        ext = filename.lower().split('.')[-1]
        file_type = None
        parsed_content = {}
        document_file_id = str(uuid.uuid4())

        try:
            # Save file on disk
            file_path = save_user_file(file_obj, user_id, ext, document_file_id, ext)

            if ext == 'pdf':
                file_type = 'PDF'
                agent = AdvancedPDFProcessor(
                    ollama_client=AI_MODELS.get('ollama'),
                    ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
                )
                parsed_content = agent.process_pdf_fast(file_obj)
                if parsed_content.get('status') == 'success' and parsed_content.get('chunks'):
                    for chunk in parsed_content['chunks']:
                        chunk['source_file'] = filename
                    document_data['chunks'].extend(parsed_content['chunks'])

            elif ext in ('xls', 'xlsx', 'csv'):
                file_type = 'EXCEL'
                if ext == 'csv':
                    df = pd.read_csv(file_obj)
                else:
                    df = pd.read_excel(file_obj)
                parsed_content = {
                    'file_type': 'csv_qa',
                    'status': 'success',
                    'text_content': df.to_csv(index=False),
                    'data_summary': {
                        'basic_info': {
                            'rows': df.shape[0],
                            'column_names': list(df.columns)
                        }
                    },
                    'chunks': [{
                        'content': df.to_csv(index=False),
                        'source_file': filename
                    }]
                }
                document_data['chunks'].extend(parsed_content['chunks'])

            elif ext in ('doc', 'docx'):
                file_type = 'WORD'
                agent = AdvancedWordProcessor(
                    ollama_client=AI_MODELS.get('ollama'),
                    ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
                )
                parsed_content = agent.process_word_fast(file_obj)
                if parsed_content.get('status') == 'success' and parsed_content.get('chunks'):
                    for chunk in parsed_content['chunks']:
                        chunk['source_file'] = filename
                    document_data['chunks'].extend(parsed_content['chunks'])
            else:
                continue  # unsupported format, skip

            parsed_content['file_type'] = file_type
            parsed_content['status'] = parsed_content.get('status', 'success')
            parsed_content['filename'] = filename
            document_data['files'][filename] = parsed_content

            # Save file metadata in Django DB
            UploadedFile.objects.create(
                user=request.user,
                file_id=document_file_id,
                file_type=file_type,
                file_path=file_path,
                filename=filename,
                metadata=parsed_content.get('metadata', {}),
                document_group=document_group
            )

        except Exception as e:
            document_data['files'][filename] = {
                'file_type': file_type or 'unknown',
                'status': 'error',
                'error': str(e)
            }

    DOCUMENT_GROUPS[documents_id] = document_data

    return Response({
        'documents_id': documents_id,
        'details': [
            {'filename': fn, 'status': fc.get('status'), 'file_type': fc.get('file_type'), 'error': fc.get('error', '')}
            for fn, fc in document_data['files'].items()
        ]
    }, status=status.HTTP_201_CREATED)

# Import your streamlit functions for knowledge base operations
from .MultipleUpload import combine_knowledge_base, _process_knowledge_base_question

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def ask_combined_documents(request, documents_id):
    question = request.data.get('question', '').strip()
    if not question:
        return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

    document_data = DOCUMENT_GROUPS.get(documents_id)
    if not document_data:
        return Response({'error': 'Invalid documents_id'}, status=status.HTTP_404_NOT_FOUND)

    # Set streamlit session_state knowledge_base for compatibility
    if not hasattr(st, 'session_state'):
        st.session_state = {}
    st.session_state['knowledge_base'] = {'files': document_data['files']}

    try:
        combined_content = combine_knowledge_base()
        result = _process_knowledge_base_question(question, combined_content)

        filenames = list(document_data['files'].keys())

        # Save chat history in MongoDB
        save_chat_history_to_mongo(
            user_id=str(request.user.id),
            file_id=documents_id,
            question=question,
            answer=result.get('answer'),
            timestamp=datetime.utcnow().isoformat(),
            metadata={"filenames": filenames}
        )
    except Exception as e:
        return Response({'error': f'Error processing question: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(result, status=status.HTTP_200_OK)

# Sent By Arun
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_user_file(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(file_id=file_id, user=request.user)
        file_path = uploaded_file.file_path
        filename = uploaded_file.filename or os.path.basename(file_path)
 
        if not os.path.exists(file_path):
            raise Http404("File not found")
 
        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'
 
        # Use Django FileResponse to stream the file
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
 
    except UploadedFile.DoesNotExist:
        raise Http404("File not found")