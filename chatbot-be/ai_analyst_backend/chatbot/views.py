import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import User
from .serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth.hashers import check_password
import uuid
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework_simplejwt.tokens import AccessToken
from .chatbot_curerent_v3 import *
import pandas as pd



# Secret key
JWT_SECRET = getattr(settings, 'SECRET_KEY', 'your_jwt_secret')
JWT_EXP_DELTA_SECONDS = 3600


@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        access_token.set_exp(lifetime=timedelta(minutes=60))  # token expiry

        return Response({
            'token': str(access_token),
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
            }
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# In-memory session store for demo (replace with Redis or DB in production)
PDF_SESSIONS = {}

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_pdf(request):
    file_obj = request.FILES.get('file')
    if not file_obj:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    # Process the PDF
    from .chatbot_v3 import extract_comprehensive_pdf_content, AdvancedPDFProcessor, AI_MODELS
    # from .chatbot_curerent_v3 import extract_comprehensive_pdf_content, AdvancedPDFProcessor, AI_MODELS
    # from .chatbot_curerent_v3 import extract_comprehensive_pdf_content, AdvancedPDFProcessor, AI_MODELS, AppConfig, initialize_session_state, load_ai_models, enhanced_error_handling, track_performance, validate_input, QueryIntentAgent, SmartSuggestionAgent, VisualizationAgent, PredictiveModelingAgent, SimplifiedPredictiveModelingAgent, AdvancedWordProcessor, AgenticTabularProcessor, load_and_validate_data, smart_data_type_conversion, detect_lookup_query, _parse_statistical_query_with_unlimited_filters, _extract_all_filters_enhanced, _process_statistical_lookup_with_unlimited_filters, _apply_smart_date_filter, _apply_statistical_operation_robust, _process_simple_lookup, _find_best_column_match, _apply_smart_filter, _create_error_response, find_column_match, detect_statistical_query, perform_statistical_analysis, detect_outliers, perform_clustering, perform_data_distribution_analysis, extract_comprehensive_pdf_content, handle_pdf_file_upload, display_pdf_qa_section, _process_pdf_question,  extract_comprehensive_word_content, handle_word_file_upload, display_word_qa_section, _process_word_question, _parse_visualization_query_with_unlimited_filters,  _create_enhanced_chart_with_unlimited_filters, process_enhanced_query, _detect_statistical_intent, assess_data_quality, display_data_quality_report, display_enhanced_chart,  display_performance_metrics, display_enhanced_predictive_modeling_interface, display_model_results, display_simplified_model_results, display_data_analysis_page, display_data_explorer_page, display_welcome_page, display_pdf_explorer, display_word_explorer, main
    
    # Initialize agent here to store for session-based reference
    agent = AdvancedPDFProcessor(
        ollama_client=AI_MODELS.get('ollama'), 
        ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
    )

    pdf_content = agent.process_pdf_fast(file_obj)
    if not pdf_content or pdf_content.get('status') != 'success':
        return Response({'error': 'PDF processing failed', 'details': pdf_content}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Create session
    pdf_id = str(uuid.uuid4())
    PDF_SESSIONS[pdf_id] = {
        'pdf_agent': agent,
        'pdf_content': pdf_content,
        'chat_history': []
    }
    return Response({
        'status': 'success',
        'pdf_id': pdf_id,
        'metadata': pdf_content.get('metadata', {}),
        'tables': len(pdf_content.get('tables', [])),
        'images': len(pdf_content.get('images', [])),
        'chunks': len(pdf_content.get('chunks', []))

    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_pdf_question(request, pdf_id):
    data = request.data
    question = data.get('question', '').strip()
    if not question:
        return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

    pdf_session = PDF_SESSIONS.get(pdf_id)
    if not pdf_session:
        return Response({'error': 'PDF session not found'}, status=status.HTTP_404_NOT_FOUND)

    pdf_agent = pdf_session['pdf_agent']
    pdf_content = pdf_session['pdf_content']

    answer_data = pdf_agent.answer_question(question, pdf_content)
    # Append to history
    pdf_session['chat_history'].append({'role': 'user', 'message': question})
    pdf_session['chat_history'].append({'role': 'assistant', **answer_data})

    return Response({
        'question': question,
        'answer': answer_data.get('answer'),
        'confidence': answer_data.get('confidence'),
        'method': answer_data.get('method'),
        'relevant_pages': answer_data.get('relevant_pages', [])
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request, pdf_id):
    pdf_session = PDF_SESSIONS.get(pdf_id)
    if not pdf_session:
        return Response({'error': 'PDF session not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'history': pdf_session['chat_history']}, status=status.HTTP_200_OK)




# In-memory session store (you might want something persistent in real setups)
DATASET_SESSIONS = {}

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_excel_csv(request):
    file_obj = request.FILES.get('file')
    if not file_obj:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    # Try to load file into pandas DataFrame
    try:
        if file_obj.name.endswith('.csv'):
            df = pd.read_csv(file_obj)
        elif file_obj.name.endswith('.xls') or file_obj.name.endswith('.xlsx'):
            df = pd.read_excel(file_obj)
        else:
            return Response({'error': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'Failed to process file', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Initialize tabular agent (no DataFrame in constructor)
    agent = AgenticTabularProcessor(
        ollama_client=AI_MODELS.get('ollama'),
        ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
    )

    # try:
    #     df_clean = df.replace([np.inf, -np.inf], np.nan).fillna(None)
    #     sample_rows = df.head(1000).to_dict(orient="records")
    # except Exception as e:
    #     sample_rows = []

    dataset_id = str(uuid.uuid4())
    DATASET_SESSIONS[dataset_id] = {
        'data_agent': agent,
        'dataframe': df,
        'chat_history': []
    }
    return Response({
        'status': 'success',
        'dataset_id': dataset_id,
        'rows': df.shape[0],
        'columns': df.shape[1],
        'columns_list': list(df.columns),
        # 'sample_data': sample_rows
    }, status=status.HTTP_201_CREATED)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_data_question(request, dataset_id):
    data = request.data
    question = data.get('question', '').strip()
    if not question:
        return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

    dataset_session = DATASET_SESSIONS.get(dataset_id)
    if not dataset_session:
        return Response({'error': 'Dataset session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    agent = dataset_session['data_agent']
    df = dataset_session['dataframe']
    
    answer_data = agent.process_tabular_query(df, question)
    dataset_session['chat_history'].append({'role': 'user', 'message': question})
    dataset_session['chat_history'].append({'role': 'assistant', **answer_data})
    
    return Response({
        'question': question,
        'answer': answer_data.get('answer'),
        'confidence': answer_data.get('confidence'),
        'method': answer_data.get('method'),
        'analysis_data': answer_data.get('analysis_data', {}),
        'plan_executed': answer_data.get('plan_executed', {})
    }, status=status.HTTP_200_OK)
