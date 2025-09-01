
# ============================================================================
# 1. 🔧 IMPORTS & HEADERS
# ============================================================================

"""
🤖 Enhanced AI Data Analyst - Demo Ready Version
====================================================

A modern, AI-powered data analysis application with:
- AI Agent-based intent detection and query processing
- Smart visualization creation with dynamic recommendations
- Advanced PDF processing with multi-modal extraction
- Statistical analysis with natural language interface
- Real-time query processing with error handling
- Production-ready architecture with monitoring

Author: AI-Enhanced Development
Version: 3.0 (Demo Ready) __NAYAN & AI TOOLS - CLAUDE/GPT
"""

import streamlit as st
st.set_page_config(page_title="AI Data Analyst NooB", layout="wide", initial_sidebar_state="expanded")

# Core imports
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io
import re
import time
import warnings
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Union
from dataclasses import dataclass
from functools import wraps
import logging
import traceback
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
import uuid

# ML and AI imports (with fallbacks)
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    from transformers import pipeline
    AI_MODELS_AVAILABLE = True
except ImportError:
    AI_MODELS_AVAILABLE = False
    st.warning("⚠️ Advanced AI features limited. Install transformers and faiss for full functionality.")

try:
    from ollama import Client
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Statistical and ML imports
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score

# PDF processing imports (with advanced multimodal support)
try:
    import fitz  # PyMuPDF
    import pdfplumber
    import pytesseract
    from pdf2image import convert_from_bytes
    from PIL import Image
    PDF_PROCESSING_AVAILABLE = True
    
    #Advanced PDF processing with Docling (if available)
    try:
        from docling.document_converter import DocumentConverter
        from docling.datamodel.base_models import InputFormat
        DOCLING_AVAILABLE = True
    except ImportError:
        DOCLING_AVAILABLE = False
    
    #ColPali for visual document understanding (if available)
    try:
        from colpali_engine import ColPali
        from colpali_engine.utils import process_images
        COLPALI_AVAILABLE = True
    except ImportError:
        COLPALI_AVAILABLE = False
        
except ImportError:
    PDF_PROCESSING_AVAILABLE = False
    DOCLING_AVAILABLE = False
    COLPALI_AVAILABLE = False

# Database imports (optional)
try:
    import mysql.connector
    from sqlalchemy import create_engine
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Performance monitoring (optional)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

warnings.filterwarnings('ignore')

# ============================================================================
# 2. 🔧 CONFIGURATION AND INITIALIZATION
# ============================================================================

@dataclass
class AppConfig:
    """Production application configuration"""
    max_file_size_mb: int = 200
    max_pdf_pages: int = 10
    chunk_size: int = 500
    temperature: float = 0.5
    max_retries: int = 3
    cache_ttl: int = 3600
    max_query_length: int = 500
    max_rows_display: int = 10000

CONFIG = AppConfig()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def initialize_session_state():
    """Initialize Streamlit session state variables - Enhanced safety"""
    
    # Define default values
    defaults = {
        'query_history': [],
        'favorite_queries': [],
        'performance_metrics': [],
        'analysis_results': {},
        'chat_history': [],
        'current_df': None,
        'current_pdf_content': None,
        'file_type': None,
        'user_preferences': {'preferred_viz': [], 'common_columns': []},
        'connected': False,
        'selected_query': None,
        'error_count': 0,
        'pdf_question_history': [],
        'db_connected': False,
        'db_tables': [],
        'data_source': 'None',
        'just_loaded_data': False,
        'page_selection': "📊 Data Analysis"
    }
    
    # Initialize only if not already present
    for key, default_value in defaults.items():
        if key not in st.session_state:
            try:
                st.session_state[key] = default_value
            except Exception as e:
                logger.warning(f"Failed to initialize session state key '{key}': {e}")
                # Continue with other keys even if one fails

# ============================================================================
# 3. 🤖 AI MODELS AND SERVICES INITIALIZATION
# ============================================================================

@st.cache_resource
def load_ai_models():
    """Load and cache AI models with comprehensive error handling"""
    models = {
        'embed_model': None,
        'tapas': None,
        'ollama': None,
        'embed_available': False,
        'tapas_available': False,
        'ollama_available': False,
        'ollama_model': None
    }
    
    # Load embedding model
    if AI_MODELS_AVAILABLE:
        try:
            models['embed_model'] = SentenceTransformer("all-MiniLM-L6-v2")
            models['embed_available'] = True
            logger.info("✅ SentenceTransformer loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}")
        
        try:
            models['tapas'] = pipeline("table-question-answering", model="google/tapas-large-finetuned-wtq")
            models['tapas_available'] = True
            logger.info("✅ TAPAS model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load TAPAS: {e}")
    
    # Load Ollama
    if OLLAMA_AVAILABLE:
        try:
            models['ollama'] = Client(host='http://localhost:11434')
            available_models = models['ollama'].list()
            model_names = [model['name'] for model in available_models.get('models', [])]
            
            # Check for available models (in order of preference)
            preferred_models = ['llama3.2', 'llama3.1', 'llama3', 'llama2', 'mistral', 'codellama']
            selected_model = None
            
            for model in preferred_models:
                if any(model in name for name in model_names):
                    selected_model = next(name for name in model_names if model in name)
                    break
            
            if selected_model:
                models['ollama_model'] = selected_model
                models['ollama_available'] = True
                logger.info(f"✅ Ollama connected with model: {selected_model}")
            else:
                logger.warning("⚠️ Ollama connected but no compatible models found")
                
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
    
    return models

# Load models
AI_MODELS = load_ai_models()

# ============================================================================
# 4. 🛠️ UTILITY FUNCTIONS AND DECORATORS
# ============================================================================

def enhanced_error_handling(func):
    """Enhanced error handling decorator with logging"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            error_msg = f"📁 File not found: {str(e)}"
            st.error(error_msg)
            logger.error(error_msg)
            return None
        except pd.errors.EmptyDataError:
            error_msg = "📊 The uploaded file is empty."
            st.error(error_msg)
            logger.error(error_msg)
            return None
        except pd.errors.ParserError as e:
            error_msg = f"📋 Error parsing file: {str(e)}"
            st.error(error_msg)
            logger.error(error_msg)
            return None
        except ValueError as e:
            error_msg = f"⚠️ Value error: {str(e)}"
            st.error(error_msg)
            logger.error(error_msg)
            return None
        except Exception as e:
            error_msg = f"🚨 Unexpected error: {str(e)}"
            st.error(error_msg)
            logger.error(f"Unexpected error in {func.__name__}: {traceback.format_exc()}")
            st.session_state.error_count += 1
            return None
    return wrapper

def track_performance(operation_name):
    """Performance tracking decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            memory_before = psutil.Process().memory_info().rss / 1024 / 1024 if PSUTIL_AVAILABLE else 0
            
            try:
                result = func(*args, **kwargs)
                status = 'success'
            except Exception as e:
                result = None
                status = 'error'
                logger.error(f"Performance tracking - {operation_name} failed: {e}")
            
            end_time = time.time()
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024 if PSUTIL_AVAILABLE else 0
            
            metrics = {
                'operation': operation_name,
                'duration': end_time - start_time,
                'memory_used': memory_after - memory_before,
                'timestamp': datetime.now(),
                'status': status
            }
            
            st.session_state.performance_metrics.append(metrics)
            
            if metrics['duration'] > 2:
                st.info(f"⏱️ {operation_name} completed in {metrics['duration']:.2f} seconds")
            
            return result
        return wrapper
    return decorator

def validate_input(data, max_size_mb=200):
    """Validate input data for security and size"""
    if data is None:
        return False, "No data provided"
    
    if hasattr(data, 'size') and data.size > max_size_mb * 1024 * 1024:
        return False, f"File too large. Maximum size: {max_size_mb}MB"
    
    return True, "Valid"

# ============================================================================
# 5. 🤖 AI AGENT CLASSES
# ============================================================================

class QueryIntentAgent:
    """Advanced AI-powered query intent detection and analysis"""
    def __init__(self, ollama_client=None, embed_model=None, ollama_model=None):
        self.ollama = ollama_client
        self.embed_model = embed_model
        self.ollama_model = ollama_model or 'llama3.2'
        self.fallback_patterns = {
            'extremes': ['maximum', 'max', 'highest', 'largest', 'minimum', 'min', 'lowest', 'smallest'],
            'aggregation': ['average', 'avg', 'mean', 'sum', 'total', 'median', 'count'],
            'counting': ['count of', 'how many', 'number of'],
            'unique': ['unique', 'distinct', 'different'],  # ADD THIS to fallback_patterns
            'visualize': ['show', 'plot', 'chart', 'graph', 'visualize', 'display'],
            'analyze': ['analyze', 'analysis', 'examine', 'study', 'investigate'],
            'compare': ['compare', 'comparison', 'vs', 'versus', 'against', 'difference'],
            'predict': ['predict', 'forecast', 'estimate', 'future', 'model'],
            'cluster': ['cluster', 'group', 'segment', 'similar', 'categorize'],
            'correlate': ['correlation', 'relationship', 'related', 'associated'],
            'summarize': ['summarize', 'summary', 'overview', 'total', 'aggregate'],
            'detect': ['outlier', 'anomaly', 'unusual', 'extreme', 'detect'],
            'trend': ['trend', 'over time', 'time series', 'temporal', 'change'],
            'quality': ['quality', 'missing', 'duplicate', 'clean', 'validate']
        }
    def understand_query_with_context(self, query, df):
        """AI-powered query understanding with enhanced context awareness"""
        
        # Validate input
        if not query or len(query.strip()) == 0:
            return self._create_default_context()
        if len(query) > CONFIG.max_query_length:
            query = query[:CONFIG.max_query_length]
        
        # Step 1: Analyze data structure for context
        data_context = self._analyze_dataframe_context(df)
        
        # Step 2: Use AI agent for intelligent intent detection
        if self.ollama and AI_MODELS['ollama_available']:
            try:
                ai_context = self._ai_powered_intent_detection(query, data_context)
                ai_context = self._enhance_with_entity_extraction(ai_context, query, df)
                return ai_context
            except Exception as e:
                logger.warning(f"AI intent detection failed: {e}")
                return self._fallback_intent_detection(query, df, data_context)
        else:
            return self._fallback_intent_detection(query, df, data_context)
    
    def _create_default_context(self):
        """Create default context for empty or invalid queries"""
        return {
            'intent': 'analyze',
            'entities': [],
            'operations': [],
            'visualization_type': 'auto',
            'analysis_type': 'descriptive',
            'confidence': 0.3,
            'reasoning': 'Default context for empty query',
            'suggested_columns': [],
            'filters_detected': [],
            'aggregation_needed': False,
            'aggregation_function': 'none'
        }
    
    def _analyze_dataframe_context(self, df):
        """Analyze DataFrame to provide AI agent with data context"""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
            
            return {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'numeric_columns': numeric_cols,
                'categorical_columns': categorical_cols,
                'date_columns': date_cols,
                'data_types': df.dtypes.astype(str).to_dict(),
                'sample_values': {
                    col: df[col].value_counts().head(3).to_dict() 
                    for col in categorical_cols[:3]
                },
                'numeric_ranges': {
                    col: {'min': float(df[col].min()), 'max': float(df[col].max())} 
                    for col in numeric_cols[:3]
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing dataframe context: {e}")
            return {
                'total_rows': 0,
                'total_columns': 0,
                'column_names': [],
                'numeric_columns': [],
                'categorical_columns': [],
                'date_columns': []
            }
    
    def _ai_powered_intent_detection(self, query, data_context):
        """Use Ollama to intelligently detect query intent and context"""
        
        ai_prompt = f"""You are an expert data analyst AI. Analyze this user query and determine their intent based on the available data.
        USER QUERY: "{query}"

        AVAILABLE DATA CONTEXT:
        - Dataset size: {data_context['total_rows']} rows, {data_context['total_columns']} columns
        - Numeric columns: {data_context['numeric_columns']}
        - Categorical columns: {data_context['categorical_columns']}
        - Date columns: {data_context['date_columns']}

        Analyze the query and respond with JSON format:
        {{
            "intent": "one of: extremes, aggregation, counting, visualize, analyze, compare, predict, cluster, correlate, summarize, detect, trend, quality",
            "visualization_type": "bar|line|scatter|pie|histogram|box|auto|none",
            "analysis_type": "descriptive|predictive|clustering|correlation|time_series|anomaly_detection|statistical",
            "entities": ["list", "of", "relevant", "column", "names"],
            "operations": ["list", "of", "operations", "like", "min", "max", "mean", "sum"],
            "confidence": 0.95,
            "reasoning": "brief explanation",
            "suggested_columns": ["most", "relevant", "columns"],
            "aggregation_needed": true/false,
            "aggregation_function": "sum|mean|count|max|min|none"
        }}

        IMPORTANT: 
        - If asking for minimum/maximum/average/sum of a column, use intent "extremes" or "aggregation"
        - If asking to show/plot/visualize data, use intent "visualize"
        - Be specific and accurate."""

        try:
            response = self.ollama.generate(
                model=self.ollama_model,
                prompt=ai_prompt,
                options={
                    "temperature": CONFIG.temperature,
                    "top_p": 0.95,
                    "num_predict": 600
                }
            )
            
            parsed_context = self._parse_ai_intent_response(response['response'])
            return self._validate_and_enhance_ai_response(parsed_context, query, data_context)   
        except Exception as e:
            logger.error(f"AI intent detection failed: {e}")
            raise e
    
    def _parse_ai_intent_response(self, ai_response):
        """Parse AI response into structured context"""
        try:
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return {
                    'intent': parsed.get('intent', 'analyze'),
                    'entities': parsed.get('entities', []),
                    'operations': parsed.get('operations', []),
                    'visualization_type': parsed.get('visualization_type', 'auto'),
                    'analysis_type': parsed.get('analysis_type', 'descriptive'),
                    'confidence': float(parsed.get('confidence', 0.8)),
                    'reasoning': parsed.get('reasoning', ''),
                    'suggested_columns': parsed.get('suggested_columns', []),
                    'aggregation_needed': parsed.get('aggregation_needed', False),
                    'aggregation_function': parsed.get('aggregation_function', 'none')
                }
        except json.JSONDecodeError:
            return self._extract_intent_from_text(ai_response)
        return self._create_default_context()
    
    def _extract_intent_from_text(self, ai_response):
        """Extract intent from unstructured AI response with PRIORITY ORDER"""
        response_lower = ai_response.lower()
        
        # PRIORITY 1: Check statistical operations FIRST
        statistical_intents = {
            'extremes': ['minimum', 'maximum', 'min', 'max', 'highest', 'lowest'],
            'aggregation': ['average', 'mean', 'sum', 'total', 'median'],
            'counting': ['count', 'how many', 'number of']
        }
        
        # Check statistical operations first (highest priority)
        for intent, keywords in statistical_intents.items():
            matches = sum(1 for keyword in keywords if keyword in response_lower)
            if matches > 0:
                # Determine specific operation
                operations = []
                aggregation_function = 'none'
                
                if intent == 'extremes':
                    if any(word in response_lower for word in ['minimum', 'min', 'lowest', 'smallest']):
                        operations = ['min']
                        aggregation_function = 'min'
                    elif any(word in response_lower for word in ['maximum', 'max', 'highest', 'largest']):
                        operations = ['max']
                        aggregation_function = 'max'
                elif intent == 'aggregation':
                    if any(word in response_lower for word in ['average', 'mean']):
                        operations = ['mean']
                        aggregation_function = 'mean'
                    elif any(word in response_lower for word in ['sum', 'total']):
                        operations = ['sum']
                        aggregation_function = 'sum'
                    elif 'median' in response_lower:
                        operations = ['median']
                        aggregation_function = 'median'
                elif intent == 'counting':
                    operations = ['count']
                    aggregation_function = 'count'
                
                return {
                    'intent': intent,
                    'entities': [],
                    'operations': operations,
                    'visualization_type': 'none',  # Statistical queries don't need viz
                    'analysis_type': 'statistical',
                    'confidence': min(matches * 0.4, 0.9),
                    'reasoning': f'Statistical operation detected: {intent} with {matches} indicators',
                    'suggested_columns': [],
                    'aggregation_needed': intent in ['aggregation', 'counting'],
                    'aggregation_function': aggregation_function
                }
        
        # PRIORITY 2: Other intents (if no statistical operations found)
        other_intents = {
            'visualize': ['visualize', 'chart', 'plot', 'graph', 'show'],
            'analyze': ['analyze', 'analysis', 'examine'],
            'compare': ['compare', 'comparison', 'versus'],
            'predict': ['predict', 'forecast', 'model'],
            'cluster': ['cluster', 'group', 'segment'],
            'correlate': ['correlation', 'relationship'],
            'summarize': ['summarize', 'summary', 'aggregate'],
            'detect': ['detect', 'outlier', 'anomaly']
        }
        
        detected_intent = 'analyze'
        max_matches = 0
        
        for intent, keywords in other_intents.items():
            matches = sum(1 for keyword in keywords if keyword in response_lower)
            if matches > max_matches:
                max_matches = matches
                detected_intent = intent
        # Set visualization type based on intent
        viz_type = 'auto' if detected_intent == 'visualize' else 'none'
        
        # Set analysis type based on intent
        analysis_type_mapping = {
            'predict': 'predictive',
            'cluster': 'clustering', 
            'correlate': 'correlation',
            'detect': 'anomaly_detection',
            'visualize': 'descriptive'
        }
        analysis_type = analysis_type_mapping.get(detected_intent, 'descriptive')
        
        return {
            'intent': detected_intent,
            'entities': [],
            'operations': [],
            'visualization_type': viz_type,
            'analysis_type': analysis_type,
            'confidence': min(max_matches * 0.3, 0.8),
            'reasoning': f'Extracted from AI text response, found {max_matches} intent indicators',
            'suggested_columns': [],
            'aggregation_needed': False,
            'aggregation_function': 'none'
        }
    
    def _validate_and_enhance_ai_response(self, parsed_context, query, data_context):
        """Validate AI response and enhance with data-specific logic"""
        
        # Validate entities exist in dataframe
        valid_entities = []
        for entity in parsed_context.get('entities', []):
            if entity in data_context['column_names']:
                valid_entities.append(entity)
            else:
                # Try to find close matches
                close_matches = [col for col in data_context['column_names'] 
                               if entity.lower() in col.lower() or col.lower() in entity.lower()]
                valid_entities.extend(close_matches[:1])
        parsed_context['entities'] = list(set(valid_entities))
        
        # Enhance suggested columns based on intent
        if parsed_context['intent'] == 'visualize':
            if not parsed_context['suggested_columns']:
                if data_context['categorical_columns'] and data_context['numeric_columns']:
                    parsed_context['suggested_columns'] = [
                        data_context['categorical_columns'][0],
                        data_context['numeric_columns'][0]
                    ]
        elif parsed_context['intent'] == 'correlate':
            if len(data_context['numeric_columns']) >= 2:
                parsed_context['suggested_columns'] = data_context['numeric_columns'][:2]
        # Adjust confidence based on data availability
        if parsed_context['entities'] and all(entity in data_context['column_names'] for entity in parsed_context['entities']):
            parsed_context['confidence'] = min(parsed_context['confidence'] + 0.2, 1.0)
        return parsed_context
    
    def _enhance_with_entity_extraction(self, context, query, df):
        """Enhance AI context with semantic similarity if embedding model available"""
        
        if self.embed_model and AI_MODELS['embed_available'] and not context['entities']:
            try:
                query_embedding = self.embed_model.encode([query])
                column_descriptions = [f"{col} ({df[col].dtype})" for col in df.columns]
                column_embeddings = self.embed_model.encode(column_descriptions)
                
                similarities = np.dot(query_embedding, column_embeddings.T)[0]
                top_indices = np.argsort(similarities)[-3:][::-1]
                semantic_entities = [df.columns[i] for i in top_indices if similarities[i] > 0.3]
                
                all_entities = list(set(context['entities'] + semantic_entities))
                context['entities'] = all_entities[:5]
                context['suggested_columns'] = all_entities[:3]
                
                if semantic_entities:
                    context['confidence'] = min(context['confidence'] + 0.1, 1.0)
                    context['reasoning'] += f" Enhanced with semantic matching: {semantic_entities}"
            except Exception as e:
                logger.warning(f"Semantic enhancement failed: {e}")
        return context
    
    def _fallback_intent_detection(self, query, df, data_context):
        """Enhanced fallback using pattern matching with PRIORITY ORDER"""
        query_lower = query.lower()
        context = self._create_default_context()
        context['reasoning'] = 'Using fallback pattern matching'
        
        # PRIORITY 1: Statistical operations (check FIRST)
        if any(word in query_lower for word in ['maximum', 'max', 'highest', 'largest']) and not any(word in query_lower for word in ['show', 'plot', 'chart', 'graph', 'visualize', 'display']):
            context['intent'] = 'extremes'
            context['operations'] = ['max']
            context['confidence'] = 0.9
            
        elif any(word in query_lower for word in ['minimum', 'min', 'lowest', 'smallest']) and not any(word in query_lower for word in ['show', 'plot', 'chart', 'graph', 'visualize', 'display']):
            context['intent'] = 'extremes'
            context['operations'] = ['min']
            context['confidence'] = 0.9
            
        elif any(word in query_lower for word in ['average', 'avg', 'mean']) and not any(word in query_lower for word in ['show', 'plot', 'chart', 'graph', 'visualize', 'display']):
            context['intent'] = 'aggregation'
            context['operations'] = ['mean']
            context['confidence'] = 0.9
            
        elif any(word in query_lower for word in ['sum', 'total']) and not any(word in query_lower for word in ['show', 'plot', 'chart', 'graph', 'visualize', 'display']):
            context['intent'] = 'aggregation'
            context['operations'] = ['sum']
            context['confidence'] = 0.9
            
        elif any(word in query_lower for word in ['median', 'middle']) and not any(word in query_lower for word in ['show', 'plot', 'chart', 'graph', 'visualize', 'display']):
            context['intent'] = 'aggregation'
            context['operations'] = ['median']
            context['confidence'] = 0.9
            
        elif any(phrase in query_lower for phrase in ['count of', 'how many', 'number of']) and not any(word in query_lower for word in ['show', 'plot', 'chart', 'graph', 'visualize', 'display']):
            context['intent'] = 'counting'
            context['operations'] = ['count']
            context['confidence'] = 0.9
        
        # PRIORITY 2: Other intents (existing fallback_patterns logic)
        else:
            max_confidence = 0
            for intent, keywords in self.fallback_patterns.items():
                confidence = sum(1 for keyword in keywords if keyword in query_lower)
                if confidence > max_confidence:
                    max_confidence = confidence
                    context['intent'] = intent
                    context['confidence'] = min(confidence * 0.2, 1.0)
        # Entity extraction (unchanged)
        for col in df.columns:
            if col.lower() in query_lower or col.replace('_', ' ') in query_lower:
                context['entities'].append(col)
                context['confidence'] += 0.1
        
        # Analysis type detection (ADD statistical analysis)
        analysis_indicators = {
            'statistical': ['minimum', 'maximum', 'average', 'sum', 'count', 'median', 'min', 'max', 'mean', 'total'],
            'predictive': ['predict', 'model', 'forecast'],
            'clustering': ['cluster', 'group', 'segment'],
            'correlation': ['correlation', 'relationship'],
            'time_series': ['trend', 'time', 'temporal'],
            'anomaly_detection': ['outlier', 'anomaly']
        }
        for analysis_type, indicators in analysis_indicators.items():
            if any(word in query_lower for word in indicators):
                context['analysis_type'] = analysis_type
                break
        # Enhance with data context (unchanged)
        if not context['entities'] and context['intent'] == 'visualize':
            if data_context['categorical_columns'] and data_context['numeric_columns']:
                context['suggested_columns'] = [
                    data_context['categorical_columns'][0],
                    data_context['numeric_columns'][0]
                ]
        return context

class SmartSuggestionAgent:
    """AI-powered dynamic query suggestion generation"""
    
    def __init__(self, embed_model=None):
        self.embed_model = embed_model
    
    def generate_smart_suggestions(self, df):
        """Generate context-aware suggestions based on actual data patterns"""
        suggestions = []
        
        # Analyze data structure
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        
        # Time-based suggestions
        if date_cols and numeric_cols:
            suggestions.append(f"show trend of {numeric_cols[0]} over {date_cols[0]}")
        
        # High-correlation detection
        if len(numeric_cols) >= 2:
            try:
                corr_matrix = df[numeric_cols].corr().abs()
                # Find highest correlation pair (excluding self-correlation)
                corr_values = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_values.append((
                            corr_matrix.columns[i], 
                            corr_matrix.columns[j], 
                            corr_matrix.iloc[i, j]
                        ))
                
                if corr_values:
                    best_pair = max(corr_values, key=lambda x: x[2])
                    if best_pair[2] > 0.3:  # Only suggest if correlation is meaningful
                        suggestions.append(f"analyze relationship between {best_pair[0]} and {best_pair[1]}")
            except Exception:
                pass
        
        # Adaptive suggestions based on user history
        user_prefs = st.session_state.get('user_preferences', {})
        common_columns = user_prefs.get('common_columns', [])
        
        if common_columns:
            for col in common_columns[:2]:
                if col in df.columns:
                    suggestions.insert(0, f"deep dive analysis of {col}")
        
        # Standard suggestions
        if categorical_cols and numeric_cols:
            suggestions.extend([
                f"show {numeric_cols[0]} by {categorical_cols[0]}",
                f"detect outliers in {numeric_cols[0]}",
                f"compare {numeric_cols[0]} across {categorical_cols[0]}"
            ])
        
        # Data quality suggestions
        missing_cols = df.columns[df.isnull().any()].tolist()
        if missing_cols:
            suggestions.append("data quality assessment")
        
        return suggestions[:8]  # Limit to top 8 suggestions

class VisualizationAgent:
    """Robust AI-powered smart visualization creation with comprehensive query parsing"""
    
    def __init__(self, ollama_client=None):
        self.ollama = ollama_client
        
        # Define aggregation keywords for detection
        self.aggregation_keywords = {
            'sum': ['sum', 'total', 'add', 'aggregate'],
            'mean': ['average', 'avg', 'mean'],
            'count': ['count', 'number', 'frequency'],
            'max': ['max', 'maximum', 'highest', 'largest', 'peak'],
            'min': ['min', 'minimum', 'lowest', 'smallest'],
            'median': ['median', 'middle'],
            'std': ['std', 'standard deviation', 'stddev']
        }
        
        # Chart type keywords
        self.chart_keywords = {
            'bar': ['bar', 'column', 'bars', 'columns'],
            'line': ['line', 'trend', 'time', 'over time', 'temporal', 'series'],
            'scatter': ['scatter', 'correlation', 'relationship', 'vs', 'versus'],
            'pie': ['pie', 'donut', 'proportion', 'percentage', 'share'],
            'histogram': ['histogram', 'distribution', 'frequency', 'bins'],
            'box': ['box', 'boxplot', 'quartile', 'outlier', 'whisker'],
            'heatmap': ['heatmap', 'heat map', 'correlation matrix', 'corr']
        }
    
    # =============================================================================
    # MAIN PUBLIC METHOD
    # =============================================================================
    
    def create_intelligent_visualization(self, df, query, intent_context):
        """Main method to create smart visualizations with comprehensive error handling"""
        
        try:
            # Parse the query comprehensively
            query_info = self._parse_query_comprehensive(query, df, intent_context)
            
            if not query_info['success']:
                return None, query_info['error_message']
            
            # Apply any detected filters
            df_filtered = self._apply_comprehensive_filters(df, query_info['filters'])
            
            if df_filtered.empty:
                return None, "No data remaining after applying filters"
            
            # Apply aggregation if needed
            df_viz, final_y_col = self._apply_smart_aggregation(
                df_filtered, 
                query_info['x_column'], 
                query_info['y_column'], 
                query_info['aggregation']
            )
            
            # Limit data for performance
            df_viz = self._intelligent_data_limiting(df_viz, query_info['viz_type'])
            
            # Create the visualization
            fig = self._create_robust_visualization(
                df_viz, 
                query_info['x_column'], 
                final_y_col, 
                query_info['viz_type']
            )
            
            # Apply professional styling
            fig = self._apply_comprehensive_styling(
                fig, 
                query_info['x_column'], 
                final_y_col, 
                query_info['viz_type'], 
                len(df_viz)
            )
            
            # Generate detailed success message
            message = self._generate_success_message(query_info, len(df_filtered), len(df))
            
            return fig, message
            
        except Exception as e:
            logger.error(f"Visualization creation failed: {e}")
            return None, f"Visualization error: {str(e)}"
    
    # =============================================================================
    # QUERY PARSING METHODS
    # =============================================================================
    
    def _parse_query_comprehensive(self, query, df, intent_context):
        """Comprehensive query parsing with multiple fallback strategies"""
        
        query_lower = query.lower().strip()
        
        # Initialize result structure
        result = {
            'success': False,
            'x_column': None,
            'y_column': None,
            'viz_type': 'bar',
            'aggregation': 'none',
            'filters': [],
            'error_message': '',
            'confidence': 0.0
        }
        
        try:
            # Step 1: Detect visualization type
            result['viz_type'] = self._detect_visualization_type(query_lower, intent_context)
            
            # Step 2: Detect aggregation function
            result['aggregation'] = self._detect_aggregation_function(query_lower)
            
            # Step 3: Parse column patterns with multiple strategies
            columns_found = self._parse_column_patterns(query_lower, df)
            
            if not columns_found['success']:
                result['error_message'] = columns_found['error_message']
                return result
            
            result['x_column'] = columns_found['x_column']
            result['y_column'] = columns_found['y_column']
            result['confidence'] = columns_found['confidence']
            
            # Step 4: Detect any filters
            result['filters'] = self._detect_query_filters(query_lower, df)
            
            # Step 5: Validate the configuration
            validation = self._validate_visualization_config(df, result)
            if not validation['valid']:
                result['error_message'] = validation['error_message']
                return result
            
            result['success'] = True
            return result
            
        except Exception as e:
            result['error_message'] = f"Query parsing failed: {str(e)}"
            return result
    
    def _detect_visualization_type(self, query_lower, intent_context):
        """Detect visualization type from query with fallbacks"""
        
        # Check explicit chart type mentions
        for chart_type, keywords in self.chart_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return chart_type
        
        # Check intent context
        viz_type = intent_context.get('visualization_type', 'auto')
        if viz_type != 'auto':
            return viz_type
        
        # Smart defaults based on query patterns
        if any(word in query_lower for word in ['trend', 'over time', 'time series']):
            return 'line'
        elif any(word in query_lower for word in ['relationship', 'correlation', 'vs', 'versus']):
            return 'scatter'
        elif any(word in query_lower for word in ['distribution', 'frequency']):
            return 'histogram'
        elif any(word in query_lower for word in ['proportion', 'percentage', 'share']):
            return 'pie'
        
        return 'bar'  # Safe default
    
    def _detect_aggregation_function(self, query_lower):
        """Detect aggregation function from query"""
        
        for agg_func, keywords in self.aggregation_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return agg_func
        
        # Check for aggregation patterns
        if re.search(r'\b(?:group|grouped)\s+by\b', query_lower):
            return 'sum'  # Default aggregation when grouping
        elif re.search(r'\b(?:aggregated?)\b', query_lower):
            return 'sum'  # Default for explicit aggregation
        
        return 'none'
    
    def _parse_column_patterns(self, query_lower, df):
        """Parse column patterns with multiple strategies and fallbacks"""
        
        result = {
            'success': False,
            'x_column': None,
            'y_column': None,
            'confidence': 0.0,
            'error_message': ''
        }
        
        # Strategy 1: Explicit aggregation patterns
        agg_patterns = [
            r'(?:with\s+)?(?:sum|total|average|mean|count|max|min)\s+(?:of\s+)?(\w+)\s+by\s+(\w+)',
            r'(?:aggregated?|grouped?)\s+(\w+)\s+by\s+(\w+)',
            r'(\w+)\s+(?:grouped?\s+)?by\s+(\w+)',
            r'(?:plot|show|graph|chart)\s+(?:of\s+)?(\w+)\s+by\s+(\w+)',
        ]
        
        for pattern in agg_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                y_hint, x_hint = match.groups()
                
                x_col = self._find_best_column_match(df, x_hint)
                y_col = self._find_best_column_match(df, y_hint)
                
                if x_col and y_col:
                    result['x_column'] = x_col
                    result['y_column'] = y_col
                    result['confidence'] = 0.9
                    result['success'] = True
                    return result
        
        # Strategy 2: Direct column mentions
        mentioned_columns = self._extract_mentioned_columns(query_lower, df)
        
        if len(mentioned_columns) >= 2:
            # Determine which should be x and which should be y
            x_col, y_col = self._determine_axis_assignment(df, mentioned_columns)
            result['x_column'] = x_col
            result['y_column'] = y_col
            result['confidence'] = 0.7
            result['success'] = True
            return result
        elif len(mentioned_columns) == 1:
            # Find a good pairing
            mentioned_col = mentioned_columns[0]
            other_col = self._find_best_pairing(df, mentioned_col)
            
            if other_col:
                if pd.api.types.is_numeric_dtype(df[mentioned_col]):
                    result['x_column'] = other_col
                    result['y_column'] = mentioned_col
                else:
                    result['x_column'] = mentioned_col
                    result['y_column'] = other_col
                
                result['confidence'] = 0.6
                result['success'] = True
                return result
        
        # Strategy 3: Smart defaults based on data types
        smart_pairing = self._get_smart_default_pairing(df)
        if smart_pairing[0] and smart_pairing[1]:
            result['x_column'] = smart_pairing[0]
            result['y_column'] = smart_pairing[1]
            result['confidence'] = 0.4
            result['success'] = True
            return result
        
        # Strategy 4: Last resort - suggest columns
        if len(df.columns) >= 2:
            result['error_message'] = f"Could not identify columns. Try specifying like 'plot {df.columns[1]} by {df.columns[0]}'"
        else:
            result['error_message'] = "Insufficient columns for visualization"
        
        return result
    
    def _detect_query_filters(self, query_lower, df):
        """Detect filter conditions from the query"""
        
        filters = []
        
        filter_patterns = [
            (r'(\w+)\s+(?:equals?|eq|=)\s+(["\']?)([^"\']+)\2', '=='),
            (r'(\w+)\s+(?:is|equals?)\s+(["\']?)([^"\']+)\2', '=='),
            (r'(\w+)\s+(?:greater\s+than|>)\s+(\d+(?:\.\d+)?)', '>'),
            (r'(\w+)\s+(?:less\s+than|<)\s+(\d+(?:\.\d+)?)', '<'),
            (r'(\w+)\s+(?:contains?|includes?)\s+(["\']?)([^"\']+)\2', 'contains'),
            (r'where\s+(\w+)\s*=\s*(["\']?)([^"\']+)\2', '=='),
        ]
        
        for pattern, operator in filter_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 2:
                    col_hint = groups[0]
                    value = groups[-1]  # Last group is always the value
                    
                    # Find matching column
                    actual_col = self._find_best_column_match(df, col_hint)
                    if actual_col:
                        filters.append({
                            'column': actual_col,
                            'operator': operator,
                            'value': value
                        })
        
        return filters
    
    def _validate_visualization_config(self, df, config):
        """Validate the visualization configuration"""
        
        x_col = config['x_column']
        y_col = config['y_column']
        
        if not x_col or not y_col:
            return {'valid': False, 'error_message': 'Could not identify both x and y columns'}
        
        if x_col not in df.columns:
            return {'valid': False, 'error_message': f'Column {x_col} not found in dataset'}
        
        if y_col not in df.columns:
            return {'valid': False, 'error_message': f'Column {y_col} not found in dataset'}
        
        # Check if aggregation makes sense
        if config['aggregation'] != 'none' and not pd.api.types.is_numeric_dtype(df[y_col]):
            if config['aggregation'] != 'count':
                return {'valid': False, 'error_message': f'Cannot apply {config["aggregation"]} to non-numeric column {y_col}'}
        
        return {'valid': True, 'error_message': ''}
    
    # =============================================================================
    # COLUMN DETECTION HELPER METHODS
    # =============================================================================
    
    def _find_best_column_match(self, df, column_hint):
        """Find the best matching column for a given hint"""
        
        if not column_hint:
            return None
        
        column_hint = column_hint.strip().lower()
        
        # Direct exact match
        for col in df.columns:
            if col.lower() == column_hint:
                return col
        
        # Partial matches with different strategies
        matches = []
        
        for col in df.columns:
            col_lower = col.lower()
            score = 0
            
            # Exact substring match
            if column_hint in col_lower or col_lower in column_hint:
                score += 3
            
            # Match without underscores/spaces
            hint_clean = column_hint.replace('_', '').replace(' ', '')
            col_clean = col_lower.replace('_', '').replace(' ', '')
            if hint_clean in col_clean or col_clean in hint_clean:
                score += 2
            
            # Word-by-word matching
            hint_words = column_hint.replace('_', ' ').split()
            col_words = col_lower.replace('_', ' ').split()
            common_words = set(hint_words) & set(col_words)
            if common_words:
                score += len(common_words)
            
            if score > 0:
                matches.append((col, score))
        
        # Return best match
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0][0]
        
        return None
    
    def _extract_mentioned_columns(self, query_lower, df):
        """Extract all columns mentioned in the query"""
        
        mentioned = []
        
        for col in df.columns:
            # Create variations of column names
            variations = [
                col.lower(),
                col.lower().replace('_', ' '),
                col.lower().replace('_', ''),
                col.lower().replace(' ', ''),
            ]
            
            for variation in variations:
                if len(variation) > 2 and variation in query_lower:
                    mentioned.append(col)
                    break
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(mentioned))
    
    def _determine_axis_assignment(self, df, columns):
        """Determine which column should be x-axis and which should be y-axis"""
        
        if len(columns) < 2:
            return None, None
        
        # Strategy: categorical columns prefer x-axis, numeric prefer y-axis
        categorical_cols = []
        numeric_cols = []
        
        for col in columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                numeric_cols.append(col)
            else:
                categorical_cols.append(col)
        
        # If we have both types, use categorical for x and numeric for y
        if categorical_cols and numeric_cols:
            return categorical_cols[0], numeric_cols[0]
        
        # If all same type, use first two
        return columns[0], columns[1]
    
    def _find_best_pairing(self, df, target_col):
        """Find the best column to pair with the target column"""
        
        if pd.api.types.is_numeric_dtype(df[target_col]):
            # Find categorical column with reasonable cardinality
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            for col in cat_cols:
                if col != target_col and 2 <= df[col].nunique() <= 50:
                    return col
            
            # Fallback to another numeric column
            num_cols = df.select_dtypes(include=[np.number]).columns
            for col in num_cols:
                if col != target_col:
                    return col
        else:
            # Find a numeric column
            num_cols = df.select_dtypes(include=[np.number]).columns
            if len(num_cols) > 0:
                return num_cols[0]
        
        return None
    
    def _get_smart_default_pairing(self, df):
        """Get smart default column pairing based on data analysis"""
        
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        
        # Priority 1: Date + Numeric (time series)
        if date_cols and num_cols:
            return date_cols[0], num_cols[0]
        
        # Priority 2: Categorical + Numeric (grouped analysis)
        if cat_cols and num_cols:
            # Choose categorical with reasonable cardinality
            for cat_col in cat_cols:
                if 2 <= df[cat_col].nunique() <= 50:
                    return cat_col, num_cols[0]
            # If all have high cardinality, use first anyway
            return cat_cols[0], num_cols[0]
        
        # Priority 3: Two numeric columns
        if len(num_cols) >= 2:
            return num_cols[0], num_cols[1]
        
        # Priority 4: Two categorical columns
        if len(cat_cols) >= 2:
            return cat_cols[0], cat_cols[1]
        
        return None, None
    
    # =============================================================================
    # DATA PROCESSING METHODS
    # =============================================================================
    
    def _apply_comprehensive_filters(self, df, filters):
        """Apply detected filters with comprehensive error handling"""
        
        df_filtered = df.copy()
        
        for filter_info in filters:
            try:
                col = filter_info['column']
                operator = filter_info['operator']
                value = filter_info['value']
                
                if col not in df.columns:
                    continue
                
                if operator == '==':
                    if pd.api.types.is_numeric_dtype(df[col]):
                        try:
                            numeric_value = float(value)
                            df_filtered = df_filtered[df_filtered[col] == numeric_value]
                        except ValueError:
                            df_filtered = df_filtered[df_filtered[col].astype(str) == str(value)]
                    else:
                        df_filtered = df_filtered[df_filtered[col].astype(str).str.lower() == str(value).lower()]
                
                elif operator == '>':
                    df_filtered = df_filtered[df_filtered[col] > float(value)]
                elif operator == '<':
                    df_filtered = df_filtered[df_filtered[col] < float(value)]
                elif operator == 'contains':
                    df_filtered = df_filtered[df_filtered[col].astype(str).str.contains(str(value), case=False, na=False)]
                
            except Exception as e:
                logger.warning(f"Filter application failed for {filter_info}: {e}")
                continue
        
        return df_filtered
    
    def _apply_smart_aggregation(self, df, x_col, y_col, aggregation):
        """Apply aggregation with smart handling of different scenarios"""
        
        if aggregation == 'none':
            return df, y_col
        
        try:
            if aggregation == 'count':
                # Count works on any column
                df_agg = df.groupby(x_col).size().reset_index(name=f'{y_col}_count')
                return df_agg, f'{y_col}_count'
            
            elif not pd.api.types.is_numeric_dtype(df[y_col]):
                # For non-numeric columns, default to count
                df_agg = df.groupby(x_col).size().reset_index(name=f'{y_col}_count')
                return df_agg, f'{y_col}_count'
            
            else:
                # Apply numeric aggregation
                agg_funcs = {
                    'sum': 'sum',
                    'mean': 'mean',
                    'max': 'max',
                    'min': 'min',
                    'median': 'median',
                    'std': 'std'
                }
                
                if aggregation in agg_funcs:
                    df_agg = df.groupby(x_col)[y_col].agg(agg_funcs[aggregation]).reset_index()
                    return df_agg, y_col
                else:
                    # Default to sum for unknown aggregation
                    df_agg = df.groupby(x_col)[y_col].sum().reset_index()
                    return df_agg, y_col
        
        except Exception as e:
            logger.warning(f"Aggregation failed: {e}")
            return df, y_col
    
    def _intelligent_data_limiting(self, df, viz_type, max_points=50):
        """Intelligently limit data points based on visualization type"""
        
        if len(df) <= max_points:
            return df
        
        try:
            if viz_type in ['bar', 'pie']:
                # For bar/pie charts, keep top values by y-column if numeric
                y_col = df.columns[-1]  # Assume last column is y
                if pd.api.types.is_numeric_dtype(df[y_col]):
                    return df.nlargest(max_points, y_col)
                else:
                    return df.head(max_points)
            
            elif viz_type == 'line':
                # For line charts, take evenly spaced points
                step = max(1, len(df) // max_points)
                return df.iloc[::step].head(max_points)
            
            elif viz_type == 'scatter':
                # For scatter plots, random sample
                return df.sample(n=max_points, random_state=42)
            
            else:
                return df.head(max_points)
                
        except Exception as e:
            logger.warning(f"Data limiting failed: {e}")
            return df.head(max_points)
    
    # =============================================================================
    # VISUALIZATION CREATION METHODS
    # =============================================================================
    
    def _create_robust_visualization(self, df, x_col, y_col, viz_type):
        """Create robust visualization with comprehensive error handling"""
        
        try:
            # Handle single column case
            if x_col == y_col:
                return self._create_single_column_viz(df, x_col, viz_type)
            
            # Create visualization based on type
            if viz_type == 'bar':
                fig = px.bar(df, x=x_col, y=y_col)
            elif viz_type == 'line':
                df_sorted = df.sort_values(x_col)
                fig = px.line(df_sorted, x=x_col, y=y_col, markers=True)
            elif viz_type == 'scatter':
                fig = px.scatter(df, x=x_col, y=y_col)
            elif viz_type == 'pie':
                if pd.api.types.is_numeric_dtype(df[y_col]):
                    fig = px.pie(df, names=x_col, values=y_col)
                else:
                    # Create pie from value counts
                    value_counts = df[x_col].value_counts()
                    fig = px.pie(values=value_counts.values, names=value_counts.index)
            elif viz_type == 'histogram':
                fig = px.histogram(df, x=y_col if pd.api.types.is_numeric_dtype(df[y_col]) else x_col)
            elif viz_type == 'box':
                fig = px.box(df, x=x_col, y=y_col)
            elif viz_type == 'heatmap':
                # Create correlation heatmap if both columns are numeric
                if pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if len(numeric_cols) > 1:
                        corr_matrix = df[numeric_cols].corr()
                        fig = px.imshow(corr_matrix, text_auto=True, aspect="auto")
                    else:
                        fig = px.bar(df, x=x_col, y=y_col)  # Fallback
                else:
                    fig = px.bar(df, x=x_col, y=y_col)  # Fallback
            else:
                # Default fallback
                fig = px.bar(df, x=x_col, y=y_col)
            
            return fig
            
        except Exception as e:
            logger.error(f"Chart creation failed: {e}")
            # Ultimate fallback - simple bar chart
            try:
                return px.bar(df, x=x_col, y=y_col)
            except:
                return px.bar(x=['Error'], y=[1], title="Chart Creation Failed")
    
    def _create_single_column_viz(self, df, col, viz_type):
        """Create visualization for single column"""
        
        if pd.api.types.is_numeric_dtype(df[col]):
            return px.histogram(df, x=col, title=f"Distribution of {col}")
        else:
            value_counts = df[col].value_counts().head(20)
            return px.bar(x=value_counts.index, y=value_counts.values, 
                         title=f"Value Counts for {col}")
    
    # =============================================================================
    # STYLING AND FORMATTING METHODS
    # =============================================================================
    
    def _apply_comprehensive_styling(self, fig, x_col, y_col, viz_type, data_count):
        """Apply comprehensive professional styling"""
        
        # Clean column names for display
        x_title = x_col.replace('_', ' ').title() if x_col else 'X'
        y_title = y_col.replace('_', ' ').title() if y_col else 'Y'
        
        # Generate appropriate title
        title = self._generate_dynamic_title(x_title, y_title, viz_type)
        
        # Apply layout styling
        fig.update_layout(
            height=600,
            margin=dict(l=80, r=80, t=120, b=100),
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#2c3e50', 'family': 'Arial, sans-serif'}
            },
            xaxis={
                'title': x_title,
                'title_font': {'size': 14, 'color': '#34495e'},
                'tickfont': {'size': 11, 'color': '#000000'},
                'tickangle': -45 if self._should_rotate_labels(fig, data_count) else 0
            },
            yaxis={
                'title': y_title,
                'title_font': {'size': 14, 'color': '#34495e'},
                'tickfont': {'size': 11, 'color': '#000000'}
            },
            plot_bgcolor='rgba(248, 249, 250, 0.8)',
            paper_bgcolor='white',
            font={'family': 'Arial, sans-serif', 'size': 12},
            showlegend=viz_type in ['pie', 'scatter'] or data_count > 20
        )
        
        # Add data count annotation
        if data_count > 0:
            fig.add_annotation(
                text=f"📊 {data_count:,} data points",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=10, color="#05838b"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#bdc3c7",
                borderwidth=1
            )
        
        # Chart-specific styling
        if viz_type == 'bar':
            fig.update_traces(
                marker_color='#3498db',
                texttemplate='%{y:,.0f}' if data_count <= 20 else None,
                textposition='outside' if data_count <= 20 else None,
                textfont={'color': '#000000', 'size': 12}
            )
        elif viz_type == 'line':
            fig.update_traces(
                line=dict(width=3, color='#3498db'),
                marker=dict(size=6, color='#3498db')
            )
        elif viz_type == 'scatter':
            fig.update_traces(marker=dict(color='#3498db', size=8))
        elif viz_type == 'pie':
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont={'size': 11},
                marker=dict(line=dict(color='white', width=2))
            )
        else:
            fig.update_traces(marker_color='#3498db')
        
        return fig
    
    def _generate_dynamic_title(self, x_title, y_title, viz_type):
        """Generate dynamic, descriptive chart title"""
        
        icons = {
            'bar': '📊',
            'line': '📈',
            'scatter': '🔍',
            'pie': '🥧',
            'histogram': '📊',
            'box': '📦',
            'heatmap': '🔥'
        }
        
        icon = icons.get(viz_type, '📊')
        
        if viz_type == 'bar':
            return f"{icon} {y_title} by {x_title}"
        elif viz_type == 'line':
            return f"{icon} {y_title} Trend over {x_title}"
        elif viz_type == 'scatter':
            return f"{icon} {y_title} vs {x_title} Relationship"
        elif viz_type == 'pie':
            return f"{icon} {y_title} Distribution by {x_title}"
        elif viz_type == 'histogram':
            return f"{icon} Distribution of {y_title}"
        elif viz_type == 'box':
            return f"{icon} {y_title} Distribution by {x_title}"
        elif viz_type == 'heatmap':
            return f"{icon} Correlation Heatmap"
        else:
            return f"{icon} {y_title} Analysis"
    
    def _should_rotate_labels(self, fig, data_count):
        """Determine if x-axis labels should be rotated"""
        
        try:
            # Rotate if there are many data points or long labels expected
            return data_count > 10
        except Exception:
            return False
    
    # =============================================================================
    # MESSAGE GENERATION METHODS
    # =============================================================================
    
    def _generate_success_message(self, query_info, filtered_count, original_count):
        """Generate detailed success message"""
        
        x_col = query_info['x_column']
        y_col = query_info['y_column']
        viz_type = query_info['viz_type']
        aggregation = query_info['aggregation']
        
        # Base message
        if aggregation != 'none':
            message = f"Created {viz_type} chart showing {aggregation} of {y_col} by {x_col}"
        else:
            message = f"Created {viz_type} visualization of {y_col} by {x_col}"
        
        # Add data info
        if filtered_count != original_count:
            message += f" (filtered: {filtered_count:,} of {original_count:,} records)"
        else:
            message += f" ({filtered_count:,} records)"
        
        # Add confidence info
        if query_info['confidence'] < 0.6:
            message += " - Low confidence in column detection"
        
        return message

class PredictiveModelingAgent:
    """Advanced AI-powered predictive modeling with comprehensive statistics"""
    
    def __init__(self, ollama_client=None, ollama_model=None):
        self.ollama = ollama_client
        self.ollama_model = ollama_model or 'llama3.2'
        
    def create_intelligent_prediction_model(self, df, target_column, feature_columns=None, model_type='auto'):
        """Create comprehensive predictive model with full statistics"""
        
        # Validate target column
        if target_column not in df.columns:
            return None, f"Target column '{target_column}' not found"
        
        # Auto-detect model type if needed
        if model_type == 'auto':
            model_type = self._determine_model_type(df, target_column)
        
        # Smart feature selection
        if feature_columns is None:
            feature_columns = self._intelligent_feature_selection(df, target_column)
        
        if len(feature_columns) < 1:
            return None, f"No suitable features found to predict {target_column}"
        
        # Build and evaluate model
        try:
            model_result = self._build_comprehensive_model(df, target_column, feature_columns, model_type)
            
            # Generate AI insights if available
            if self.ollama and AI_MODELS.get('ollama_available', False):
                insights = self._generate_model_insights(model_result, target_column, feature_columns)
                model_result['ai_insights'] = insights
            
            return model_result, f"Successfully created {model_type} model for {target_column}"
            
        except Exception as e:
            logger.error(f"Model creation failed: {e}")
            return None, f"Model creation failed: {str(e)}"
    
    def _determine_model_type(self, df, target_column):
        """Automatically determine if classification or regression"""
        
        target_data = df[target_column].dropna()
        
        # Check if target is numeric
        if pd.api.types.is_numeric_dtype(target_data):
            unique_values = target_data.nunique()
            total_values = len(target_data)
            
            # If few unique values relative to total, treat as classification
            if unique_values <= 10 and unique_values / total_values < 0.05:
                return 'classification'
            else:
                return 'regression'
        else:
            return 'classification'
    
    def _intelligent_feature_selection(self, df, target_column):
        """Smart feature selection based on data analysis"""
        
        # Get all potential features (exclude target)
        all_features = [col for col in df.columns if col != target_column]
        
        # Remove non-predictive columns
        excluded_patterns = ['id', 'index', 'date', 'time', 'created', 'updated', 'timestamp']
        features = []
        
        for col in all_features:
            # Skip ID-like columns
            if any(pattern in col.lower() for pattern in excluded_patterns):
                continue
                
            # Skip high-cardinality text columns
            if df[col].dtype == 'object' and df[col].nunique() > len(df) * 0.8:
                continue
                
            features.append(col)
        
        # Correlation-based feature selection for numeric target
        if pd.api.types.is_numeric_dtype(df[target_column]):
            features = self._correlation_based_selection(df, target_column, features)
        
        return features[:15]  # Limit to top 15 features
    
    def _correlation_based_selection(self, df, target_column, features):
        """Select features based on correlation with target"""
        
        numeric_features = [col for col in features if pd.api.types.is_numeric_dtype(df[col])]
        
        if len(numeric_features) == 0:
            return features
        
        # Calculate correlations
        correlations = []
        for feature in numeric_features:
            try:
                corr = df[feature].corr(df[target_column])
                if not pd.isna(corr):
                    correlations.append((feature, abs(corr)))
            except:
                continue
        
        # Sort by correlation strength
        correlations.sort(key=lambda x: x[1], reverse=True)
        
        # Keep top correlated features + non-numeric features
        top_numeric = [feat for feat, corr in correlations[:10]]
        non_numeric = [col for col in features if col not in numeric_features]
        
        return top_numeric + non_numeric[:5]
    
    def _build_comprehensive_model(self, df, target_column, features, model_type):
        """Build comprehensive predictive model with full statistics"""
        
        # Prepare data
        df_model = df[features + [target_column]].copy()
        
        # Handle missing values
        initial_rows = len(df_model)
        df_model = df_model.dropna()
        final_rows = len(df_model)
        
        if final_rows < 10:
            raise Exception('Insufficient data for modeling (need at least 10 rows after cleaning)')
        
        # Encode categorical variables
        encoders = {}
        feature_info = {}
        
        for col in features:
            feature_info[col] = {
                'original_type': str(df_model[col].dtype),
                'unique_values': int(df_model[col].nunique()),
                'missing_count': int(df[col].isnull().sum())
            }
            
            if df_model[col].dtype == 'object':
                try:
                    le = LabelEncoder()
                    df_model[col] = le.fit_transform(df_model[col].astype(str))
                    encoders[col] = le
                    feature_info[col]['encoded'] = True
                    feature_info[col]['categories'] = le.classes_.tolist()
                except:
                    continue
            else:
                feature_info[col]['encoded'] = False
        
        # Encode target if classification
        target_encoder = None
        target_info = {
            'original_type': str(df_model[target_column].dtype),
            'unique_values': int(df_model[target_column].nunique())
        }
        
        if model_type == 'classification' and df_model[target_column].dtype == 'object':
            target_encoder = LabelEncoder()
            df_model[target_column] = target_encoder.fit_transform(df_model[target_column])
            target_info['encoded'] = True
            target_info['categories'] = target_encoder.classes_.tolist()
        else:
            target_info['encoded'] = False
        
        # Split data with stratification for classification
        X = df_model[features]
        y = df_model[target_column]
        
        test_size = min(0.3, max(0.15, 20 / len(X)))
        
        if model_type == 'classification' and len(y.unique()) > 1:
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=42, stratify=y
                )
            except:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=42
                )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
        
        # Train model
        if model_type == 'regression':
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            model.fit(X_train, y_train)
            
            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Comprehensive metrics
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            train_mae = np.mean(np.abs(y_train - y_pred_train))
            test_mae = np.mean(np.abs(y_test - y_pred_test))
            
            # Calculate additional metrics
            residuals = y_test - y_pred_test
            mean_residual = np.mean(residuals)
            std_residual = np.std(residuals)
            
            metrics = {
                'model_type': 'regression',
                'train_r2': float(train_r2),
                'test_r2': float(test_r2),
                'train_rmse': float(train_rmse),
                'test_rmse': float(test_rmse),
                'train_mae': float(train_mae),
                'test_mae': float(test_mae),
                'mean_residual': float(mean_residual),
                'std_residual': float(std_residual),
                'overfitting': train_r2 - test_r2 > 0.15,
                'train_size': len(X_train),
                'test_size': len(X_test)
            }
            
        else:  # classification
            model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
            model.fit(X_train, y_train)
            
            # Predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
            
            # Comprehensive metrics
            train_acc = accuracy_score(y_train, y_pred_train)
            test_acc = accuracy_score(y_test, y_pred_test)
            
            # Additional classification metrics
            from sklearn.metrics import precision_score, recall_score, f1_score, classification_report
            
            try:
                precision = precision_score(y_test, y_pred_test, average='weighted', zero_division=0)
                recall = recall_score(y_test, y_pred_test, average='weighted', zero_division=0)
                f1 = f1_score(y_test, y_pred_test, average='weighted', zero_division=0)
                class_report = classification_report(y_test, y_pred_test, output_dict=True, zero_division=0)
            except:
                precision = recall = f1 = 0.0
                class_report = {}
            
            metrics = {
                'model_type': 'classification',
                'train_accuracy': float(train_acc),
                'test_accuracy': float(test_acc),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'classification_report': class_report,
                'overfitting': train_acc - test_acc > 0.15,
                'train_size': len(X_train),
                'test_size': len(X_test)
            }
        
        # Feature importance analysis
        feature_importance = pd.DataFrame({
            'feature': features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Add feature information
        feature_importance['feature_type'] = feature_importance['feature'].map(
            lambda x: feature_info[x]['original_type']
        )
        feature_importance['unique_values'] = feature_importance['feature'].map(
            lambda x: feature_info[x]['unique_values']
        )
        
        # Predictions dataframe with comprehensive info
        predictions_df = pd.DataFrame({
            'actual': y_test,
            'predicted': y_pred_test
        })
        
        if model_type == 'regression':
            predictions_df['residuals'] = predictions_df['actual'] - predictions_df['predicted']
            predictions_df['abs_error'] = np.abs(predictions_df['residuals'])
            predictions_df['pct_error'] = (predictions_df['residuals'] / predictions_df['actual'] * 100).fillna(0)
        else:
            predictions_df['correct'] = predictions_df['actual'] == predictions_df['predicted']
            if y_pred_proba is not None:
                max_proba = np.max(y_pred_proba, axis=1)
                predictions_df['confidence'] = max_proba
        
        # Model summary
        model_summary = {
            'total_features': len(features),
            'features_used': features,
            'target_column': target_column,
            'model_type': model_type,
            'data_preprocessing': {
                'initial_rows': initial_rows,
                'final_rows': final_rows,
                'rows_dropped': initial_rows - final_rows,
                'categorical_features_encoded': len(encoders),
                'train_test_split': f"{(1-test_size)*100:.0f}%/{test_size*100:.0f}%"
            }
        }
        
        return {
            'model': model,
            'metrics': metrics,
            'feature_importance': feature_importance,
            'feature_info': feature_info,
            'target_info': target_info,
            'predictions': predictions_df,
            'encoders': encoders,
            'target_encoder': target_encoder,
            'model_summary': model_summary,
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test
        }
    
    def _generate_model_insights(self, model_result, target_column, features):
        """Generate AI insights about the prediction model"""
        
        if 'error' in model_result:
            return "Model building failed - insufficient data"
        
        metrics = model_result['metrics']
        feature_importance = model_result['feature_importance']
        
        top_features = feature_importance.head(3)['feature'].tolist()
        model_type = metrics['model_type']
        
        if model_type == 'regression':
            performance = metrics['test_r2']
            performance_desc = f"R² score of {performance:.3f}"
        else:
            performance = metrics['test_accuracy'] 
            performance_desc = f"accuracy of {performance:.3f}"
        
        ai_prompt = f"""Generate business insights about this predictive model:

        Target Variable: {target_column}
        Model Type: {model_type}
        Performance: {performance_desc}
        Top Predictive Features: {', '.join(top_features)}
        Overfitting: {'Yes' if metrics.get('overfitting', False) else 'No'}
        Training Size: {metrics.get('train_size', 'N/A')} samples

        Provide 4-5 key insights about:
        1. Model performance interpretation
        2. Most important predictive factors
        3. Business recommendations
        4. Model reliability and limitations
        5. Actionable next steps

        Keep insights practical and business-focused. Be concise but comprehensive."""

        try:
            response = self.ollama.generate(
                model=self.ollama_model,
                prompt=ai_prompt,
                options={"temperature": 0.5}
            )
            return response['response']
        except Exception as e:
            logger.warning(f"AI insights generation failed: {e}")
            return f"Model achieves {performance_desc}. Top predictive factors: {', '.join(top_features)}. {'Overfitting detected - consider regularization.' if metrics.get('overfitting', False) else 'Model shows good generalization.'}", f"Created {viz_type} visualization with {len(df)} records"
        except Exception as e:
            logger.error(f"Visualization creation failed: {e}")
            return None, f"Error creating visualization: {str(e)}"
    
    def _auto_detect_viz_type(self, df, query, intent_context):
        """Auto-detect best visualization type"""
        query_lower = query.lower()
        
        # Explicit chart type mentions
        chart_indicators = {
            'bar': ['bar', 'column'],
            'line': ['line', 'trend', 'time'],
            'scatter': ['scatter', 'correlation'],
            'pie': ['pie', 'donut'],
            'histogram': ['histogram', 'distribution'],
            'box': ['box', 'boxplot']
        }
        
        for chart_type, indicators in chart_indicators.items():
            if any(word in query_lower for word in indicators):
                return chart_type
        
        # Smart default based on data types
        suggested_cols = intent_context.get('suggested_columns', [])
        if len(suggested_cols) >= 2:
            col1_type = df[suggested_cols[0]].dtype
            col2_type = df[suggested_cols[1]].dtype
            
            if pd.api.types.is_numeric_dtype(col1_type) and pd.api.types.is_numeric_dtype(col2_type):
                return 'scatter'
            elif pd.api.types.is_categorical_dtype(col1_type) or col1_type == 'object':
                return 'bar'
        
        return 'bar'  # Default
    
    def _get_visualization_columns(self, df, query, suggested_cols):
        """Get appropriate columns for visualization"""
        
        if len(suggested_cols) >= 2:
            return suggested_cols[0], suggested_cols[1]
        
        # Find columns mentioned in query
        mentioned_cols = []
        for col in df.columns:
            col_variations = [col.lower(), col.lower().replace('_', ' ')]
            if any(var in query.lower() for var in col_variations):
                mentioned_cols.append(col)
        
        if len(mentioned_cols) >= 2:
            return mentioned_cols[0], mentioned_cols[1]
        elif len(mentioned_cols) == 1:
            if pd.api.types.is_numeric_dtype(df[mentioned_cols[0]]):
                cat_cols = df.select_dtypes(include=['object']).columns
                if len(cat_cols) > 0:
                    return cat_cols[0], mentioned_cols[0]
            else:
                num_cols = df.select_dtypes(include=[np.number]).columns
                if len(num_cols) > 0:
                    return mentioned_cols[0], num_cols[0]
        
        # Fallback
        cat_cols = df.select_dtypes(include=['object']).columns
        num_cols = df.select_dtypes(include=[np.number]).columns
        
        x_col = cat_cols[0] if len(cat_cols) > 0 else None
        y_col = num_cols[0] if len(num_cols) > 0 else None
        
        return x_col, y_col
    
    def _create_plotly_visualization(self, df, x_col, y_col, viz_type, aggregation, query):
        """Create the actual Plotly visualization with professional styling"""
        
        # Apply aggregation if needed
        if aggregation != 'none' and pd.api.types.is_numeric_dtype(df[y_col]):
            if aggregation == 'sum':
                df_plot = df.groupby(x_col)[y_col].sum().reset_index()
            elif aggregation == 'mean':
                df_plot = df.groupby(x_col)[y_col].mean().reset_index()
            elif aggregation == 'count':
                df_plot = df.groupby(x_col)[y_col].count().reset_index()
            else:
                df_plot = df.copy()
        else:
            df_plot = df.copy()
        
        # Limit data for performance
        if len(df_plot) > 50:
            df_plot = df_plot.head(50)
        
        # Create visualization based on type
        if viz_type == 'bar':
            fig = px.bar(df_plot, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
            fig.update_traces(marker_color='#3498db')
            
        elif viz_type == 'line':
            fig = px.line(df_plot.sort_values(x_col), x=x_col, y=y_col, 
                        title=f"{y_col} trend over {x_col}", markers=True)
            fig.update_traces(line_color='#3498db')
            
        elif viz_type == 'scatter':
            fig = px.scatter(df_plot, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
            fig.update_traces(marker_color='#3498db')
            
        elif viz_type == 'pie':
            if pd.api.types.is_numeric_dtype(df_plot[y_col]):
                fig = px.pie(df_plot, names=x_col, values=y_col, 
                           title=f"{y_col} distribution by {x_col}")
            else:
                value_counts = df_plot[x_col].value_counts()
                fig = px.pie(values=value_counts.values, names=value_counts.index,
                           title=f"Distribution of {x_col}")
                
        elif viz_type == 'histogram':
            fig = px.histogram(df_plot, x=y_col, title=f"Distribution of {y_col}")
            fig.update_traces(marker_color='#3498db')
            
        elif viz_type == 'box':
            fig = px.box(df_plot, x=x_col, y=y_col, title=f"{y_col} distribution by {x_col}")
            fig.update_traces(marker_color='#3498db')
            
        else:
            fig = px.bar(df_plot, x=x_col, y=y_col)
            fig.update_traces(marker_color='#3498db')
        
        # Apply professional styling
        fig.update_layout(
            height=600,
            margin=dict(l=80, r=80, t=120, b=100),
            title={
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'family': 'Arial, sans-serif'}
        )
        
        return fig

class SimplifiedPredictiveModelingAgent:
    """Simplified predictive modeling based on your reference code - MORE RELIABLE"""

    def __init__(self):
        pass

    def create_predictive_model(self, df, target_column, feature_columns=None):
        """Create and evaluate a predictive model - BASED ON YOUR REFERENCE"""
        
        if target_column not in df.columns:
            return None, f"Target column '{target_column}' not found"
        
        # Determine if this is classification or regression
        target_data = df[target_column].dropna()
        is_classification = False
        
        if not pd.api.types.is_numeric_dtype(target_data):
            is_classification = True
        elif target_data.nunique() <= 10 and target_data.nunique() / len(target_data) < 0.05:
            is_classification = True
        
        # Prepare features
        if feature_columns is None:
            # Get all numeric columns
            feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            if target_column in feature_columns:
                feature_columns.remove(target_column)
            
            # Add categorical columns with low cardinality
            cat_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
            for col in cat_columns:
                if df[col].nunique() < 20:  # Low cardinality categorical
                    feature_columns.append(col)
        
        if len(feature_columns) == 0:
            return None, "No suitable feature columns found"
        
        # Clean data
        df_clean = df[[target_column] + feature_columns].dropna()
        
        if len(df_clean) < 10:
            return None, "Not enough data for modeling (need at least 10 rows)"
        
        # Handle categorical variables
        df_encoded = df_clean.copy()
        label_encoders = {}
        
        for col in feature_columns:
            if df_encoded[col].dtype == 'object' or pd.api.types.is_categorical_dtype(df_encoded[col]):
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                label_encoders[col] = le
        
        # Handle target variable for classification
        target_encoder = None
        if is_classification and (df_encoded[target_column].dtype == 'object' or pd.api.types.is_categorical_dtype(df_encoded[target_column])):
            target_encoder = LabelEncoder()
            df_encoded[target_column] = target_encoder.fit_transform(df_encoded[target_column].astype(str))
        
        # Prepare features and target
        X = df_encoded[feature_columns]
        y = df_encoded[target_column]
        
        # Split data
        test_size = min(0.3, max(0.1, 20 / len(X)))  # Adaptive test size
        
        if is_classification and len(y.unique()) > 1:
            try:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=42, stratify=y
                )
            except:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=42
                )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
        
        # Train model
        if is_classification:
            model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Calculate metrics
            train_acc = accuracy_score(y_train, y_pred_train)
            test_acc = accuracy_score(y_test, y_pred_test)
            
            # Additional metrics
            try:
                from sklearn.metrics import precision_score, recall_score, f1_score
                precision = precision_score(y_test, y_pred_test, average='weighted', zero_division=0)
                recall = recall_score(y_test, y_pred_test, average='weighted', zero_division=0)
                f1 = f1_score(y_test, y_pred_test, average='weighted', zero_division=0)
            except:
                precision = recall = f1 = 0.0
            
            metrics = {
                'model_type': 'classification',
                'train_accuracy': float(train_acc),
                'test_accuracy': float(test_acc),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'overfitting': train_acc - test_acc > 0.15,
                'train_size': len(X_train),
                'test_size': len(X_test)
            }
            
            # Predictions dataframe
            predictions_df = pd.DataFrame({
                'actual': y_test,
                'predicted': y_pred_test,
                'correct': y_test == y_pred_test
            })
            
        else:
            # Regression
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Calculate metrics
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            train_mae = np.mean(np.abs(y_train - y_pred_train))
            test_mae = np.mean(np.abs(y_test - y_pred_test))
            
            metrics = {
                'model_type': 'regression',
                'train_r2': float(train_r2),
                'test_r2': float(test_r2),
                'train_rmse': float(train_rmse),
                'test_rmse': float(test_rmse),
                'train_mae': float(train_mae),
                'test_mae': float(test_mae),
                'overfitting': train_r2 - test_r2 > 0.15,
                'train_size': len(X_train),
                'test_size': len(X_test)
            }
            
            # Predictions dataframe
            predictions_df = pd.DataFrame({
                'actual': y_test,
                'predicted': y_pred_test,
                'residuals': y_test - y_pred_test,
                'abs_error': np.abs(y_test - y_pred_test)
            })
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        results = {
            'model': model,
            'metrics': metrics,
            'feature_importance': feature_importance,
            'predictions': predictions_df,
            'label_encoders': label_encoders,
            'target_encoder': target_encoder,
            'features_used': feature_columns,
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test
        }
        
        return results, f"Predictive model created successfully ({metrics['model_type']})"

class AdvancedPDFProcessor:
    """Advanced PDF processing with Docling and ColPali integration"""
    """Fast and efficient PDF processing agent with Ollama integration"""
    
    def __init__(self, ollama_client=None, ollama_model='llama3.2'):
        self.ollama = ollama_client
        self.ollama_model = ollama_model
        self.max_chunk_size = 1000
        self.max_pages = 20  # Limit for performance
        
    def process_pdf_fast(self, pdf_file) -> Dict[str, Any]:
        """Fast PDF processing with immediate Q&A capability"""
        
        start_time = datetime.now()
        
        try:
            # Reset file pointer
            pdf_file.seek(0)
            pdf_bytes = pdf_file.read()
            
            # Step 1: Extract text and structure with PyMuPDF (fastest)
            text_content = self._extract_text_pymupdf(pdf_bytes)
            
            # Step 2: Extract tables with pdfplumber (targeted)
            tables = self._extract_tables_fast(pdf_file)

            # ✅ Step 2B: Heuristic fallback if no structured tables found
            if not tables:
                heuristic_tables = self._extract_heuristic_tables(text_content)
                for h_table in heuristic_tables:
                    tables.append({
                        'page': 0,  # Optional: infer page if you track it
                        'index': len(tables),
                        'dataframe': h_table['dataframe'],
                        'text_summary': f"Heuristically detected: {h_table['rows']} rows × {h_table['cols']} cols",
                        'columns': [f"Col_{i+1}" for i in range(h_table['cols'])],
                        'shape': (h_table['rows'], h_table['cols'])
                    })
                if heuristic_tables:
                    logger.info(f"{len(heuristic_tables)} heuristic tables detected as fallback.")
            
            # Step 3: Extract images and OCR (if needed)
            images = self._extract_images_fast(pdf_bytes)
            
            # Step 4: Create semantic chunks for Q&A
            chunks = self._create_smart_chunks(text_content)
            
            # Step 5: Build searchable index
            searchable_content = self._build_searchable_index(chunks, tables)

             # ✅ Step 6: Structured JSON fallback (newly added)
            document_json = self._generate_structured_json_fallback(text_content, tables)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'text_content': text_content,
                'tables': tables,
                'images': images,
                'chunks': chunks,
                'searchable_content': searchable_content,
                'metadata': {
                    'processing_time': processing_time,
                    'total_chunks': len(chunks),
                    'total_tables': len(tables),
                    'total_images': len(images),
                    'content_length': len(text_content)
                },
                'status': 'success'
            }
            
            logger.info(f"PDF processed in {processing_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'text_content': '',
                'tables': [],
                'images': [],
                'chunks': [],
                'searchable_content': {},
                'document_json': {},  # Optional in error path
                'metadata': {}
            }
    
    def _extract_text_pymupdf(self, pdf_bytes: bytes) -> str:
        """Fast text extraction using PyMuPDF"""
        
        try:
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                full_text = ""
                
                # Limit pages for performance
                max_pages = min(len(doc), self.max_pages)
                
                for page_num in range(max_pages):
                    page = doc[page_num]
                    
                    # Get text with basic structure
                    page_text = page.get_text()
                    
                    # Clean and structure the text
                    cleaned_text = self._clean_text(page_text)
                    
                    full_text += f"\n=== PAGE {page_num + 1} ===\n{cleaned_text}\n"
                
                return full_text.strip()
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return f"Error extracting text: {str(e)}"
    
    def _extract_tables_fast(self, pdf_file) -> List[Dict[str, Any]]:
        """Fast table extraction using pdfplumber"""
        
        tables = []
        
        try:
            pdf_file.seek(0)
            
            with pdfplumber.open(pdf_file) as pdf:
                # Limit pages for performance
                max_pages = min(len(pdf.pages), self.max_pages)
                
                for page_num in range(max_pages):
                    page = pdf.pages[page_num]
                    
                    # Extract tables with better settings
                    page_tables = page.extract_tables(table_settings={
                        "vertical_strategy": "lines_strict",
                        "horizontal_strategy": "lines_strict",
                        "min_words_vertical": 3,
                        "min_words_horizontal": 1
                    })
                    
                    for table_idx, table in enumerate(page_tables):
                        if table and len(table) > 1:
                            try:
                                # Process table into DataFrame
                                processed_table = self._process_table(table, page_num + 1, table_idx)
                                if processed_table:
                                    tables.append(processed_table)
                                    
                            except Exception as e:
                                logger.warning(f"Table processing failed on page {page_num + 1}: {e}")
                                continue
                
        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
        
        return tables
    
    def _extract_heuristic_tables(self, text: str) -> List[Dict[str, Any]]:
        """
        Detects table-like structures from plain text extracted by PyMuPDF.
        Returns a list of DataFrames with aligned rows.
        """
        tables = []
        current_table = []
        lines = text.split("\n")

        for i in range(len(lines)):
            line = lines[i].strip()
            if not line:
                continue

            # Split by whitespace
            parts = line.split()

            # Start or continue a table if line has ≥2 columns
            if len(parts) >= 2:
                current_table.append(parts)

                # If next line is empty or invalid, end table
                if i == len(lines) - 1 or len(lines[i + 1].split()) < 2:
                    if len(current_table) >= 2:
                        try:
                            # Normalize to same width
                            max_cols = max(len(row) for row in current_table)
                            normalized = [
                                row + [""] * (max_cols - len(row)) for row in current_table
                            ]
                            df = pd.DataFrame(normalized)
                            tables.append({
                                'dataframe': df,
                                'rows': df.shape[0],
                                'cols': df.shape[1],
                                'preview': df.head(3).to_string(index=False)
                            })
                        except Exception as e:
                            logger.warning(f"Heuristic table formatting failed: {e}")
                    current_table = []
            else:
                current_table = []  # reset if format breaks

        return tables

    def _extract_images_fast(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """Fast image extraction with optional OCR"""
        
        images = []
        
        try:
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                # Limit pages for performance
                max_pages = min(len(doc), self.max_pages)
                
                for page_num in range(max_pages):
                    page = doc[page_num]
                    image_list = page.get_images()
                    
                    # Limit images per page
                    for img_idx, img in enumerate(image_list[:3]):  # Max 3 images per page
                        try:
                            xref = img[0]
                            pix = fitz.Pixmap(doc, xref)
                            
                            # Only process RGB/GRAY images
                            if pix.n - pix.alpha < 4:
                                img_data = pix.tobytes("png")
                                
                                # Optional OCR (only if image is text-heavy)
                                ocr_text = ""
                                if self._is_text_image(pix):
                                    ocr_text = self._ocr_image_fast(img_data)
                                
                                images.append({
                                    'page': page_num + 1,
                                    'index': img_idx,
                                    'size': (pix.width, pix.height),
                                    'ocr_text': ocr_text,
                                    'has_text': len(ocr_text) > 10
                                })
                            
                            pix = None  # Free memory
                            
                        except Exception as e:
                            logger.warning(f"Image processing failed: {e}")
                            continue
                
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
        
        return images
    
    def _process_table(self, table: List[List], page_num: int, table_idx: int) -> Optional[Dict[str, Any]]:
        """Process raw table into structured format"""
        
        try:
            # Clean headers
            headers = table[0] if table else []
            clean_headers = []
            
            for i, header in enumerate(headers):
                if header and str(header).strip():
                    clean_headers.append(str(header).strip())
                else:
                    clean_headers.append(f"Column_{i+1}")
            
            # Process data rows
            data_rows = table[1:] if len(table) > 1 else []
            clean_rows = []
            
            for row in data_rows:
                clean_row = []
                for cell in row:
                    cell_value = str(cell).strip() if cell else ""
                    clean_row.append(cell_value)
                clean_rows.append(clean_row)
            
            # Create DataFrame
            if clean_rows:
                df = pd.DataFrame(clean_rows, columns=clean_headers)
                
                # Remove completely empty rows
                df = df.replace('', np.nan)
                df = df.dropna(how='all')
                
                if not df.empty:
                    return {
                        'page': page_num,
                        'index': table_idx,
                        'dataframe': df,
                        'text_summary': f"Table on page {page_num}: {df.shape[0]} rows, {df.shape[1]} columns",
                        'columns': df.columns.tolist(),
                        'shape': df.shape
                    }
            
            return None
            
        except Exception as e:
            logger.warning(f"Table processing error: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\"\']+', ' ', text)
        
        # Fix common OCR errors
        text = text.replace('`', "'")
        text = text.replace('"', '"').replace('"', '"')
        
        return text.strip()
    
    def _create_smart_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Create semantic chunks optimized for Q&A"""
        
        if not text:
            return []
        
        chunks = []
        
        # Split by pages first
        pages = text.split('=== PAGE')
        
        for page_content in pages:
            if not page_content.strip():
                continue
            
            # Extract page number
            page_match = re.search(r'(\d+)', page_content)
            page_num = int(page_match.group(1)) if page_match else 0
            
            # Remove page header
            content = re.sub(r'^\d+\s*===\s*', '', page_content).strip()
            
            if len(content) <= self.max_chunk_size:
                # Small content, keep as single chunk
                chunks.append({
                    'id': len(chunks),
                    'page': page_num,
                    'content': content,
                    'word_count': len(content.split()),
                    'type': 'page_content'
                })
            else:
                # Split large content by sentences
                sentences = re.split(r'[.!?]+', content)
                current_chunk = ""
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    # Check if adding this sentence exceeds chunk size
                    if len(current_chunk) + len(sentence) > self.max_chunk_size:
                        if current_chunk:
                            chunks.append({
                                'id': len(chunks),
                                'page': page_num,
                                'content': current_chunk.strip(),
                                'word_count': len(current_chunk.split()),
                                'type': 'text_chunk'
                            })
                        current_chunk = sentence
                    else:
                        current_chunk += ". " + sentence if current_chunk else sentence
                
                # Add final chunk
                if current_chunk.strip():
                    chunks.append({
                        'id': len(chunks),
                        'page': page_num,
                        'content': current_chunk.strip(),
                        'word_count': len(current_chunk.split()),
                        'type': 'text_chunk'
                    })
        
        return chunks
    
    def _build_searchable_index(self, chunks: List[Dict], tables: List[Dict]) -> Dict[str, Any]:
        """Build searchable index for fast Q&A"""
        
        searchable = {
            'text_chunks': chunks,
            'tables': [],
            'keywords': set(),
            'page_map': {}
        }
        
        # Index chunks by page
        for chunk in chunks:
            page_num = chunk.get('page', 0)
            if page_num not in searchable['page_map']:
                searchable['page_map'][page_num] = []
            searchable['page_map'][page_num].append(chunk['id'])
            
            # Extract keywords
            content = chunk['content'].lower()
            words = re.findall(r'\b\w+\b', content)
            searchable['keywords'].update(words)
        
        # Index tables
        for table in tables:
            table_summary = {
                'page': table['page'],
                'text_summary': table['text_summary'],
                'columns': table['columns'],
                'shape': table['shape']
            }
            searchable['tables'].append(table_summary)
        
        searchable['keywords'] = list(searchable['keywords'])
        return searchable
    
    def _generate_structured_json_fallback(self, text: str, tables: List[Dict]) -> Dict:
        """
        Attempt to heuristically convert document text into structured JSON format
        """
        structured = {
            "sections": [],
            "key_value_pairs": {},
            "tables_summary": [tbl['text_summary'] for tbl in tables if 'text_summary' in tbl]
        }

        try:
            current_section = {"title": None, "content": ""}
            for line in text.split("\n"):
                line = line.strip()
                if not line:
                    continue

                # Detect section titles (heuristic)
                if re.match(r'^[A-Z ]{5,}$', line):
                    # Save previous section
                    if current_section["title"]:
                        structured["sections"].append(current_section)
                    current_section = {"title": line, "content": ""}
                else:
                    current_section["content"] += line + " "

                # Detect key-value patterns (e.g., "Invoice No: 12345")
                if ":" in line and len(line.split(":")[0].strip()) < 40:
                    k, v = line.split(":", 1)
                    structured["key_value_pairs"][k.strip()] = v.strip()

            # Add last section
            if current_section["title"]:
                structured["sections"].append(current_section)

            return structured

        except Exception as e:
            logger.warning(f"JSON fallback structuring failed: {e}")
            return {}

    def _is_text_image(self, pix) -> bool:
        """Determine if image likely contains text worth OCR"""
        
        # Simple heuristic: check aspect ratio and size
        width, height = pix.width, pix.height
        aspect_ratio = width / height if height > 0 else 1
        # Text images are usually wide or have reasonable dimensions
        return (aspect_ratio > 2 or (width > 200 and height > 50))
    
    def _ocr_image_fast(self, img_data: bytes) -> str:
        """Fast OCR with error handling"""
        
        try:
            # Check if tesseract is available
            import shutil
            if not shutil.which('tesseract'):
                return ""
            
            image = Image.open(io.BytesIO(img_data))
            
            # Use fast OCR settings
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?:;-() '
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # Clean and validate OCR result
            cleaned_text = self._clean_text(text)
            
            # Only return if OCR found meaningful text
            if len(cleaned_text) > 5 and len(cleaned_text.split()) > 2:
                return cleaned_text
            
            return ""
            
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return ""
    
    def answer_question(self, question: str, pdf_content: Dict[str, Any]) -> Dict[str, Any]:
        """Answer questions about the PDF using Ollama"""
        
        if not self.ollama:
            return {
                'answer': 'Ollama not available for PDF Q&A',
                'confidence': 0.0,
                'method': 'error'
            }
        
        # CHECK: Don't reprocess if content already exists
        if not pdf_content or pdf_content.get('status') != 'success':
            return {
                'answer': 'PDF content not available',
                'confidence': 0.0,
                'method': 'error'
            }
        
        try:
            # Step 1: Find relevant chunks
            relevant_chunks = self._find_relevant_content(question, pdf_content)
            
            # Step 2: Prepare context
            context = self._prepare_context(relevant_chunks, pdf_content)
            
            # Step 3: Generate answer with Ollama
            answer = self._generate_answer_ollama(question, context)
            
            return {
                'answer': answer['response'],
                'confidence': answer['confidence'],
                'method': 'ollama_rag',
                'relevant_pages': answer['pages'],
                'context_length': len(context)
            }
            
        except Exception as e:
            logger.error(f"PDF Q&A failed: {e}")
            return {
                'answer': f'Error processing question: {str(e)}',
                'confidence': 0.0,
                'method': 'error'
            }
    
    def _find_relevant_content(self, question: str, pdf_content: Dict[str, Any]) -> List[Dict]:
        """Find relevant chunks for the question"""
        
        question_lower = question.lower()
        question_words = set(re.findall(r'\b\w+\b', question_lower))
        
        chunks = pdf_content.get('chunks', [])
        relevant_chunks = []
        
        # Score chunks by keyword overlap
        for chunk in chunks:
            content_lower = chunk['content'].lower()
            content_words = set(re.findall(r'\b\w+\b', content_lower))
            
            # Calculate similarity score
            overlap = len(question_words.intersection(content_words))
            total_words = len(question_words.union(content_words))
            
            if total_words > 0:
                similarity = overlap / len(question_words)
                
                # Add context bonus for certain keywords
                if any(keyword in content_lower for keyword in ['table', 'figure', 'chart', 'data']):
                    similarity += 0.1
                
                if similarity > 0.1:  # Minimum relevance threshold
                    chunk_with_score = chunk.copy()
                    chunk_with_score['relevance_score'] = similarity
                    relevant_chunks.append(chunk_with_score)
        
        # Sort by relevance and return top chunks
        relevant_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_chunks[:5]  # Top 5 most relevant chunks
    
    def _prepare_context(self, relevant_chunks: List[Dict], pdf_content: Dict[str, Any]) -> str:
        """Prepare context for Ollama"""
        
        context_parts = []
        
        # Add text chunks
        for chunk in relevant_chunks:
            page_num = chunk.get('page', 'Unknown')
            content = chunk['content']
            context_parts.append(f"[Page {page_num}] {content}")
        
        # Add relevant table information
        tables = pdf_content.get('tables', [])
        for table in tables[:2]:  # Limit to 2 tables
            table_summary = table.get('text_summary', '')
            if table_summary:
                context_parts.append(f"[Table] {table_summary}")
        
        return "\n\n".join(context_parts)
    
    def _generate_answer_ollama(self, question: str, context: str) -> Dict[str, Any]:
        """Generate answer using Ollama"""
        
        prompt = f"""Based on the following document content, answer the user's question accurately and concisely.

        DOCUMENT CONTENT:
        {context}

        USER QUESTION: {question}

        Instructions:
        - Answer based only on the provided document content
        - If the answer is not in the document, say "I cannot find this information in the document"
        - Be specific and cite page numbers when possible
        - Keep the answer concise but complete

        ANSWER:"""

        try:
            response = self.ollama.generate(
                model=self.ollama_model,
                prompt=prompt,
                options={
                    "temperature": 0.5,
                    "top_p": 0.95,
                    "num_predict": 600
                }
            )
            
            answer_text = response['response'].strip()
            
            # Extract page references
            page_refs = re.findall(r'[Pp]age\s+(\d+)', answer_text)
            pages = list(set(int(p) for p in page_refs))
            
            # Estimate confidence based on answer quality
            confidence = self._estimate_answer_confidence(answer_text, context)
            
            return {
                'response': answer_text,
                'confidence': confidence,
                'pages': pages
            }
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return {
                'response': f"Error generating answer: {str(e)}",
                'confidence': 0.0,
                'pages': []
            }
    
    def _estimate_answer_confidence(self, answer: str, context: str) -> float:
        """Estimate confidence in the answer"""
        
        # Simple confidence estimation
        if "cannot find" in answer.lower() or "not in the document" in answer.lower():
            return 0.2
        
        # Check if answer contains specific information
        if any(keyword in answer.lower() for keyword in ['page', 'table', 'figure', 'section']):
            return 0.8
        
        # Check answer length and context overlap
        answer_words = set(re.findall(r'\b\w+\b', answer.lower()))
        context_words = set(re.findall(r'\b\w+\b', context.lower()))
        
        overlap = len(answer_words.intersection(context_words))
        if overlap > 5:
            return 0.7
        elif overlap > 2:
            return 0.5
        else:
            return 0.3

class AgenticTabularProcessor:
    """
    Advanced agentic processor for tabular data queries
    Replaces TAPAS with intelligent reasoning and calculation
    """
    
    def __init__(self, ollama_client=None, ollama_model='llama3.2'):
        self.ollama = ollama_client
        self.ollama_model = ollama_model
        
    def process_tabular_query(self, df, query, context=None):
        """
        Main agentic processing method that intelligently handles tabular queries
        """
        # Input validation
        if not query or len(query.strip()) < 2:
            return {
                'answer': 'Please provide a more specific question',
                'confidence': 0.1,
                'method': 'input_validation_error'
            }
        
        if df is None or df.empty:
            return {
                'answer': 'No data available to analyze',
                'confidence': 0.1,
                'method': 'data_validation_error'
            }
        
        try:
            # Step 1: Analyze the query intent and data context
            analysis_plan = self._create_analysis_plan(df, query, context)
            
            # Step 2: Execute the analysis plan
            result = self._execute_analysis_plan(df, analysis_plan)
            
            # Step 3: Generate natural language response
            response = self._generate_response(result, analysis_plan, query)
            
            return {
                'answer': response['answer'],
                'confidence': response['confidence'],
                'method': 'agentic_reasoning',
                'analysis_data': result,
                'plan_executed': analysis_plan
            }
            
        except Exception as e:
            logger.error(f"Agentic tabular processing failed: {e}")
            return {
                'answer': f"I encountered an error processing your query: {str(e)}",
                'confidence': 0.1,
                'method': 'error_fallback'
            }
    
    def _create_analysis_plan(self, df, query, context):
        """Create an intelligent analysis plan with AI-first approach"""
        
        plan = {
            'query_type': 'unknown',
            'target_columns': [],
            'operations': [],
            'filters': [],
            'aggregations': [],
            'confidence': 0.5,
            'original_query': query  # Store original query for context
        }
        
        # Step 1: Try AI-powered intent detection first (if Ollama available)
        if self.ollama and AI_MODELS.get('ollama_available', False):
            try:
                # Use your existing QueryIntentAgent
                intent_agent = QueryIntentAgent(self.ollama, AI_MODELS.get('embed_model'), self.ollama_model)
                ai_context = intent_agent.understand_query_with_context(query, df)
                
                # If AI detection is confident enough, use it
                if ai_context.get('confidence', 0) > 0.8:
                    plan.update({
                        'query_type': ai_context.get('intent', 'unknown'),
                        'operations': ai_context.get('operations', []),
                        'confidence': ai_context.get('confidence', 0.6),
                        'ai_reasoning': ai_context.get('reasoning', '')
                    })
                    
                    # Extract target columns and filters 
                    plan['target_columns'] = self._extract_target_columns(df, query, ai_context)
                    plan['filters'] = self._extract_filters(df, query)
                    
                    logger.info(f"AI intent detection successful: {plan['query_type']} (confidence: {plan['confidence']:.2f})")
                    return plan
                    
            except Exception as e:
                logger.warning(f"AI intent detection failed, falling back to pattern matching: {e}")
        
        # Step 2: Fallback to pattern matching (improved order and logic)
        query_lower = query.lower()
        
        # High-priority specific operations (check these first)
        if any(word in query_lower for word in ['maximum', 'max', 'highest', 'largest']) and not any(word in query_lower for word in ['count of', 'number of']):
            plan['query_type'] = 'extremes'
            plan['operations'] = ['max']
            plan['confidence'] = 0.9
            
        elif any(word in query_lower for word in ['minimum', 'min', 'lowest', 'smallest']) and not any(word in query_lower for word in ['count of', 'number of']):
            plan['query_type'] = 'extremes'
            plan['operations'] = ['min']
            plan['confidence'] = 0.9
            
        elif any(word in query_lower for word in ['average', 'mean', 'avg']) and not any(word in query_lower for word in ['count of', 'number of']):
            plan['query_type'] = 'aggregation'
            plan['operations'] = ['mean']
            plan['confidence'] = 0.9
            
        elif any(word in query_lower for word in ['median', 'middle']) and not any(word in query_lower for word in ['count of', 'number of']):
            plan['query_type'] = 'aggregation'
            plan['operations'] = ['median']
            plan['confidence'] = 0.9
            
        elif any(word in query_lower for word in ['sum', 'total']) and not any(word in query_lower for word in ['count of', 'number of']):
            plan['query_type'] = 'aggregation'
            plan['operations'] = ['sum']
            plan['confidence'] = 0.9
        
        # Counting operations (more specific patterns)
        elif any(phrase in query_lower for phrase in ['count of', 'how many', 'number of records', 'number of rows']):
            plan['query_type'] = 'counting'
            plan['operations'] = ['count']
            plan['confidence'] = 0.8

        elif (any(word in query_lower for word in ['predict', 'forecast', 'estimate', 'future', 'model']) and 
              not any(word in query_lower for word in ['max', 'min', 'average', 'sum', 'median', 'distinct', 'unique'])):
            plan['query_type'] = 'predict'
            plan['operations'] = ['predict']
            plan['confidence'] = 0.8
        
        # Other intents
        elif any(word in query_lower for word in ['correlation', 'relationship', 'related']):
            plan['query_type'] = 'correlation'
            plan['operations'] = ['correlation']
            plan['confidence'] = 0.8
            
            
        elif any(word in query_lower for word in ['cluster', 'group', 'segment', 'similar', 'categorize']):
            plan['query_type'] = 'cluster'
            plan['operations'] = ['cluster']
            plan['confidence'] = 0.7
            
        elif any(word in query_lower for word in ['show', 'plot', 'chart', 'graph', 'visualize', 'display']):
            plan['query_type'] = 'visualize'
            plan['operations'] = ['visualize']
            plan['confidence'] = 0.8
            
        elif any(word in query_lower for word in ['compare', 'comparison', 'vs', 'versus', 'against', 'difference']):
            plan['query_type'] = 'comparison'
            plan['operations'] = ['compare']
            plan['confidence'] = 0.7
            
        elif any(word in query_lower for word in ['distribution', 'spread', 'range']):
            plan['query_type'] = 'distribution'
            plan['operations'] = ['describe']
            plan['confidence'] = 0.7
            
        elif any(word in query_lower for word in ['outlier', 'anomaly', 'unusual', 'extreme', 'detect']):
            plan['query_type'] = 'detect'
            plan['operations'] = ['outliers']
            plan['confidence'] = 0.7
            
        elif any(phrase in query_lower for phrase in ['unique values', 'unique', 'distinct', 'what values', 'list values']):
            plan['query_type'] = 'categorical_analysis'
            plan['operations'] = ['unique_values']
            plan['confidence'] = 0.9
            
        elif any(word in query_lower for word in ['trend', 'over time', 'time series', 'temporal', 'change']):
            plan['query_type'] = 'trend'
            plan['operations'] = ['trend']
            plan['confidence'] = 0.7
            
        elif any(word in query_lower for word in ['summarize', 'summary', 'overview']):
            plan['query_type'] = 'summary'
            plan['operations'] = ['describe']
            plan['confidence'] = 0.6
        
        # Extract columns and filters for fallback method
        plan['target_columns'] = self._extract_target_columns(df, query, context)
        plan['filters'] = self._extract_filters(df, query)
        
        logger.info(f"Fallback pattern matching: {plan['query_type']} (confidence: {plan['confidence']:.2f})")
        return plan
    
    def _extract_target_columns(self, df, query, context):
        """Extract relevant columns mentioned in the query"""
        
        target_columns = []
        query_lower = query.lower()
        
        # Check context entities first
        if context and context.get('entities'):
            for entity in context['entities']:
                if entity in df.columns:
                    target_columns.append(entity)
        
        # Enhanced column name matching with scoring
        column_scores = {}
        query_words = query_lower.split()
        
        # Direct column name matching
        for col in df.columns:
            col_variations = [
                col.lower(),
                col.lower().replace('_', ' '),
                col.lower().replace('-', ' '),
                col.lower().replace('_', ''),
                col.lower().replace(' ', '')
            ]

            score = 0
        
            score = 0
            for variation in col_variations:
                # Exact match gets highest score
                if variation in query_lower:
                    score += 10
                # Word-by-word matching
                for word in query_words:
                    if len(word) > 2 and word in variation:
                        score += 5
                    if variation in word and len(word) > 3:
                        score += 3
            
            if score > 0:
                column_scores[col] = score
        
        # Sort by score and take best matches
        if column_scores:
            sorted_columns = sorted(column_scores.items(), key=lambda x: x[1], reverse=True)
            target_columns.extend([col for col, score in sorted_columns])
        
        # Remove duplicates while preserving order
        target_columns = list(dict.fromkeys(target_columns))
        
        # Special handling for distinct/unique queries
        if any(word in query_lower for word in ['distinct', 'unique']) and len(target_columns) > 1:
            # For distinct queries, prioritize exact matches and take only one column
            best_match = None
            highest_score = 0
            
            for col in target_columns:
                col_words = col.lower().replace('_', ' ').split()
                match_score = sum(1 for word in query_words if word in col_words)
                if match_score > highest_score:
                    highest_score = match_score
                    best_match = col
            
            if best_match:
                target_columns = [best_match]
        
        # Fallback heuristics if no columns found
        if not target_columns:
            # For aggregation queries, prefer numeric columns
            if any(word in query_lower for word in ['average', 'sum', 'total', 'mean', 'max', 'min', 'median']):
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    target_columns = [numeric_cols[0]]
            
            # For counting/distinct queries, can work with any column
            elif any(word in query_lower for word in ['count', 'distinct', 'unique']):
                target_columns = [df.columns[0]]
        
        return target_columns[:3]  # Limit to top 3 columns
    
    def _extract_filters(self, df, query):
        """Extract filter conditions from the query"""
        
        filters = []
        query_lower = query.lower()
        
        # Pattern matching for common filter formats
        filter_patterns = [
            r'where\s+(\w+)\s*=\s*(["\']?)([^"\']+)\2',  # where column = value
            r'for\s+(\w+)\s+(["\']?)([^"\']+)\2',        # for column value
            r'(\w+)\s*=\s*(["\']?)([^"\']+)\2',          # column = value
            r'(\w+)\s+is\s+(["\']?)([^"\']+)\2',         # column is value
            r'in\s+(\w+)\s+(["\']?)([^"\']+)\2',         # in column value
        ]
        
        for pattern in filter_patterns:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                if len(match) >= 3:
                    column_hint = match[0]
                    value = match[2]
                    
                    # Enhanced column matching
                    matching_cols = []
                    for col in df.columns:
                        if (column_hint.lower() in col.lower() or 
                            col.lower() in column_hint.lower() or
                            column_hint.lower().replace('_', ' ') in col.lower().replace('_', ' ')):
                            matching_cols.append(col)
                    
                    if matching_cols:
                        filters.append({
                            'column': matching_cols[0],
                            'operator': '==',
                            'value': value
                        })
        
        return filters
    
    def _execute_analysis_plan(self, df, plan, query = None):
        """Execute the analysis plan and return results"""
        
        result = {
            'query_type': plan['query_type'],
            'operations_performed': [],
            'results': {},
            'data_used': {
                'total_rows': len(df),
                'columns_analyzed': plan['target_columns']
            }
        }
        
        # Apply filters first
        working_df = df.copy()
        if plan['filters']:
            for filter_condition in plan['filters']:
                try:
                    col = filter_condition['column']
                    value = filter_condition['value']
                    
                    if col in working_df.columns:
                        # Try different value types
                        if working_df[col].dtype == 'object':
                            working_df = working_df[working_df[col].str.lower().str.contains(str(value).lower(), na=False)]
                        else:
                            try:
                                numeric_value = float(value)
                                working_df = working_df[working_df[col] == numeric_value]
                            except:
                                working_df = working_df[working_df[col].astype(str).str.lower() == str(value).lower()]
                        
                        result['operations_performed'].append(f"Filtered {col} = {value}")
                        
                except Exception as e:
                    logger.warning(f"Filter failed: {e}")
                    continue
        
        result['data_used']['rows_after_filter'] = len(working_df)
        
        # Execute operations based on query type
        if plan['query_type'] == 'aggregation':
            result['results'] = self._perform_aggregation(working_df, plan)
            
        elif plan['query_type'] == 'counting':
            result['results'] = self._perform_counting(working_df, plan)
            
        elif plan['query_type'] == 'extremes':
            result['results'] = self._perform_extremes(working_df, plan)
            
        elif plan['query_type'] == 'correlation':
            result['results'] = self._perform_correlation(working_df, plan)
            
        elif plan['query_type'] == 'distribution':
            result['results'] = self._perform_distribution(working_df, plan)
            
        elif plan['query_type'] == 'comparison':
            result['results'] = self._perform_comparison(working_df, plan)
            
        elif plan['query_type'] == 'categorical_analysis':
            result['results'] = self._perform_categorical_analysis(working_df, plan)
            
        elif plan['query_type'] == 'summary':
            result['results'] = self._perform_summary(working_df, plan)
            
        else:
            # Default: basic description
            result['results'] = self._perform_basic_analysis(working_df, plan)

        # Filter results based on query intent
        result['results'] = self._filter_results_by_query_intent(result['results'], query, plan)
        
        
        return result
    
    def _filter_results_by_query_intent(self, results, query, plan):
        """Filter results to only show what user specifically asked for"""
        
        if not query:
            return results
            
        query_lower = query.lower()
        filtered_results = {}
        
        # For distinct/unique queries, be very specific
        if any(word in query_lower for word in ['distinct', 'unique', 'how many distinct', 'how many unique']):
            query_words = query_lower.split()
            
            # Find the specific column being asked about
            target_word = None
            for word in query_words:
                if len(word) > 2 and word not in ['how', 'many', 'distinct', 'unique', 'the', 'of', 'are', 'is']:
                    target_word = word
                    break
            
            if target_word:
                for key, value in results.items():
                    # Only include results that match the target word and are unique counts
                    if (target_word in key.lower() and 
                        ('unique_count' in key or 'unique_values' in str(value))):
                        filtered_results[key] = value
            
            # If no specific matches, look for any unique_count results
            if not filtered_results:
                for key, value in results.items():
                    if 'unique_count' in key:
                        filtered_results[key] = value
        
        # For max/min queries, only show the extreme values
        elif any(word in query_lower for word in ['max', 'maximum', 'min', 'minimum']):
            for key, value in results.items():
                if isinstance(value, dict):
                    if 'max_value' in value or 'min_value' in value:
                        filtered_results[key] = value
                elif 'max' in key.lower() or 'min' in key.lower():
                    filtered_results[key] = value
        
        # For statistical queries, filter to specific operation
        elif any(word in query_lower for word in ['average', 'mean', 'sum', 'total', 'median']):
            for key, value in results.items():
                if isinstance(value, dict):
                    # Filter to only the requested statistic
                    filtered_value = {}
                    if 'average' in query_lower or 'mean' in query_lower:
                        if 'mean' in value:
                            filtered_value['mean'] = value['mean']
                    if 'sum' in query_lower or 'total' in query_lower:
                        if 'sum' in value:
                            filtered_value['sum'] = value['sum']
                    if 'median' in query_lower:
                        if 'median' in value:
                            filtered_value['median'] = value['median']
                    
                    if filtered_value:
                        filtered_results[key] = filtered_value
                    else:
                        filtered_results[key] = value
                else:
                    filtered_results[key] = value
        
        else:
            # For other queries, return all results but prioritize relevant ones
            filtered_results = results
        
        return filtered_results if filtered_results else results
    
    def _perform_aggregation(self, df, plan):
        """Perform aggregation operations"""
        
        results = {}
        target_cols = plan['target_columns'] if plan['target_columns'] else df.select_dtypes(include=[np.number]).columns.tolist()[:1]
        
        for col in target_cols:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                col_results = {}
                
                for operation in plan['operations']:
                    try:
                        if operation == 'mean':
                            col_results['mean'] = float(df[col].mean())
                        elif operation == 'sum':
                            col_results['sum'] = float(df[col].sum())
                        elif operation == 'median':
                            col_results['median'] = float(df[col].median())
                    except Exception as e:
                        logger.warning(f"Aggregation failed for {col}, {operation}: {e}")
                
                if col_results:
                    results[col] = col_results
        
        return results
    
    def _perform_counting(self, df, plan):
        """Perform counting operations"""
        
        results = {}
        
        if plan['target_columns']:
            for col in plan['target_columns']:
                if col in df.columns:
                    results[f'{col}_count'] = len(df[col].dropna())
                    results[f'{col}_unique_count'] = df[col].nunique()
        else:
            results['total_rows'] = len(df)
            results['total_columns'] = len(df.columns)
        
        return results
    
    def _perform_extremes(self, df, plan):
        """Find extreme values (max/min)"""
        
        results = {}
        target_cols = plan['target_columns'] if plan['target_columns'] else df.select_dtypes(include=[np.number]).columns.tolist()[:1]
        
        for col in target_cols:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                col_results = {}
                
                for operation in plan['operations']:
                    try:
                        if operation == 'max':
                            col_results['max_value'] = float(df[col].max())
                            max_idx = df[col].idxmax()
                            col_results['max_row_info'] = df.loc[max_idx].to_dict()
                        elif operation == 'min':
                            col_results['min_value'] = float(df[col].min())
                            min_idx = df[col].idxmin()
                            col_results['min_row_info'] = df.loc[min_idx].to_dict()
                    except Exception as e:
                        logger.warning(f"Extreme value calculation failed for {col}: {e}")
                
                if col_results:
                    results[col] = col_results
        
        return results
    
    def _perform_correlation(self, df, plan):
        """Perform correlation analysis"""
        
        results = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) >= 2:
            # If specific columns mentioned, use those
            if len(plan['target_columns']) >= 2:
                col1, col2 = plan['target_columns'][:2]
                if col1 in numeric_cols and col2 in numeric_cols:
                    try:
                        corr_value = df[col1].corr(df[col2])
                        results[f'{col1}_vs_{col2}'] = {
                            'correlation': float(corr_value),
                            'strength': 'strong' if abs(corr_value) > 0.7 else 'moderate' if abs(corr_value) > 0.3 else 'weak'
                        }
                    except Exception as e:
                        logger.warning(f"Correlation calculation failed: {e}")
            
            # Default: correlation matrix of numeric columns
            if not results:
                try:
                    corr_matrix = df[numeric_cols[:4]].corr()  # Limit to 4 columns for performance
                    results['correlation_matrix'] = corr_matrix.to_dict()
                except Exception as e:
                    logger.warning(f"Correlation matrix failed: {e}")
        
        return results
    
    def _perform_distribution(self, df, plan):
        """Analyze data distribution"""
        
        results = {}
        target_cols = plan['target_columns'] if plan['target_columns'] else df.select_dtypes(include=[np.number]).columns.tolist()[:2]
        
        for col in target_cols:
            if col in df.columns:
                col_results = {}
                
                if pd.api.types.is_numeric_dtype(df[col]):
                    try:
                        col_results.update({
                            'mean': float(df[col].mean()),
                            'median': float(df[col].median()),
                            'std': float(df[col].std()),
                            'min': float(df[col].min()),
                            'max': float(df[col].max()),
                            'range': float(df[col].max() - df[col].min())
                        })
                    except Exception as e:
                        logger.warning(f"Distribution analysis failed for {col}: {e}")
                else:
                    # Categorical distribution
                    try:
                        value_counts = df[col].value_counts().head(5)
                        col_results['top_values'] = value_counts.to_dict()
                        col_results['unique_count'] = df[col].nunique()
                    except Exception as e:
                        logger.warning(f"Categorical distribution failed for {col}: {e}")
                
                if col_results:
                    results[col] = col_results
        
        return results
    
    def _perform_comparison(self, df, plan):
        """Perform comparison analysis"""
        
        results = {}
        
        if len(plan['target_columns']) >= 2:
            col1, col2 = plan['target_columns'][:2]
            
            if col1 in df.columns and col2 in df.columns:
                try:
                    if pd.api.types.is_numeric_dtype(df[col1]) and pd.api.types.is_numeric_dtype(df[col2]):
                        # Numeric comparison
                        results['comparison'] = {
                            f'{col1}_mean': float(df[col1].mean()),
                            f'{col2}_mean': float(df[col2].mean()),
                            'difference': float(df[col1].mean() - df[col2].mean()),
                            'ratio': float(df[col1].mean() / df[col2].mean()) if df[col2].mean() != 0 else None
                        }
                    else:
                        # Categorical comparison
                        results['comparison'] = {
                            f'{col1}_unique': df[col1].nunique(),
                            f'{col2}_unique': df[col2].nunique(),
                            f'{col1}_mode': str(df[col1].mode().iloc[0]) if not df[col1].mode().empty else 'N/A',
                            f'{col2}_mode': str(df[col2].mode().iloc[0]) if not df[col2].mode().empty else 'N/A'
                        }
                except Exception as e:
                    logger.warning(f"Comparison failed: {e}")
        
        return results
    
    def _perform_categorical_analysis(self, df, plan, query=None):
        """Enhanced categorical/unique value analysis with query-specific filtering"""
        
        results = {}
        target_cols = plan['target_columns'] if plan['target_columns'] else [df.columns[0]]
        
        # Query-specific column filtering
        if query:
            query_lower = query.lower()
            query_words = query_lower.split()
            
            # Filter target columns to only those mentioned in the query
            filtered_cols = []
            for col in target_cols:
                col_words = col.lower().replace('_', ' ').split()
                if any(word in col_words for word in query_words if len(word) > 2):
                    filtered_cols.append(col)
            
            if filtered_cols:
                target_cols = filtered_cols
        
        for col in target_cols:
            if col in df.columns:
                try:
                    unique_values = df[col].unique()
                    value_counts = df[col].value_counts()
                    
                    results[col] = {
                        'unique_values': [str(val) for val in unique_values[:20]],
                        'unique_count': len(unique_values),
                        'total_count': len(df[col].dropna()),
                        'most_common': str(value_counts.index[0]) if len(value_counts) > 0 else 'N/A',
                        'most_common_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
                    }
                    
                    if len(unique_values) > 20:
                        results[col]['note'] = f"Showing first 20 of {len(unique_values)} unique values"
                        
                except Exception as e:
                    logger.warning(f"Categorical analysis failed for {col}: {e}")
        
        return results
    
    def _perform_summary(self, df, plan):
        """Perform summary analysis"""
        
        results = {}
        
        try:
            # Basic summary statistics
            results['basic_info'] = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
                'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns)
            }
            
            # Summary of numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:3]
            if numeric_cols:
                numeric_summary = {}
                for col in numeric_cols:
                    try:
                        numeric_summary[col] = {
                            'mean': float(df[col].mean()),
                            'median': float(df[col].median()),
                            'std': float(df[col].std())
                        }
                    except Exception as e:
                        logger.warning(f"Numeric summary failed for {col}: {e}")
                
                results['numeric_summary'] = numeric_summary
            
        except Exception as e:
            logger.warning(f"Summary analysis failed: {e}")
        
        return results
    
    def _perform_basic_analysis(self, df, plan):
        """Fallback basic analysis"""
        
        results = {
            'basic_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist()[:10]  # First 10 columns
            }
        }
        
        if plan['target_columns']:
            col = plan['target_columns'][0]
            if col in df.columns:
                try:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        results[col] = {
                            'type': 'numeric',
                            'mean': float(df[col].mean()),
                            'count': len(df[col].dropna())
                        }
                    else:
                        results[col] = {
                            'type': 'categorical',
                            'unique_values': df[col].nunique(),
                            'most_common': str(df[col].mode().iloc[0]) if not df[col].mode().empty else 'N/A'
                        }
                except Exception as e:
                    logger.warning(f"Basic analysis failed for {col}: {e}")
        
        return results
    
    def _generate_response(self, result, plan, original_query):
        """Enhanced natural language response generation with smart filtering"""
        
        try:
            response_parts = []
            confidence = 0.7
            query_lower = original_query.lower() if original_query else ""
            
            # Handle different result types with smart filtering
            if result.get('results'):
                
                # For distinct/unique queries, prioritize unique_count results
                if any(word in query_lower for word in ['distinct', 'unique']):
                    unique_found = False
                    
                    for key, value in result['results'].items():
                        if isinstance(value, dict) and 'unique_count' in value:
                            response_parts.append(f"Distinct {key}: {value['unique_count']:,}")
                            unique_found = True
                        elif 'unique_count' in key:
                            response_parts.append(f"Distinct {key.replace('_unique_count', '')}: {value:,}")
                            unique_found = True
                    
                    if unique_found:
                        confidence = 0.9
                    
                # For statistical operations, show only the requested statistic
                elif any(word in query_lower for word in ['max', 'maximum', 'min', 'minimum', 'average', 'mean', 'sum', 'total', 'median']):
                    
                    for key, value in result['results'].items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if isinstance(sub_value, (int, float)):
                                    if ('max' in query_lower or 'maximum' in query_lower) and 'max_value' in sub_key:
                                        response_parts.append(f"Maximum {key}: {sub_value:,.2f}")
                                        confidence = 0.9
                                    elif ('min' in query_lower or 'minimum' in query_lower) and 'min_value' in sub_key:
                                        response_parts.append(f"Minimum {key}: {sub_value:,.2f}")
                                        confidence = 0.9
                                    elif ('average' in query_lower or 'mean' in query_lower) and 'mean' in sub_key:
                                        response_parts.append(f"Average {key}: {sub_value:,.2f}")
                                        confidence = 0.9
                                    elif ('sum' in query_lower or 'total' in query_lower) and 'sum' in sub_key:
                                        response_parts.append(f"Total {key}: {sub_value:,.2f}")
                                        confidence = 0.9
                                    elif 'median' in query_lower and 'median' in sub_key:
                                        response_parts.append(f"Median {key}: {sub_value:,.2f}")
                                        confidence = 0.9
                
                # For general queries, show all relevant results
                else:
                    for key, value in result['results'].items():
                        if isinstance(value, dict):
                            # Handle nested results
                            for sub_key, sub_value in value.items():
                                if isinstance(sub_value, (int, float)):
                                    if 'mean' in sub_key or 'average' in sub_key:
                                        response_parts.append(f"Average {key}: {sub_value:,.2f}")
                                    elif 'sum' in sub_key or 'total' in sub_key:
                                        response_parts.append(f"Total {key}: {sub_value:,.2f}")
                                    elif 'max_value' in sub_key:
                                        response_parts.append(f"Maximum {key}: {sub_value:,.2f}")
                                    elif 'min_value' in sub_key:
                                        response_parts.append(f"Minimum {key}: {sub_value:,.2f}")
                                    elif 'median' in sub_key:
                                        response_parts.append(f"Median {key}: {sub_value:,.2f}")
                                    elif 'correlation' in sub_key:
                                        response_parts.append(f"{key} correlation: {sub_value:.3f}")
                                    elif 'unique_count' in sub_key:
                                        response_parts.append(f"Distinct {key}: {sub_value:,}")
                                    else:
                                        response_parts.append(f"{key} {sub_key}: {sub_value:,.2f}")
                        elif isinstance(value, (int, float)):
                            if 'unique_count' in key:
                                col_name = key.replace('_unique_count', '')
                                response_parts.append(f"Distinct {col_name}: {value:,}")
                            elif 'count' in key:
                                response_parts.append(f"{key.replace('_', ' ').title()}: {value:,}")
                            else:
                                response_parts.append(f"{key.replace('_', ' ').title()}: {value:,.2f}")
                        elif isinstance(value, str):
                            response_parts.append(f"{key.replace('_', ' ').title()}: {value}")
            
            # Create final response
            if response_parts:
                # For distinct queries, keep it simple and focused
                if any(word in query_lower for word in ['distinct', 'unique']):
                    answer = response_parts[0] if response_parts else "No distinct values found"
                else:
                    answer = ". ".join(response_parts[:3])  # Limit to top 3 for readability
                confidence = min(confidence + 0.1, 1.0)
            else:
                # Fallback response
                query_type = plan.get('query_type', 'analysis')
                rows_analyzed = result.get('data_used', {}).get('total_rows', 0)
                answer = f"Completed {query_type} on {rows_analyzed:,} rows"
                confidence = 0.5
            
            # Add filter context if applicable
            data_used = result.get('data_used', {})
            if (data_used.get('rows_after_filter', 0) != data_used.get('total_rows', 0) and 
                data_used.get('rows_after_filter', 0) > 0):
                filtered_rows = data_used['rows_after_filter']
                answer += f" (filtered to {filtered_rows:,} rows)"
            
            return {'answer': answer, 'confidence': confidence}
                
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return {
                'answer': f"Analysis completed successfully. Results available in detailed view.",
                'confidence': 0.4
            }
        
    def _format_aggregation_response(self, result, plan):
        """Format aggregation results into natural language"""
        
        if not result['results']:
            return {'answer': 'No aggregation results found.', 'confidence': 0.2}
        
        response_parts = []
        confidence = 0.8
        
        for col, col_results in result['results'].items():
            for operation, value in col_results.items():
                if operation == 'mean':
                    response_parts.append(f"Average {col}: {value:,.2f}")
                elif operation == 'sum':
                    response_parts.append(f"Total {col}: {value:,.2f}")
                elif operation == 'median':
                    response_parts.append(f"Median {col}: {value:,.2f}")
        
        answer = ". ".join(response_parts)
        
        # Add context if data was filtered
        if result['data_used'].get('rows_after_filter', 0) != result['data_used']['total_rows']:
            answer += f". (Based on {result['data_used']['rows_after_filter']} filtered rows)"
        
        return {'answer': answer, 'confidence': confidence}
    
    def _format_counting_response(self, result, plan):
        """Format counting results"""
        
        if not result['results']:
            return {'answer': 'No counting results found.', 'confidence': 0.2}
        
        response_parts = []
        
        for key, value in result['results'].items():
            if 'total_rows' in key:
                response_parts.append(f"Total records: {value:,}")
            elif 'unique_count' in key:
                col_name = key.replace('_unique_count', '')
                response_parts.append(f"Unique {col_name} values: {value:,}")
            elif '_count' in key:
                col_name = key.replace('_count', '')
                response_parts.append(f"{col_name} count: {value:,}")
        
        answer = ". ".join(response_parts)
        return {'answer': answer, 'confidence': 0.9}
    
    def _format_extremes_response(self, result, plan):
        """Format extreme values results"""
        
        if not result['results']:
            return {'answer': 'No extreme values found.', 'confidence': 0.2}
        
        response_parts = []
        
        for col, col_results in result['results'].items():
            if 'max_value' in col_results:
                response_parts.append(f"Maximum {col}: {col_results['max_value']:,.2f}")
            if 'min_value' in col_results:
                response_parts.append(f"Minimum {col}: {col_results['min_value']:,.2f}")
        
        answer = ". ".join(response_parts)
        return {'answer': answer, 'confidence': 0.8}
    
    def _format_correlation_response(self, result, plan):
        """Format correlation results"""
        
        if not result['results']:
            return {'answer': 'No correlation analysis possible.', 'confidence': 0.2}
        
        response_parts = []
        
        for key, value in result['results'].items():
            if isinstance(value, dict) and 'correlation' in value:
                corr_val = value['correlation']
                strength = value['strength']
                response_parts.append(f"{key.replace('_vs_', ' vs ')}: {corr_val:.3f} ({strength} correlation)")
        
        if not response_parts and 'correlation_matrix' in result['results']:
            response_parts.append("Correlation matrix calculated for numeric columns")
        
        answer = ". ".join(response_parts) if response_parts else "Correlation analysis completed"
        return {'answer': answer, 'confidence': 0.7}
    
    def _format_distribution_response(self, result, plan):
        """Format distribution analysis results"""
        
        if not result['results']:
            return {'answer': 'No distribution analysis available.', 'confidence': 0.2}
        
        response_parts = []
        
        for col, col_results in result['results'].items():
            if 'mean' in col_results and 'std' in col_results:
                mean_val = col_results['mean']
                std_val = col_results['std']
                response_parts.append(f"{col}: mean={mean_val:.2f}, std={std_val:.2f}")
            elif 'unique_count' in col_results:
                unique_count = col_results['unique_count']
                response_parts.append(f"{col}: {unique_count} unique values")
        
        answer = ". ".join(response_parts)
        return {'answer': answer, 'confidence': 0.7}
    
    def _format_comparison_response(self, result, plan):
        """Format comparison results"""
        
        if not result['results'] or 'comparison' not in result['results']:
            return {'answer': 'No comparison results available.', 'confidence': 0.2}
        
        comp_data = result['results']['comparison']
        response_parts = []
        
        # Look for mean comparisons
        mean_keys = [k for k in comp_data.keys() if '_mean' in k]
        if len(mean_keys) >= 2:
            col1_mean = comp_data[mean_keys[0]]
            col2_mean = comp_data[mean_keys[1]]
            col1_name = mean_keys[0].replace('_mean', '')
            col2_name = mean_keys[1].replace('_mean', '')
            
            response_parts.append(f"{col1_name} average: {col1_mean:.2f}")
            response_parts.append(f"{col2_name} average: {col2_mean:.2f}")
            
            if 'difference' in comp_data:
                diff = comp_data['difference']
                response_parts.append(f"Difference: {diff:.2f}")
        
        # Look for unique value comparisons
        unique_keys = [k for k in comp_data.keys() if '_unique' in k]
        if len(unique_keys) >= 2:
            for key in unique_keys:
                col_name = key.replace('_unique', '')
                response_parts.append(f"{col_name} has {comp_data[key]} unique values")
        
        answer = ". ".join(response_parts) if response_parts else "Comparison analysis completed"
        return {'answer': answer, 'confidence': 0.6}
    
    def _format_summary_response(self, result, plan):
        """Format summary results"""
        
        if not result['results']:
            return {'answer': 'No summary information available.', 'confidence': 0.2}
        
        response_parts = []
        
        # Basic info
        if 'basic_info' in result['results']:
            basic = result['results']['basic_info']
            if 'total_rows' in basic and 'total_columns' in basic:
                response_parts.append(f"Dataset has {basic['total_rows']:,} rows and {basic['total_columns']} columns")
            
            if 'numeric_columns' in basic:
                response_parts.append(f"{basic['numeric_columns']} numeric columns")
        
        # Numeric summary
        if 'numeric_summary' in result['results']:
            num_summary = result['results']['numeric_summary']
            for col, stats in list(num_summary.items())[:2]:  # Limit to 2 columns
                if 'mean' in stats:
                    response_parts.append(f"{col} average: {stats['mean']:.2f}")
        
        answer = ". ".join(response_parts) if response_parts else "Data summary completed"
        return {'answer': answer, 'confidence': 0.6}

# ============================================================================
# 6 . 📊 DATA PROCESSING AND STATISTICAL ANALYSIS
# ============================================================================
@enhanced_error_handling
@track_performance("Data Loading")
def load_and_validate_data(file):
    """Load and clean data from CSV or Excel with smart type conversion"""
    
    # Validate file
    is_valid, error_msg = validate_input(file, CONFIG.max_file_size_mb)
    if not is_valid:
        st.error(error_msg)
        return None
    
    try:
        # Load data based on file type
        if file.name.endswith('.csv'):
            try:
                df = pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                file.seek(0)
                df = pd.read_csv(file, encoding='latin-1')
        else:
            df = pd.read_excel(file)
        
        # Validate data size
        if len(df) > CONFIG.max_rows_display:
            st.warning(f"Large dataset detected ({len(df)} rows). Showing first {CONFIG.max_rows_display} rows for performance.")
            df = df.head(CONFIG.max_rows_display)
        
        # Clean column names
        df.columns = [
            str(col).strip().replace(' ', '_').replace('-', '_')
            .replace('(', '').replace(')', '').replace('[', '')
            .replace(']', '').replace('/', '_').replace('\\', '_')
            .lower()[:50] for col in df.columns
        ]
        
        # Remove empty rows and unnamed columns
        df = df.dropna(how="all")
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Handle duplicate columns
        if df.columns.duplicated().any():
            cols = pd.Series(df.columns)
            for dup in cols[cols.duplicated()].unique():
                cols[cols[cols == dup].index.values.tolist()] = [
                    dup + f'_{i}' for i in range(sum(cols == dup))
                ]
            df.columns = cols.tolist()
        
        # Smart data type conversion
        df = smart_data_type_conversion(df)
        
        if df.empty or len(df.columns) == 0:
            st.error("No valid data found in the uploaded file.")
            return None
        
        logger.info(f"Data loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = True
            st.success(f"✅ Data loaded: {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"Error loading file: {str(e)}")
        st.error(f"Error loading file: {str(e)}")
        return None

def smart_data_type_conversion(df):
    """Automatically detect and convert data types with optimized sampling"""
    conversion_log = []
    
    for col in df.columns:
        original_type = str(df[col].dtype)
        
        try:
            # Skip if already optimal numeric type
            if pd.api.types.is_numeric_dtype(df[col]) and df[col].dtype != 'object':
                continue
            
            # Use sampling for large datasets to speed up detection
            sample_size = min(1000, len(df))
            sample = df[col].sample(n=sample_size, random_state=42) if len(df) > 1000 else df[col]
            
            # 1. Try numeric conversion first
            numeric_sample = pd.to_numeric(sample, errors='coerce')
            numeric_ratio = numeric_sample.notna().sum() / len(sample)
            
            if numeric_ratio >= 0.8:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                conversion_log.append(f"{col}: {original_type} → numeric")
                continue
            
            # 2. Try datetime conversion for date-like columns
            if any(indicator in col.lower() for indicator in ['date', 'time', 'created', 'updated']):
                try:
                    date_sample = pd.to_datetime(sample, errors='coerce')
                    date_ratio = date_sample.notna().sum() / len(sample)
                    
                    if date_ratio >= 0.7:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        conversion_log.append(f"{col}: {original_type} → datetime")
                        continue
                except Exception:
                    pass
            
            # 3. Convert to category for low-cardinality string columns
            if df[col].dtype == 'object':
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.05 and df[col].nunique() < 50:
                    df[col] = df[col].astype('category')
                    conversion_log.append(f"{col}: {original_type} → category")
                else:
                    # Keep as string but ensure no NaN
                    df[col] = df[col].astype(str).fillna('')
                    if original_type != 'object':
                        conversion_log.append(f"{col}: {original_type} → string")
            
        except Exception as e:
            logger.warning(f"Type conversion failed for {col}: {e}")
            conversion_log.append(f"{col}: conversion failed - {str(e)}")
            # Fallback: keep as string
            try:
                df[col] = df[col].astype(str).fillna('')
            except:
                pass
    
    # Log conversion summary
    if conversion_log:
        logger.info(f"Data type conversions completed: {len(conversion_log)} columns processed")
        for log_entry in conversion_log:
            logger.debug(log_entry)
    
    return df

def detect_lookup_query(query, df):
    """
    Robust lookup query detector that handles:
    - Simple lookups: "what is X for Y = Z"
    - Statistical lookups: "sum of X for Y = Z"
    - UNLIMITED FILTERS: "sum of X for A = B where C is D and E = F..."
    - Date filters: "for planned_dates 2025-07-15"
    - Mixed operators: equals, is, contains, >, <, >=, <=
    - Fuzzy column matching with confidence scoring
    """
    
    query_lower = query.lower().strip()
    
    # Skip if clearly visualization query
    viz_keywords = ['plot', 'chart', 'graph', 'visualize', 'display', 'show chart', 'draw']
    if any(keyword in query_lower for keyword in viz_keywords):
        return None
    
    # Try to parse as a statistical query with multiple filters
    stat_result = _parse_statistical_query_with_unlimited_filters(query_lower, df)
    if stat_result:
        return stat_result
    
    # Try simple lookup patterns
    simple_patterns = [
        # Enhanced patterns with 'is' and 'equals'
        r'what\s+(?:is\s+)?(?:the\s+)?(\w+)\s+for\s+(\w+)\s+([^\s]+)',
        r'(?:find|get|show)\s+(?:the\s+)?(\w+)\s+for\s+(\w+)\s+([^\s]+)',
        r'^(\w+)\s+for\s+(\w+)\s+([^\s]+)$',
        
        # 'where' patterns with 'is' and 'equals'
        r'what\s+(?:is\s+)?(?:the\s+)?(\w+)\s+where\s+(\w+)\s*[=:]\s*([^\s]+)',
        r'what\s+(?:is\s+)?(?:the\s+)?(\w+)\s+where\s+(\w+)\s+(?:is|equals?|is\s+equal\s+to)\s+([^\s]+)',
        r'(?:find|get|show)\s+(?:the\s+)?(\w+)\s+where\s+(\w+)\s+(?:is|equals?|is\s+equal\s+to)\s+([^\s]+)',
        
        # Reverse pattern
        r'^(\w+)\s+([^\s]+)\s+(\w+)$',
    ]
    
    for pattern in simple_patterns:
        match = re.search(pattern, query_lower)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                if pattern.endswith('(\\w+)$') and not any(word in groups[0] for word in ['what', 'find', 'get', 'show']):
                    filter_col, filter_value, target_col = groups
                else:
                    target_col, filter_col, filter_value = groups
                
                result = _process_simple_lookup(df, target_col, filter_col, filter_value)
                if result:
                    return result
    
    return None

def _parse_statistical_query_with_unlimited_filters(query_lower, df):
    """Parse statistical queries with unlimited number of filters"""
    
    # Step 1: Extract the statistical operation and target column
    stat_match = re.match(r'(sum|total|average|avg|mean|max|maximum|min|minimum|count|median)\s+(?:of\s+)?(\w+)', query_lower)
    
    if not stat_match:
        return None
    
    stat_operation = stat_match.group(1)
    target_col_hint = stat_match.group(2)
    
    # Step 2: Extract all filter conditions
    filters = _extract_all_filters_enhanced(query_lower)
    
    if not filters:
        return None
    
    # Step 3: Process the query with all filters
    return _process_statistical_lookup_with_unlimited_filters(df, stat_operation, target_col_hint, filters)

def _extract_all_filters_enhanced(query_lower):
    """Extract all filter conditions from the query - Enhanced for unlimited filters"""
    
    filters = []
    
    # Pattern 1: "for column value" format (handles dates automatically)
    for_pattern = r'for\s+(\w+)\s+([^\s]+)'
    for_matches = re.finditer(for_pattern, query_lower)
    
    for match in for_matches:
        col_hint, value = match.groups()
        filters.append({
            'column_hint': col_hint,
            'value': value,
            'operator': '=',
            'type': 'for'
        })
    
    # Pattern 2: "where column operator value" format (COMPREHENSIVE)
    where_patterns = [
        # Equality patterns (handles 'is' and 'equals')
        r'where\s+(\w+)\s*[=:]\s*([^\s]+)',
        r'where\s+(\w+)\s+(?:is|equals?|is\s+equal\s+to)\s+([^\s]+)',
        
        # Contains patterns
        r'where\s+(\w+)\s+(?:contains?|includes?)\s+([^\s]+)',
        
        # Comparison patterns
        r'where\s+(\w+)\s+(?:>|greater\s+than)\s+([^\s]+)',
        r'where\s+(\w+)\s+(?:<|less\s+than)\s+([^\s]+)',
        r'where\s+(\w+)\s+(?:>=|greater\s+than\s+or\s+equal\s+to)\s+([^\s]+)',
        r'where\s+(\w+)\s+(?:<=|less\s+than\s+or\s+equal\s+to)\s+([^\s]+)',
        r'where\s+(\w+)\s+(?:!=|not\s+equal\s+to|is\s+not)\s+([^\s]+)',
        
        # Date range patterns
        r'where\s+(\w+)\s+(?:between|from)\s+([^\s]+)\s+(?:and|to)\s+([^\s]+)',
        r'where\s+(\w+)\s+(?:after|since)\s+([^\s]+)',
        r'where\s+(\w+)\s+(?:before|until)\s+([^\s]+)',
    ]
    
    for pattern in where_patterns:
        matches = re.finditer(pattern, query_lower)
        for match in matches:
            groups = match.groups()
            
            if len(groups) == 3:  # Date range pattern
                col_hint, start_value, end_value = groups
                filters.append({
                    'column_hint': col_hint,
                    'value': start_value,
                    'operator': '>=',
                    'type': 'where'
                })
                filters.append({
                    'column_hint': col_hint,
                    'value': end_value,
                    'operator': '<=',
                    'type': 'where'
                })
            elif len(groups) == 2:  # Regular pattern
                col_hint, value = groups
                
                # Determine operator from pattern
                if 'contains' in pattern or 'includes' in pattern:
                    operator = 'contains'
                elif '>=' in pattern or 'greater_than_or_equal' in pattern:
                    operator = '>='
                elif '<=' in pattern or 'less_than_or_equal' in pattern:
                    operator = '<='
                elif '>' in pattern or 'greater_than' in pattern:
                    operator = '>'
                elif '<' in pattern or 'less_than' in pattern:
                    operator = '<'
                elif '!=' in pattern or 'not_equal' in pattern or 'is_not' in pattern:
                    operator = '!='
                elif 'after' in pattern or 'since' in pattern:
                    operator = '>'
                elif 'before' in pattern or 'until' in pattern:
                    operator = '<'
                else:
                    operator = '='  # Default for 'is', 'equals', '='
                
                filters.append({
                    'column_hint': col_hint,
                    'value': value,
                    'operator': operator,
                    'type': 'where'
                })
    
    # Pattern 3: "and column operator value" format (COMPREHENSIVE)
    and_patterns = [
        # Equality patterns
        r'and\s+(\w+)\s*[=:]\s*([^\s]+)',
        r'and\s+(\w+)\s+(?:is|equals?|is\s+equal\s+to)\s+([^\s]+)',
        
        # Contains patterns
        r'and\s+(\w+)\s+(?:contains?|includes?)\s+([^\s]+)',
        
        # Comparison patterns
        r'and\s+(\w+)\s+(?:>|greater\s+than)\s+([^\s]+)',
        r'and\s+(\w+)\s+(?:<|less\s+than)\s+([^\s]+)',
        r'and\s+(\w+)\s+(?:>=|greater\s+than\s+or\s+equal\s+to)\s+([^\s]+)',
        r'and\s+(\w+)\s+(?:<=|less\s+than\s+or\s+equal\s+to)\s+([^\s]+)',
        r'and\s+(\w+)\s+(?:!=|not\s+equal\s+to|is\s+not)\s+([^\s]+)',
        
        # Date patterns
        r'and\s+(\w+)\s+(?:after|since)\s+([^\s]+)',
        r'and\s+(\w+)\s+(?:before|until)\s+([^\s]+)',
    ]
    
    for pattern in and_patterns:
        matches = re.finditer(pattern, query_lower)
        for match in matches:
            col_hint, value = match.groups()
            
            # Determine operator
            if 'contains' in pattern or 'includes' in pattern:
                operator = 'contains'
            elif '>=' in pattern or 'greater_than_or_equal' in pattern:
                operator = '>='
            elif '<=' in pattern or 'less_than_or_equal' in pattern:
                operator = '<='
            elif '>' in pattern or 'greater_than' in pattern:
                operator = '>'
            elif '<' in pattern or 'less_than' in pattern:
                operator = '<'
            elif '!=' in pattern or 'not_equal' in pattern or 'is_not' in pattern:
                operator = '!='
            elif 'after' in pattern or 'since' in pattern:
                operator = '>'
            elif 'before' in pattern or 'until' in pattern:
                operator = '<'
            else:
                operator = '='
            
            filters.append({
                'column_hint': col_hint,
                'value': value,
                'operator': operator,
                'type': 'and'
            })
    
    # Remove duplicates while preserving order
    unique_filters = []
    seen = set()
    
    for filter_item in filters:
        key = (filter_item['column_hint'], filter_item['value'], filter_item['operator'])
        if key not in seen:
            seen.add(key)
            unique_filters.append(filter_item)
    
    return unique_filters

def _process_statistical_lookup_with_unlimited_filters(df, stat_operation, target_col_hint, filters):
    """Process statistical lookup with unlimited filters"""
    
    # Find target column
    target_match = _find_best_column_match(target_col_hint, df)
    if not target_match['column']:
        return {
            'operation': 'unlimited_filter_lookup_error',
            'result_text': f"Could not find target column '{target_col_hint}'. Available columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}",
            'confidence': 0.3
        }
    
    target_column = target_match['column']
    
    # Process each filter
    processed_filters = []
    total_confidence = target_match['confidence']
    
    for filter_item in filters:
        # Find matching column
        col_match = _find_best_column_match(filter_item['column_hint'], df)
        
        if not col_match['column']:
            # Skip this filter if column not found, but continue with others
            continue
        
        processed_filters.append({
            'column': col_match['column'],
            'value': filter_item['value'],
            'operator': filter_item['operator'],
            'original_hint': filter_item['column_hint'],
            'confidence': col_match['confidence']
        })
        
        total_confidence += col_match['confidence']
    
    if not processed_filters:
        return {
            'operation': 'unlimited_filter_lookup_error',
            'result_text': f"Could not find any valid filter columns from: {[f['column_hint'] for f in filters]}",
            'confidence': 0.3
        }
    
    try:
        # Apply all filters sequentially
        filtered_df = df.copy()
        filters_applied = []
        
        for filter_item in processed_filters:
            column = filter_item['column']
            value = filter_item['value']
            operator = filter_item['operator']
            
            # Apply the filter based on operator
            if operator == '=':
                # Check if it's a date
                if re.match(r'\d{4}-\d{2}-\d{2}', value):
                    filtered_df = _apply_smart_date_filter(filtered_df, column, value, '=')
                    filters_applied.append(f"{column} = {value}")
                else:
                    filtered_df = _apply_smart_filter(filtered_df, column, value)
                    filters_applied.append(f"{column} = {value}")
            
            elif operator == '!=':
                if re.match(r'\d{4}-\d{2}-\d{2}', value):
                    # For dates, exclude that specific date
                    date_filtered = _apply_smart_date_filter(filtered_df, column, value, '=')
                    filtered_df = filtered_df[~filtered_df.index.isin(date_filtered.index)]
                    filters_applied.append(f"{column} != {value}")
                else:
                    filtered_df = filtered_df[filtered_df[column].astype(str).str.lower() != str(value).lower()]
                    filters_applied.append(f"{column} != {value}")
            
            elif operator == 'contains':
                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(value, case=False, na=False)]
                filters_applied.append(f"{column} contains '{value}'")
            
            elif operator in ['>', '<', '>=', '<=']:
                # Handle numeric and date comparisons
                if re.match(r'\d{4}-\d{2}-\d{2}', value):
                    # Date comparison
                    filtered_df = _apply_smart_date_filter(filtered_df, column, value, operator)
                    filters_applied.append(f"{column} {operator} {value}")
                else:
                    # Numeric comparison
                    try:
                        numeric_value = float(value)
                        if pd.api.types.is_numeric_dtype(filtered_df[column]):
                            if operator == '>':
                                filtered_df = filtered_df[filtered_df[column] > numeric_value]
                            elif operator == '<':
                                filtered_df = filtered_df[filtered_df[column] < numeric_value]
                            elif operator == '>=':
                                filtered_df = filtered_df[filtered_df[column] >= numeric_value]
                            elif operator == '<=':
                                filtered_df = filtered_df[filtered_df[column] <= numeric_value]
                            
                            filters_applied.append(f"{column} {operator} {numeric_value}")
                        else:
                            # Skip non-numeric comparison for non-numeric columns
                            continue
                    except ValueError:
                        # Skip invalid numeric comparisons
                        continue
        
        if len(filtered_df) == 0:
            return {
                'operation': 'unlimited_filter_lookup_no_data',
                'result_text': f"No records found for filters: {' AND '.join(filters_applied)}",
                'confidence': 0.8,
                'rows_found': 0,
                'filters_applied': filters_applied
            }
        
        # Apply statistical operation
        result = _apply_statistical_operation_robust(filtered_df, target_column, stat_operation)
        if 'error' in result:
            return result
        
        # Calculate final confidence
        avg_confidence = min(total_confidence / (len(processed_filters) + 1), 1.0)
        
        # Create result description
        filter_description = ' AND '.join(filters_applied)
        
        return {
            'operation': 'unlimited_filter_statistical_lookup',
            'stat_operation': stat_operation,
            'target_column': target_column,
            'filters': processed_filters,
            'result': result['value'],
            'result_text': f"{result['operation_text']} of {target_column} where {filter_description}: {result['formatted_value']}",
            'confidence': avg_confidence,
            'rows_found': len(filtered_df),
            'total_rows': len(df),
            'filters_applied': filters_applied,
            'total_filters': len(processed_filters)
        }
        
    except Exception as e:
        return {
            'operation': 'unlimited_filter_lookup_error',
            'result_text': f"Error processing unlimited filter lookup: {str(e)}",
            'confidence': 0.3
        }

def _apply_smart_date_filter(df, date_column, date_value, operator='='):
    """Apply date filter with smart date parsing and comparison"""
    
    try:
        # Parse the target date
        target_date = pd.to_datetime(date_value)
        
        # Ensure the date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
            try:
                df_filtered = df.copy()
                df_filtered[date_column] = pd.to_datetime(df_filtered[date_column], errors='coerce')
            except:
                # If conversion fails, try string comparison
                date_str = str(date_value)
                if operator == '=':
                    return df[df[date_column].astype(str).str.contains(date_str, na=False)]
                else:
                    return df[df.index == -1]  # Return empty
        else:
            df_filtered = df.copy()
        
        # Apply the date filter based on operator
        if operator == '=':
            # For equality, check if the date is on the same day
            mask = df_filtered[date_column].dt.date == target_date.date()
        elif operator == '>':
            mask = df_filtered[date_column] > target_date
        elif operator == '<':
            mask = df_filtered[date_column] < target_date
        elif operator == '>=':
            mask = df_filtered[date_column] >= target_date
        elif operator == '<=':
            mask = df_filtered[date_column] <= target_date
        else:
            mask = df_filtered[date_column].dt.date == target_date.date()
        
        return df_filtered[mask]
        
    except Exception as e:
        # Fallback to string comparison
        try:
            date_str = str(date_value)
            if operator == '=':
                return df[df[date_column].astype(str).str.contains(date_str, na=False)]
            else:
                return df[df.index == -1]  # Return empty dataframe
        except:
            return df[df.index == -1]  # Return empty dataframe

def _apply_statistical_operation_robust(df, target_column, stat_operation):
    """Apply statistical operation and return formatted result - ROBUST VERSION"""
    
    try:
        if stat_operation in ['sum', 'total']:
            if not pd.api.types.is_numeric_dtype(df[target_column]):
                return {
                    'error': True,
                    'operation': 'statistical_error',
                    'result_text': f"Cannot calculate sum of non-numeric column '{target_column}'. Try 'count of {target_column}' instead.",
                    'confidence': 0.9
                }
            value = df[target_column].sum()
            return {
                'value': value,
                'formatted_value': f"{value:,.2f}",
                'operation_text': "Sum"
            }
            
        elif stat_operation in ['average', 'avg', 'mean']:
            if not pd.api.types.is_numeric_dtype(df[target_column]):
                return {
                    'error': True,
                    'operation': 'statistical_error',
                    'result_text': f"Cannot calculate average of non-numeric column '{target_column}'. Try 'count of {target_column}' instead.",
                    'confidence': 0.9
                }
            value = df[target_column].mean()
            return {
                'value': value,
                'formatted_value': f"{value:,.2f}",
                'operation_text': "Average"
            }
            
        elif stat_operation == 'median':
            if not pd.api.types.is_numeric_dtype(df[target_column]):
                return {
                    'error': True,
                    'operation': 'statistical_error',
                    'result_text': f"Cannot calculate median of non-numeric column '{target_column}'. Try 'count of {target_column}' instead.",
                    'confidence': 0.9
                }
            value = df[target_column].median()
            return {
                'value': value,
                'formatted_value': f"{value:,.2f}",
                'operation_text': "Median"
            }
            
        elif stat_operation in ['max', 'maximum']:
            if not pd.api.types.is_numeric_dtype(df[target_column]):
                value = df[target_column].mode().iloc[0] if not df[target_column].mode().empty else 'N/A'
                return {
                    'value': value,
                    'formatted_value': str(value),
                    'operation_text': "Most common"
                }
            else:
                value = df[target_column].max()
                return {
                    'value': value,
                    'formatted_value': f"{value:,.2f}",
                    'operation_text': "Maximum"
                }
                
        elif stat_operation in ['min', 'minimum']:
            if not pd.api.types.is_numeric_dtype(df[target_column]):
                value_counts = df[target_column].value_counts()
                value = value_counts.index[-1] if len(value_counts) > 0 else 'N/A'
                return {
                    'value': value,
                    'formatted_value': str(value),
                    'operation_text': "Least common"
                }
            else:
                value = df[target_column].min()
                return {
                    'value': value,
                    'formatted_value': f"{value:,.2f}",
                    'operation_text': "Minimum"
                }
                
        elif stat_operation == 'count':
            value = len(df[target_column].dropna())
            return {
                'value': value,
                'formatted_value': f"{value:,}",
                'operation_text': "Count"
            }
            
        else:
            return {
                'error': True,
                'operation': 'statistical_error',
                'result_text': f"Unknown statistical operation: {stat_operation}",
                'confidence': 0.3
            }
            
    except Exception as e:
        return {
            'error': True,
            'operation': 'statistical_error',
            'result_text': f"Error applying statistical operation: {str(e)}",
            'confidence': 0.3
        }

def _process_simple_lookup(df, target_col_hint, filter_col_hint, filter_value):
    """Process simple value lookup operations - ENHANCED"""
    
    # Find matching columns
    target_match = _find_best_column_match(target_col_hint, df)
    filter_match = _find_best_column_match(filter_col_hint, df)
    
    if not target_match['column'] or not filter_match['column']:
        return _create_error_response(
            f"Could not find columns for '{target_col_hint}' or '{filter_col_hint}'",
            target_match, filter_match, df
        )
    
    target_column = target_match['column']
    filter_column = filter_match['column']
    
    try:
        # Apply filter (enhanced for dates)
        if re.match(r'\d{4}-\d{2}-\d{2}', filter_value):
            filtered_df = _apply_smart_date_filter(df, filter_column, filter_value, '=')
        else:
            filtered_df = _apply_smart_filter(df, filter_column, filter_value)
        
        if len(filtered_df) == 0:
            return {
                'operation': 'simple_lookup_no_data',
                'result_text': f"No records found for {filter_column} = {filter_value}",
                'confidence': 0.8,
                'rows_found': 0,
                'suggestion': f"Try checking if {filter_value} exists in {filter_column}"
            }
        
        # Get the value
        result_value = filtered_df[target_column].iloc[0]
        
        # Handle multiple matches
        if len(filtered_df) > 1:
            unique_values = filtered_df[target_column].nunique()
            if unique_values == 1:
                additional_info = f" (consistent across {len(filtered_df)} records)"
            else:
                additional_info = f" (first of {len(filtered_df)} records, {unique_values} unique values)"
        else:
            additional_info = ""
        
        # Calculate confidence
        confidence = min(target_match['confidence'] + filter_match['confidence'], 1.0)
        
        return {
            'operation': 'simple_lookup',
            'target_column': target_column,
            'filter_column': filter_column,
            'filter_value': filter_value,
            'result': result_value,
            'result_text': f"{target_column} for {filter_column} {filter_value}: {result_value}{additional_info}",
            'confidence': confidence,
            'rows_found': len(filtered_df),
            'unique_values': filtered_df[target_column].nunique() if len(filtered_df) > 1 else 1
        }
        
    except Exception as e:
        return {
            'operation': 'simple_lookup_error',
            'result_text': f"Error processing lookup: {str(e)}",
            'confidence': 0.3
        }

def _find_best_column_match(col_hint, df):
    """Find best matching column with confidence scoring - ENHANCED"""
    
    col_hint_clean = col_hint.lower().strip()
    matches = []
    
    for col in df.columns:
        col_clean = col.lower()
        score = 0
        match_type = ""
        
        # Exact match (highest score)
        if col_clean == col_hint_clean:
            score = 1.0
            match_type = "exact"
        
        # Exact match without underscores/spaces
        elif col_clean.replace('_', '').replace(' ', '') == col_hint_clean.replace('_', '').replace(' ', ''):
            score = 0.95
            match_type = "exact_normalized"
        
        # Column contains hint
        elif col_hint_clean in col_clean:
            score = 0.8
            match_type = "contains"
        
        # Hint contains column
        elif col_clean in col_hint_clean:
            score = 0.7
            match_type = "contained"
        
        # Partial word matching
        else:
            hint_words = set(col_hint_clean.replace('_', ' ').split())
            col_words = set(col_clean.replace('_', ' ').split())
            common_words = hint_words.intersection(col_words)
            
            if common_words:
                word_score = len(common_words) / max(len(hint_words), len(col_words))
                if word_score >= 0.5:
                    score = 0.6 * word_score
                    match_type = "partial_words"
        
        if score > 0:
            matches.append({
                'column': col,
                'confidence': score,
                'match_type': match_type
            })
    
    # Return best match
    if matches:
        best_match = max(matches, key=lambda x: x['confidence'])
        return best_match
    
    return {'column': None, 'confidence': 0.0, 'match_type': 'none'}

def _apply_smart_filter(df, filter_column, filter_value):
    """Apply filter with smart type handling - ENHANCED"""
    
    try:
        # Clean the filter value
        filter_value_clean = str(filter_value).strip().strip('\'"')
        
        # Try different matching strategies
        column_data = df[filter_column]
        
        # Strategy 1: Exact match (convert both to string)
        mask1 = column_data.astype(str).str.strip() == filter_value_clean
        
        # Strategy 2: Case-insensitive match
        mask2 = column_data.astype(str).str.strip().str.lower() == filter_value_clean.lower()
        
        # Strategy 3: Numeric comparison (if applicable)
        mask3 = pd.Series([False] * len(df))
        if pd.api.types.is_numeric_dtype(column_data):
            try:
                numeric_value = float(filter_value_clean)
                mask3 = column_data == numeric_value
            except ValueError:
                pass
        
        # Strategy 4: Contains match (for partial matching)
        mask4 = column_data.astype(str).str.contains(filter_value_clean, case=False, na=False)
        
        # Try strategies in order of preference
        for mask in [mask3, mask1, mask2]:  # Exact matches first
            if mask.any():
                return df[mask]
        
        # If no exact matches, try contains
        if mask4.any():
            return df[mask4]
        
        # No matches found
        return df[df.index == -1]  # Empty dataframe with same structure
        
    except Exception as e:
        return df[df.index == -1]  # Return empty dataframe on error

def _create_error_response(message, target_match, filter_match, df):
    """Create helpful error response with suggestions - ENHANCED"""
    
    suggestions = []
    
    # Suggest similar column names
    if target_match['column'] is None:
        similar_cols = [col for col in df.columns if any(word in col.lower() for word in message.split())]
        if similar_cols:
            suggestions.append(f"Similar columns found: {', '.join(similar_cols[:3])}")
    
    if filter_match['column'] is None:
        similar_cols = [col for col in df.columns if any(word in col.lower() for word in message.split())]
        if similar_cols:
            suggestions.append(f"Available filter columns: {', '.join(similar_cols[:3])}")
    
    # Add available columns info
    suggestions.append(f"Available columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
    
    suggestion_text = ". ".join(suggestions) if suggestions else "Check your column names and try again."
    
    return {
        'operation': 'lookup_error',
        'result_text': f"{message}. {suggestion_text}",
        'confidence': 0.3,
        'suggestions': suggestions
    }

def find_column_match(col_hint, df):
    """Simple wrapper for backward compatibility"""
    match = _find_best_column_match(col_hint, df)
    return match['column']       

def detect_statistical_query(query, df):
    """Detect and compute statistical operations directly"""
    
    query_lower = query.lower()
    
    # Skip if visualization keywords present
    viz_keywords = ['plot', 'draw', 'chart', 'graph', 'show', 'visualize', 'display']
    if any(keyword in query_lower for keyword in viz_keywords):
        return None
    
    # Statistical operations
    stat_operations = {
        'average': ['average', 'avg', 'mean'],
        'sum': ['sum', 'total', 'add'],
        'count': ['count', 'number of', 'how many'],
        'max': ['maximum', 'max', 'highest', 'largest'],
        'min': ['minimum', 'min', 'lowest', 'smallest'],
        'median': ['median', 'middle'],
        'std': ['standard deviation', 'std', 'stddev'],
        'distinct': ['distinct', 'unique'],
        'mode': ['mode', 'most common'],
    }
    
    # Find operation
    operation = None
    for op, keywords in stat_operations.items():
        if any(keyword in query_lower for keyword in keywords):
            operation = op
            break
    
    if not operation:
        return None
    
    # Find target column
    target_column = None
    for col in df.columns:
        col_variations = [col.lower(), col.lower().replace('_', ' ')]
        if any(variation in query_lower for variation in col_variations):
            target_column = col
            break
    
    # Default logic based on operation type
    if not target_column:
        if operation in ['distinct', 'count', 'mode']:
            # For distinct/count/mode, can use any column
            target_column = df.columns[0] if len(df.columns) > 0 else None
        else:
            # For numeric operations, prefer numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            target_column = numeric_cols[0] if len(numeric_cols) > 0 else None
    
    if not target_column:
        return None
    
    # Enhanced validation: some operations work on any column type
    if operation not in ['distinct', 'count', 'mode'] and not pd.api.types.is_numeric_dtype(df[target_column]):
        return None
    
    try:
        # Detect and apply filters FIRST
        working_df = df.copy()
        
        # Enhanced filter detection for "starting with letter X"
        filter_patterns = [
            (r'(\w+)\s+(?:starting\s+with|begins?\s+with)\s+(?:letter\s+)?([a-zA-Z])', 'starts_with'),
            (r'(\w+)\s+(?:ending\s+with|ends?\s+with)\s+(?:letter\s+)?([a-zA-Z])', 'ends_with'),
            (r'(\w+)\s+(?:contains?|includes?)\s+(["\']?)([^"\']+)\2', 'contains'),
            (r'(\w+)\s+(?:equals?|is)\s+(["\']?)([^"\']+)\2', 'equals'),
        ]
        
        filters_applied = []
        for pattern, filter_type in filter_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                col_hint, value = match.groups()
                
                # Find matching column (enhanced matching)
                matching_col = None
                for col in df.columns:
                    if (col_hint.lower() in col.lower() or col.lower() in col_hint.lower() or
                        col_hint.lower().replace('_', '') in col.lower().replace('_', '') or
                        col.lower().replace('_', '') in col_hint.lower().replace('_', '')):
                        matching_col = col
                        break
                
                if matching_col and matching_col in df.columns:
                    if filter_type == 'starts_with':
                        working_df = working_df[working_df[matching_col].astype(str).str.upper().str.startswith(value.upper())]
                        filters_applied.append(f"{matching_col} starts with '{value.upper()}'")
                    elif filter_type == 'ends_with':
                        working_df = working_df[working_df[matching_col].astype(str).str.upper().str.endswith(value.upper())]
                        filters_applied.append(f"{matching_col} ends with '{value.upper()}'")
                    elif filter_type == 'contains':
                        working_df = working_df[working_df[matching_col].astype(str).str.contains(value, case=False, na=False)]
                        filters_applied.append(f"{matching_col} contains '{value}'")
                    elif filter_type == 'equals':
                        working_df = working_df[working_df[matching_col].astype(str).str.lower() == value.lower()]
                        filters_applied.append(f"{matching_col} equals '{value}'")
        
        # Compute statistic on filtered data
        if operation == 'average':
            result = working_df[target_column].mean()
            result_text = f"Average {target_column}: {result:,.2f}"
        elif operation == 'sum':
            result = working_df[target_column].sum()
            result_text = f"Total {target_column}: {result:,.2f}"
        elif operation == 'count':
            result = len(working_df[target_column].dropna())
            if filters_applied:
                result_text = f"Count of {target_column} where {', '.join(filters_applied)}: {result:,}"
            else:
                result_text = f"Count of {target_column}: {result:,}"
        elif operation == 'distinct':
            result = working_df[target_column].nunique()
            if filters_applied:
                result_text = f"Count of distinct {target_column} where {', '.join(filters_applied)}: {result:,}"
            else:
                result_text = f"Count of distinct {target_column}: {result:,}"
        elif operation == 'max':
            result = working_df[target_column].max()
            result_text = f"Maximum {target_column}: {result:,.2f}"
        elif operation == 'min':
            result = working_df[target_column].min()
            result_text = f"Minimum {target_column}: {result:,.2f}"
        elif operation == 'median':
            result = working_df[target_column].median()
            result_text = f"Median {target_column}: {result:,.2f}"
        elif operation == 'std':
            result = working_df[target_column].std()
            result_text = f"Standard deviation of {target_column}: {result:,.2f}"
        elif operation == 'mode':
            mode_val = working_df[target_column].mode()
            result = mode_val.iloc[0] if len(mode_val) > 0 else 'N/A'
            result_text = f"Most common {target_column}: {result}"
        
        return {
            'operation': operation,
            'column': target_column,
            'result': result,
            'result_text': result_text,
            'confidence': 1.0,
            'filters_applied': filters_applied,
            'filtered_rows': len(working_df),
            'original_rows': len(df)
        }
    

        
    except Exception as e:
        print(f"Statistical query failed: {e}")  # Debug line
        return None

@track_performance("Statistical Analysis")
def perform_statistical_analysis(df, column1, column2=None):
    """Comprehensive statistical analysis"""
    
    results = {}
    
    if column2 is None:
        # Single column analysis
        if pd.api.types.is_numeric_dtype(df[column1]):
            data = df[column1].dropna()
            results['descriptive_stats'] = {
                'count': len(data),
                'mean': float(data.mean()),
                'median': float(data.median()),
                'std': float(data.std()),
                'min': float(data.min()),
                'max': float(data.max()),
                'skewness': float(stats.skew(data)),
                'kurtosis': float(stats.kurtosis(data))
            }
    else:
        # Two column analysis
        df_clean = df[[column1, column2]].dropna()
        if len(df_clean) > 3 and pd.api.types.is_numeric_dtype(df_clean[column1]) and pd.api.types.is_numeric_dtype(df_clean[column2]):
            correlation, p_value = stats.pearsonr(df_clean[column1], df_clean[column2])
            results['correlation'] = {
                'pearson_coefficient': float(correlation),
                'p_value': float(p_value),
                'is_significant': p_value < 0.05,
                'strength': 'strong' if abs(correlation) > 0.7 else 'moderate' if abs(correlation) > 0.3 else 'weak'
            }
    
    return results

@track_performance("Outlier Detection")
def detect_outliers(df, column, method='iqr'):
    """Detect outliers using specified method - FIXED"""
    
    if not pd.api.types.is_numeric_dtype(df[column]):
        return None, f"Column '{column}' is not numeric"
    
    data = df[column].dropna()
    
    if len(data) < 4:
        return None, f"Not enough data for outlier detection (need at least 4 values)"
    
    try:
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
        else:
            # Z-score method
            z_scores = np.abs(stats.zscore(data))
            outlier_indices = data.index[z_scores > 3]
            outlier_mask = df.index.isin(outlier_indices)
        
        outliers = df[outlier_mask]
        
        return {
            'outliers': outliers,
            'outlier_count': len(outliers),
            'outlier_percentage': len(outliers) / len(df) * 100,
            'method_used': method,
            'bounds': {
                'lower': float(lower_bound) if method == 'iqr' else None,
                'upper': float(upper_bound) if method == 'iqr' else None
            }
        }, "Outlier detection completed successfully"
        
    except Exception as e:
        logger.error(f"Outlier detection failed: {e}")
        return None, f"Outlier detection failed: {str(e)}"

@track_performance("Clustering")
def perform_clustering(df, n_clusters=3, features=None):
    """Perform K-means clustering - FIXED"""
    
    # Get numeric features
    if features is None:
        features = df.select_dtypes(include=[np.number]).columns.tolist()[:4]
    else:
        # Filter to only numeric features
        features = [f for f in features if f in df.columns and pd.api.types.is_numeric_dtype(df[f])]
    
    if len(features) < 2:
        return None, "Need at least 2 numeric features for clustering"
    
    # Clean data
    cluster_data = df[features].dropna()
    
    if len(cluster_data) < n_clusters:
        return None, f"Not enough data for {n_clusters} clusters (need at least {n_clusters} rows)"
    
    try:
        # Scale features
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(cluster_data)
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(scaled_data)
        
        # Create result dataframe
        result_df = cluster_data.copy()
        result_df['Cluster'] = clusters
        
        # Calculate cluster statistics
        cluster_stats = {}
        for i in range(n_clusters):
            cluster_data_i = result_df[result_df['Cluster'] == i]
            cluster_stats[f'Cluster_{i}'] = {
                'size': len(cluster_data_i),
                'percentage': len(cluster_data_i) / len(result_df) * 100,
                'center': cluster_data_i[features].mean().to_dict()
            }
        
        # Calculate silhouette score
        try:
            from sklearn.metrics import silhouette_score
            silhouette_avg = silhouette_score(scaled_data, clusters)
        except:
            silhouette_avg = None
        
        return {
            'clustered_data': result_df,
            'cluster_stats': cluster_stats,
            'silhouette_score': float(silhouette_avg) if silhouette_avg else None,
            'features_used': features,
            'scaler': scaler,
            'model': kmeans
        }, "Clustering completed successfully"
        
    except Exception as e:
        logger.error(f"Clustering failed: {e}")
        return None, f"Clustering failed: {str(e)}"

@track_performance("Distribution")   
def perform_data_distribution_analysis(df, column):
    """Analyze data distribution for a column - NEW FUNCTION"""
    
    if column not in df.columns:
        return None, f"Column '{column}' not found"
    
    try:
        data = df[column].dropna()
        
        if len(data) < 5:
            return None, "Not enough data for distribution analysis"
        
        if pd.api.types.is_numeric_dtype(data):
            # Numeric distribution analysis
            stats_dict = {
                'count': len(data),
                'mean': float(data.mean()),
                'median': float(data.median()),
                'std': float(data.std()),
                'min': float(data.min()),
                'max': float(data.max()),
                'q25': float(data.quantile(0.25)),
                'q75': float(data.quantile(0.75)),
                'skewness': float(stats.skew(data)),
                'kurtosis': float(stats.kurtosis(data))
            }
            
            # Test for normality
            try:
                shapiro_stat, shapiro_p = stats.shapiro(data.sample(min(5000, len(data))))
                stats_dict['shapiro_test'] = {
                    'statistic': float(shapiro_stat),
                    'p_value': float(shapiro_p),
                    'is_normal': shapiro_p > 0.05
                }
            except:
                stats_dict['shapiro_test'] = None
            
            return {
                'type': 'numeric',
                'statistics': stats_dict,
                'distribution_type': 'normal' if stats_dict.get('shapiro_test', {}).get('is_normal', False) else 'non-normal'
            }, "Distribution analysis completed"
            
        else:
            # Categorical distribution analysis
            value_counts = data.value_counts()
            
            return {
                'type': 'categorical',
                'statistics': {
                    'count': len(data),
                    'unique_values': len(value_counts),
                    'most_frequent': str(value_counts.index[0]),
                    'most_frequent_count': int(value_counts.iloc[0]),
                    'least_frequent': str(value_counts.index[-1]),
                    'least_frequent_count': int(value_counts.iloc[-1])
                },
                'value_counts': value_counts.head(10).to_dict()
            }, "Distribution analysis completed"
            
    except Exception as e:
        logger.error(f"Distribution analysis failed: {e}")
        return None, f"Distribution analysis failed: {str(e)}"

# ============================================================================
# 7. 📄 PDF PROCESSING
# ============================================================================
@enhanced_error_handling
def extract_comprehensive_pdf_content(pdf_file):
    """Extract PDF content using FastPDFAgent - UPDATED VERSION"""
    
    if not PDF_PROCESSING_AVAILABLE:
        st.error("PDF processing libraries not available")
        return None
    
    # Initialize FastPDFAgent with Ollama
    pdf_agent = AdvancedPDFProcessor(
        ollama_client=AI_MODELS.get('ollama'),
        ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
    )
    
    with st.spinner("🔄 Processing PDF document..."):
        content = pdf_agent.process_pdf_fast(pdf_file)
    
    if content and content['status'] == 'success':
        # Display processing info
        metadata = content.get('metadata', {})
        processing_time = metadata.get('processing_time', 0)
        
        st.success(f"✅ PDF processed in {processing_time:.2f} seconds")
        
        # Show what was extracted
        chunks_count = metadata.get('total_chunks', 0)
        tables_count = metadata.get('total_tables', 0)
        images_count = metadata.get('total_images', 0)
        
        info_parts = []
        if chunks_count > 0:
            info_parts.append(f"{chunks_count} text chunks")
        if tables_count > 0:
            info_parts.append(f"{tables_count} tables")
        if images_count > 0:
            info_parts.append(f"{images_count} images")
        
        if info_parts:
            st.info(f"📄 Extracted: {', '.join(info_parts)}")
        
        # Store the PDF agent in session state for Q&A
        st.session_state['pdf_agent'] = pdf_agent
        
        return content
    
    elif content and content['status'] == 'error':
        st.error(f"❌ PDF processing failed: {content.get('error', 'Unknown error')}")
        return None
    
    else:
        st.error("❌ PDF processing failed: Unknown error")
        return None
    
def handle_pdf_file_upload(uploaded_file):
    """Handle PDF file upload - Updated version"""
    
    # Process the PDF
    pdf_content = extract_comprehensive_pdf_content(uploaded_file)
    
    if pdf_content:
        # Store in session state
        st.session_state.current_pdf_content = pdf_content
        st.session_state.file_type = 'pdf'
        st.session_state.current_df = None
        
        # Display summary metrics
        metadata = pdf_content.get('metadata', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Text Chunks", metadata.get('total_chunks', 0))
        with col2:
            st.metric("Tables Found", metadata.get('total_tables', 0))
        with col3:
            st.metric("Images", metadata.get('total_images', 0))
        with col4:
            st.metric("Content Length", f"{metadata.get('content_length', 0):,} chars")
        
        # Add Q&A interface
        st.markdown("---")
        display_pdf_qa_section(pdf_content)
        
        # Add document explorer
        with st.expander("🔍 Document Explorer"):
            display_pdf_explorer(pdf_content)
        
        return True
    
    return False

def display_pdf_qa_section(pdf_content):
    """Interactive ChatGPT-style Q&A interface for PDF documents - OPTIMIZED"""

    if 'pdf_agent' not in st.session_state:
        st.warning("PDF agent not available for Q&A")
        return

    pdf_agent = st.session_state['pdf_agent']

    st.markdown("### 💬 Ask Questions About Your PDF")
    
    # Initialize chat history ONCE
    if 'pdf_chat_history' not in st.session_state:
        st.session_state.pdf_chat_history = []

    # Clear button - optimized to prevent unnecessary reruns
    col_clear, col_info = st.columns([1, 4])
    with col_clear:
        if st.button("🗑️ Clear Conversation", key="clear_pdf_chat"):
            st.session_state.pdf_chat_history = []
            st.rerun()
    
    with col_info:
        if st.session_state.pdf_chat_history:
            st.caption(f"💬 {len(st.session_state.pdf_chat_history)//2} questions asked")

    # Render existing conversation history (NO processing here)
    for i, msg in enumerate(st.session_state.pdf_chat_history):
        if msg['role'] == 'user':
            with st.chat_message("user"):
                st.markdown(msg['message'])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg['message'])
                # Add confidence indicator if available
                if 'confidence' in msg:
                    confidence = msg['confidence']
                    if confidence > 0.7:
                        st.caption("🟢 High confidence")
                    elif confidence > 0.4:
                        st.caption("🟡 Medium confidence") 
                    else:
                        st.caption("🔴 Low confidence")

    # Suggested sample questions (dynamic but cached)
    sample_questions = [
        "What is the main topic of this document?",
        "Summarize the key findings.",
        "What information is in the tables?",
        "Are there any important statistics?",
        "What are the main conclusions?"
    ]
    
    # Add table-specific question if tables exist
    if pdf_content.get('tables'):
        sample_questions.insert(2, "What data is shown in the tables?")

    # Suggested questions with better UX
    with st.expander("💡 Try a suggested question", expanded=len(st.session_state.pdf_chat_history) == 0):
        cols = st.columns(2)
        for i, q in enumerate(sample_questions[:4]):
            if cols[i % 2].button(q, key=f"sugg_q_{i}", use_container_width=True):
                # Process the suggested question
                _process_pdf_question(q, pdf_agent, pdf_content)
                st.rerun()

    # Chat input box - optimized flow
    if prompt := st.chat_input("Ask a question about your PDF"):
        _process_pdf_question(prompt, pdf_agent, pdf_content)
        st.rerun()
 
def _process_pdf_question(question: str, pdf_agent, pdf_content):
    """Helper function to process PDF questions without reprocessing PDF"""
    
    # Validate inputs
    if not question or not question.strip():
        return
    
    # Add user message to chat history
    st.session_state.pdf_chat_history.append({
        'role': 'user', 
        'message': question.strip()
    })
    
    try:
        # Process question using EXISTING pdf_content (no reprocessing!)
        with st.spinner("🤖 Thinking..."):
            # Use the already processed PDF content
            answer_result = pdf_agent.answer_question(question.strip(), pdf_content)
        
        # Extract response details
        response = answer_result.get('answer', "I couldn't find that information.")
        confidence = answer_result.get('confidence', 0.0)
        method = answer_result.get('method', 'unknown')
        
        # Add assistant message with metadata
        assistant_msg = {
            'role': 'assistant', 
            'message': response,
            'confidence': confidence,
            'method': method
        }
        
        # Add page references if available
        if answer_result.get('relevant_pages'):
            pages_str = ", ".join(map(str, sorted(answer_result['relevant_pages'])))
            assistant_msg['message'] += f"\n\n*Referenced pages: {pages_str}*"
        
        st.session_state.pdf_chat_history.append(assistant_msg)
        
        # Log the interaction (optional)
        logger.info(f"PDF Q&A: Question processed with {confidence:.2f} confidence")
        
    except Exception as e:
        # Handle errors gracefully
        error_msg = f"Sorry, I encountered an error processing your question: {str(e)}"
        st.session_state.pdf_chat_history.append({
            'role': 'assistant', 
            'message': error_msg,
            'confidence': 0.0,
            'method': 'error'
        })
        logger.error(f"PDF Q&A error: {e}")

# ============================================================================
# 8. 🔧 TAPAS INTEGRATION
# ============================================================================
##FALLBACK PLACE HOLDER
# ==================================================================================
# 9. 🎯 MAIN QUERY PROCESSING ENGINE WITH PREDICTIVE MODELING - Master Orchestrator    "analytics_project"
# ==================================================================================

def _parse_visualization_query_with_unlimited_filters(query, df):
    """Parse complex visualization queries with statistical operations and unlimited filters"""
    
    query_lower = query.lower().strip()
    
    # Step 1: Extract chart type
    chart_type = 'bar'  # default
    if 'line' in query_lower or 'trend' in query_lower:
        chart_type = 'line'
    elif 'pie' in query_lower:
        chart_type = 'pie'
    elif 'scatter' in query_lower:
        chart_type = 'scatter'
    elif 'stacked' in query_lower:
        chart_type = 'stacked_bar'
    
    # Step 2: Extract statistical operation and target column
    stat_match = re.search(r'(sum|total|average|avg|mean|max|maximum|min|minimum|count|median)\s+(?:of\s+)?(\w+)', query_lower)
    
    if not stat_match:
        return None
    
    stat_operation = stat_match.group(1)
    target_col_hint = stat_match.group(2)
    
    # Step 3: Extract grouping column (by X)
    group_match = re.search(r'by\s+(\w+)', query_lower)
    group_col_hint = group_match.group(1) if group_match else None
    
    if not group_col_hint:
        return None
    
    # Step 4: Extract all filters using the enhanced function
    filters = _extract_all_filters_enhanced(query_lower)
    
    # Step 5: Find matching columns
    target_match = _find_best_column_match(target_col_hint, df)
    group_match = _find_best_column_match(group_col_hint, df)
    
    if not target_match['column'] or not group_match['column']:
        return None
    
    target_column = target_match['column']
    group_column = group_match['column']
    
    # Step 6: Apply all filters using the unlimited filter system
    try:
        filtered_df = df.copy()
        filters_applied = []
        
        for filter_item in filters:
            col_match = _find_best_column_match(filter_item['column_hint'], df)
            if not col_match['column']:
                continue
            
            column = col_match['column']
            value = filter_item['value']
            operator = filter_item['operator']
            
            # Apply the filter based on operator
            if operator == '=':
                if re.match(r'\d{4}-\d{2}-\d{2}', value):
                    filtered_df = _apply_smart_date_filter(filtered_df, column, value, '=')
                else:
                    filtered_df = _apply_smart_filter(filtered_df, column, value)
                filters_applied.append(f"{column} = {value}")
            
            elif operator == 'contains':
                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(value, case=False, na=False)]
                filters_applied.append(f"{column} contains '{value}'")
            
            elif operator in ['>', '<', '>=', '<=']:
                # Handle numeric and date comparisons
                if re.match(r'\d{4}-\d{2}-\d{2}', value):
                    filtered_df = _apply_smart_date_filter(filtered_df, column, value, operator)
                    filters_applied.append(f"{column} {operator} {value}")
                else:
                    try:
                        numeric_value = float(value)
                        if pd.api.types.is_numeric_dtype(filtered_df[column]):
                            if operator == '>':
                                filtered_df = filtered_df[filtered_df[column] > numeric_value]
                            elif operator == '<':
                                filtered_df = filtered_df[filtered_df[column] < numeric_value]
                            elif operator == '>=':
                                filtered_df = filtered_df[filtered_df[column] >= numeric_value]
                            elif operator == '<=':
                                filtered_df = filtered_df[filtered_df[column] <= numeric_value]
                            
                            filters_applied.append(f"{column} {operator} {numeric_value}")
                        else:
                            continue
                    except ValueError:
                        continue
        
        if len(filtered_df) == 0:
            return {
                'chart': None,
                'message': f"No data found for the specified filters: {', '.join(filters_applied)}",
                'confidence': 0.3,
                'filters_applied': filters_applied,
                'total_filters': len(filters)
            }
        
        # Step 7: Apply statistical aggregation
        if stat_operation in ['sum', 'total']:
            if not pd.api.types.is_numeric_dtype(filtered_df[target_column]):
                return None
            aggregated_df = filtered_df.groupby(group_column)[target_column].sum().reset_index()
            y_title = f"Sum of {target_column}"
            
        elif stat_operation in ['average', 'avg', 'mean']:
            if not pd.api.types.is_numeric_dtype(filtered_df[target_column]):
                return None
            aggregated_df = filtered_df.groupby(group_column)[target_column].mean().reset_index()
            y_title = f"Average {target_column}"
            
        elif stat_operation == 'count':
            aggregated_df = filtered_df.groupby(group_column)[target_column].count().reset_index()
            y_title = f"Count of {target_column}"
            
        elif stat_operation in ['max', 'maximum']:
            if not pd.api.types.is_numeric_dtype(filtered_df[target_column]):
                return None
            aggregated_df = filtered_df.groupby(group_column)[target_column].max().reset_index()
            y_title = f"Maximum {target_column}"
            
        elif stat_operation in ['min', 'minimum']:
            if not pd.api.types.is_numeric_dtype(filtered_df[target_column]):
                return None
            aggregated_df = filtered_df.groupby(group_column)[target_column].min().reset_index()
            y_title = f"Minimum {target_column}"
            
        elif stat_operation == 'median':
            if not pd.api.types.is_numeric_dtype(filtered_df[target_column]):
                return None
            aggregated_df = filtered_df.groupby(group_column)[target_column].median().reset_index()
            y_title = f"Median {target_column}"
        
        # Step 8: Create visualization
        fig = _create_enhanced_chart_with_unlimited_filters(aggregated_df, group_column, target_column, chart_type, y_title)
        
        # Step 9: Generate descriptive message
        filter_desc = f" with {len(filters_applied)} filters applied" if filters_applied else ""
        message = f"{chart_type.title()} chart showing {y_title} by {group_column}{filter_desc} ({len(aggregated_df)} categories)"
        
        return {
            'chart': fig,
            'message': message,
            'confidence': 0.9,
            'filters_applied': filters_applied,
            'filtered_rows': len(filtered_df),
            'aggregated_rows': len(aggregated_df),
            'total_filters': len(filters_applied)
        }
        
    except Exception as e:
        logger.error(f"Visualization with unlimited filters failed: {e}")
        return None

def _create_enhanced_chart_with_unlimited_filters(df, x_column, y_column, chart_type, y_title):
    """Create enhanced chart with professional styling for unlimited filter queries"""
    
    # import plotly.express as px
    # import plotly.graph_objects as go
    
    # Create the chart based on type
    if chart_type == 'bar':
        fig = px.bar(df, x=x_column, y=y_column, 
                    title=f"{y_title} by {x_column}")
        fig.update_traces(marker_color='#3498db', textfont={'color': '#000000', 'size': 12})
        
        
    elif chart_type == 'stacked_bar':
        fig = px.bar(df, x=x_column, y=y_column, 
                    title=f"{y_title} by {x_column}")
        fig.update_traces(marker_color='#3498db', textfont={'color': '#000000', 'size': 12})
        
    elif chart_type == 'line':
        # Sort data for better line visualization
        df_sorted = df.sort_values(x_column)
        fig = px.line(df_sorted, x=x_column, y=y_column, 
                     title=f"{y_title} by {x_column}", markers=True)
        fig.update_traces(line_color='#3498db', marker_size=8)
        
    elif chart_type == 'pie':
        fig = px.pie(df, names=x_column, values=y_column, 
                    title=f"{y_title} Distribution by {x_column}")
        
    elif chart_type == 'scatter':
        fig = px.scatter(df, x=x_column, y=y_column, 
                        title=f"{y_title} vs {x_column}")
        fig.update_traces(marker_color='#3498db', marker_size=10)
        
    else:  # default to bar
        fig = px.bar(df, x=x_column, y=y_column, 
                    title=f"{y_title} by {x_column}")
        fig.update_traces(marker_color='#3498db')
    
    # Apply professional styling
    fig.update_layout(
        height=600,
        margin=dict(l=80, r=80, t=120, b=100),
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50', 'family': 'Arial, sans-serif'}
        },
        xaxis={
            'title': x_column.replace('_', ' ').title(),
            'title_font': {'size': 14, 'color': '#34495e'},
            'tickfont': {'size': 11, 'color': '#000000'},
            'tickangle': -45 if len(df) > 8 else 0
        },
        yaxis={
            'title': y_title,
            'title_font': {'size': 14, 'color': '#34495e'},
            'tickfont': {'size': 11, 'color': '#000000'}
        },
        plot_bgcolor='rgba(248, 249, 250, 0.8)',
        paper_bgcolor='white',
        font={'family': 'Arial, sans-serif', 'size': 12}
    )
    
    # Add value labels on bars if not too many categories
    if chart_type in ['bar', 'stacked_bar'] and len(df) <= 12:
        fig.update_traces(texttemplate='%{y:,.0f}', textposition='outside',textfont={'color': '#000000', 'size': 12})
    
    # Add data count annotation
    fig.add_annotation(
        text=f"📊 {len(df)} categories",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        font=dict(size=10, color='#7f8c8d'),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#bdc3c7",
        borderwidth=1
    )
    
    return fig

@track_performance("AI Query Processing")
def process_enhanced_query(df, query, conversation_history=None):
    """🎼 ORCHESTRATOR: Routes queries to specialist agents with intelligent fallbacks"""
    
    # === INPUT VALIDATION ===
    if not query or len(query.strip()) == 0:
        return {
            'answer': 'Please provide a valid query',
            'confidence': 0.0,
            'context': {'intent': 'unknown'},
            'method': 'validation_error'
        }
    
    # === INITIALIZE ORCHESTRATOR ===
    ollama_model = AI_MODELS.get('ollama_model', 'llama3.2')
    
    # The Conductor (Intent Understanding & Coordination)
    intent_agent = QueryIntentAgent(
        AI_MODELS['ollama'], 
        AI_MODELS['embed_model'],
        ollama_model
    )
    
    # === STEP 1: CONDUCTOR ANALYZES THE QUERY ===
    context = intent_agent.understand_query_with_context(query, df)
    
    base_result = {
        'context': context,
        'analysis_results': {},
        'ai_reasoning': context.get('reasoning', ''),
        'method': 'orchestrated'
    }

    lookup_result = detect_lookup_query(query, df)
    if lookup_result:
        return {
            **base_result,
            'answer': lookup_result['result_text'],
            'confidence': lookup_result['confidence'],
            'method': 'lookup_specialist',
            'operation_details': lookup_result
        }
    
    # === STEP 2: DELEGATE TO SPECIALISTS (Priority Order) ===
    
    # 🧮 STATISTICAL OPERATIONS SPECIALIST (First Chair - Highest Priority)
    # if context['intent'] in ['extremes', 'aggregation', 'counting'] and context['confidence'] > 0.7:
   # 🧮 STATISTICAL OPERATIONS SPECIALIST (First Chair - Highest Priority)
    if ((context['intent'] in ['extremes', 'aggregation', 'counting', 'categorical_analysis'] and 
        context['confidence'] > 0.7) or 
        any(word in query.lower() for word in ['distinct', 'unique'])) and \
    not any(viz_word in query.lower() for viz_word in ['plot', 'chart', 'graph', 'show', 'visualize', 'display']):
        try:
            # STEP 1: Detect filters from query
            filters_applied = []
            working_df = df.copy()
            
            # Enhanced filter detection patterns
            filter_patterns = [
                # Numeric filters
                (r'(\w+)\s+(?:is\s+)?(?:less\s+than|<|below)\s+(\d+(?:\.\d+)?)', 'less_than'),
                (r'(\w+)\s+(?:is\s+)?(?:greater\s+than|>|above)\s+(\d+(?:\.\d+)?)', 'greater_than'),
                (r'(\w+)\s+(?:is\s+)?(?:less\s+than\s+or\s+equal\s+to|<=)\s+(\d+(?:\.\d+)?)', 'less_equal'),
                (r'(\w+)\s+(?:is\s+)?(?:greater\s+than\s+or\s+equal\s+to|>=)\s+(\d+(?:\.\d+)?)', 'greater_equal'),
                (r'(\w+)\s+(?:is\s+)?(?:equals?|=)\s+(\d+(?:\.\d+)?)', 'equals'),
                (r'(\w+)\s+(?:is\s+)?(?:not\s+equals?|!=|<>)\s+(\d+(?:\.\d+)?)', 'not_equals'),
                (r'(\w+)\s+(?:is\s+)?(?:between)\s+(\d+(?:\.\d+)?)\s+(?:and)\s+(\d+(?:\.\d+)?)', 'between'),
                
                # String filters
                (r'(\w+)\s+(?:starting\s+with|begins?\s+with)\s+(?:letter\s+)?([a-zA-Z])', 'starts_with'),
                (r'(\w+)\s+(?:ending\s+with|ends?\s+with)\s+(?:letter\s+)?([a-zA-Z])', 'ends_with'),
                (r'(\w+)\s+(?:contains?|includes?)\s+["\']?([^"\']+)["\']?', 'contains'),
                (r'(\w+)\s+(?:equals?|is)\s+["\']([^"\']+)["\']', 'text_equals'),
                (r'(\w+)\s+(?:not\s+equals?|is\s+not)\s+["\']([^"\']+)["\']', 'text_not_equals'),
            ]
            
            query_lower = query.lower()
            
            # Apply filters
            for pattern, operation in filter_patterns:
                matches = re.finditer(pattern, query_lower)
                for match in matches:
                    if operation == 'between':
                        col_hint, val1, val2 = match.groups()
                        # Find matching column
                        matching_col = None
                        for col in df.columns:
                            if (col_hint in col.lower() or col.lower() in col_hint or
                                col_hint.replace('_', '') in col.lower().replace('_', '') or
                                col.lower().replace('_', '') in col_hint.replace('_', '')):
                                matching_col = col
                                break
                        
                        if matching_col and pd.api.types.is_numeric_dtype(df[matching_col]):
                            val1, val2 = float(val1), float(val2)
                            min_val, max_val = min(val1, val2), max(val1, val2)
                            working_df = working_df[(working_df[matching_col] >= min_val) & (working_df[matching_col] <= max_val)]
                            filters_applied.append(f"{matching_col} between {min_val} and {max_val}")
                    else:
                        col_hint, value = match.groups()
                        # Find matching column (enhanced matching)
                        matching_col = None
                        for col in df.columns:
                            if (col_hint in col.lower() or col.lower() in col_hint or
                                col_hint.replace('_', '') in col.lower().replace('_', '') or
                                col.lower().replace('_', '') in col_hint.replace('_', '')):
                                matching_col = col
                                break
                        
                        if matching_col and matching_col in df.columns:
                            # NUMERIC FILTERS
                            if operation in ['less_than', 'greater_than', 'less_equal', 'greater_equal', 'equals', 'not_equals'] and pd.api.types.is_numeric_dtype(df[matching_col]):
                                value = float(value)
                                
                                if operation == 'less_than':
                                    working_df = working_df[working_df[matching_col] < value]
                                    filters_applied.append(f"{matching_col} < {value}")
                                elif operation == 'greater_than':
                                    working_df = working_df[working_df[matching_col] > value]
                                    filters_applied.append(f"{matching_col} > {value}")
                                elif operation == 'less_equal':
                                    working_df = working_df[working_df[matching_col] <= value]
                                    filters_applied.append(f"{matching_col} <= {value}")
                                elif operation == 'greater_equal':
                                    working_df = working_df[working_df[matching_col] >= value]
                                    filters_applied.append(f"{matching_col} >= {value}")
                                elif operation == 'equals':
                                    working_df = working_df[working_df[matching_col] == value]
                                    filters_applied.append(f"{matching_col} = {value}")
                                elif operation == 'not_equals':
                                    working_df = working_df[working_df[matching_col] != value]
                                    filters_applied.append(f"{matching_col} != {value}")
                            
                            # STRING FILTERS
                            elif operation in ['starts_with', 'ends_with', 'contains', 'text_equals', 'text_not_equals']:
                                if operation == 'starts_with':
                                    working_df = working_df[working_df[matching_col].astype(str).str.upper().str.startswith(value.upper())]
                                    filters_applied.append(f"{matching_col} starts with '{value.upper()}'")
                                elif operation == 'ends_with':
                                    working_df = working_df[working_df[matching_col].astype(str).str.upper().str.endswith(value.upper())]
                                    filters_applied.append(f"{matching_col} ends with '{value.upper()}'")
                                elif operation == 'contains':
                                    working_df = working_df[working_df[matching_col].astype(str).str.contains(value, case=False, na=False)]
                                    filters_applied.append(f"{matching_col} contains '{value}'")
                                elif operation == 'text_equals':
                                    working_df = working_df[working_df[matching_col].astype(str).str.lower() == value.lower()]
                                    filters_applied.append(f"{matching_col} = '{value}'")
                                elif operation == 'text_not_equals':
                                    working_df = working_df[working_df[matching_col].astype(str).str.lower() != value.lower()]
                                    filters_applied.append(f"{matching_col} != '{value}'")
            
            # STEP 2: Find target column for the statistical operation
            target_column = context['entities'][0] if context['entities'] else None
            
            # If no target column from entities, find from query
            if not target_column:
                # Look for column names in query (excluding filter columns)
                filter_cols = [f.split()[0] for f in filters_applied]
                for col in df.columns:
                    if (col.lower() in query_lower and col not in filter_cols):
                        target_column = col
                        break
            
            # STEP 3: Perform statistical operation on filtered data
            if target_column and target_column in df.columns:
                operations = context.get('operations', [])

                # For counting operations, we can count any column (or just rows)
                if context['intent'] == 'counting' or 'count' in operations:
                    # Check if user wants unique/distinct count
                    if any(word in query.lower() for word in ['unique', 'distinct', 'different']):
                        result_value = working_df[target_column].nunique()
                        count_type = "unique"
                        if filters_applied:
                            answer = f"Count of unique {target_column} where {', '.join(filters_applied)}: {result_value:,}"
                        else:
                            answer = f"Count of unique {target_column}: {result_value:,}"
                    else:
                        result_value = len(working_df[target_column].dropna())
                        count_type = "total"
                        if filters_applied:
                            answer = f"Count of {target_column} where {', '.join(filters_applied)}: {result_value:,}"
                        else:
                            answer = f"Count of {target_column}: {result_value:,}"
                    
                    operation = 'count'
                    
                    # Track user preferences
                    if 'user_preferences' in st.session_state:
                        st.session_state.user_preferences['common_columns'].append(target_column)
                        if len(st.session_state.user_preferences['common_columns']) > 10:
                            st.session_state.user_preferences['common_columns'] = st.session_state.user_preferences['common_columns'][-10:]
                    
                    return {
                        **base_result,
                        'answer': answer,
                        'confidence': 1.0,
                        'method': 'statistical_specialist_with_filters',
                        'operation': operation,
                        'column': target_column,
                        'value': int(result_value),
                        'filters_applied': filters_applied,
                        'filtered_rows': len(working_df),
                        'original_rows': len(df)
                    }
                
                # For other operations, need numeric column
                elif pd.api.types.is_numeric_dtype(working_df[target_column]):
                    if 'max' in operations or any(word in query.lower() for word in ['maximum', 'max', 'highest', 'largest']):
                        result_value = working_df[target_column].max()
                        answer = f"Maximum {target_column}"
                        operation = 'max'
                    
                    elif 'min' in operations or any(word in query.lower() for word in ['minimum', 'min', 'lowest', 'smallest']):
                        result_value = working_df[target_column].min()
                        answer = f"Minimum {target_column}"
                        operation = 'min'
                    
                    elif 'mean' in operations or any(word in query.lower() for word in ['average', 'avg', 'mean']):
                        result_value = working_df[target_column].mean()
                        answer = f"Average {target_column}"
                        operation = 'mean'
                    
                    elif 'sum' in operations or any(word in query.lower() for word in ['sum', 'total']):
                        result_value = working_df[target_column].sum()
                        answer = f"Total {target_column}"
                        operation = 'sum'
                    
                    elif 'median' in operations or 'median' in query.lower():
                        result_value = working_df[target_column].median()
                        answer = f"Median {target_column}"
                        operation = 'median'
                    
                    else:
                        # Default based on intent
                        if context['intent'] == 'extremes':
                            result_value = working_df[target_column].max()
                            answer = f"Maximum {target_column}"
                            operation = 'max'
                        else:
                            result_value = working_df[target_column].mean()
                            answer = f"Average {target_column}"
                            operation = 'mean'
                    
                    # Add filter description to answer
                    if filters_applied:
                        answer += f" where {', '.join(filters_applied)}: {result_value:,.2f}"
                    else:
                        answer += f": {result_value:,.2f}"
                
                else:
                    return {
                        **base_result,
                        'answer': f"❌ Cannot perform statistical operations on non-numeric column '{target_column}'",
                        'confidence': 0.3,
                        'method': 'statistical_error'
                    }
                
                # Track user preferences
                if 'user_preferences' in st.session_state:
                    st.session_state.user_preferences['common_columns'].append(target_column)
                    if len(st.session_state.user_preferences['common_columns']) > 10:
                        st.session_state.user_preferences['common_columns'] = st.session_state.user_preferences['common_columns'][-10:]
                
                return {
                    **base_result,
                    'answer': answer,
                    'confidence': 1.0,
                    'method': 'statistical_specialist_with_filters',
                    'operation': operation,
                    'column': target_column,
                    'value': float(result_value),
                    'filters_applied': filters_applied,
                    'filtered_rows': len(working_df),
                    'original_rows': len(df)
                }
                
        except Exception as e:
            logger.error(f"Statistical specialist with filters failed: {e}")
    
    # 🎯 TABULAR DATA SPECIALIST (Second Chair)
    if context['confidence'] > 0.7 and context['intent'] in ['analyze', 'summarize', 'categorical_analysis']:
        try:
            tabular_agent = AgenticTabularProcessor(AI_MODELS['ollama'], ollama_model)
            specialist_result = tabular_agent.process_tabular_query(df, query, context)
            
            # Trust the specialist if confident
            if specialist_result.get('confidence', 0) > 0.6:
                return {
                    **base_result,
                    'answer': specialist_result['answer'],
                    'confidence': specialist_result['confidence'],
                    'method': 'tabular_specialist',
                    'analysis_results': {'tabular_analysis': specialist_result.get('analysis_data', {})}
                }
        except Exception as e:
            logger.warning(f"Tabular specialist failed: {e}")
    
    # 📊 VISUALIZATION SPECIALIST (Third Chair) - WITH FILTER SUPPORT
    if (context['intent'] == 'visualize' or 
        any(viz_word in query.lower() for viz_word in ['show', 'plot', 'chart', 'graph', 'visualize', 'display'])):
        
        # Check if this is a mixed intent query (visualization + statistical operation)
        has_statistical_operation = any(stat_word in query.lower() for stat_word in 
                                    ['sum', 'total', 'average', 'mean', 'max', 'maximum', 
                                    'min', 'minimum', 'count', 'median'])
        
        has_grouping = 'by ' in query.lower()
        
        try:
            # Route based on intent complexity
            if has_statistical_operation and has_grouping:
                # Mixed intent: Statistical visualization with grouping
                viz_result = _parse_visualization_query_with_unlimited_filters(query, df)
                
                if viz_result:
                    return {
                        **base_result,
                        'visualization': viz_result['chart'],
                        'viz_message': viz_result['message'],
                        'answer': f"📊 {viz_result['message']}",
                        'confidence': viz_result['confidence'],
                        'method': 'visualization_specialist_mixed_intent',
                        'intent_detected': f"visualize + {_detect_statistical_intent(query)}",
                        'filters_applied': viz_result.get('filters_applied', []),
                        'filtered_rows': viz_result.get('filtered_rows', len(df)),
                        'original_rows': len(df),
                        'total_filters': viz_result.get('total_filters', 0)
                    }
            
            elif context['intent'] == 'visualize' or not has_statistical_operation:
                # Pure visualization intent
                viz_filters_applied = []
                viz_working_df = df.copy()
                
                # Apply filter detection (your existing logic)
                filter_patterns = [
                    (r'(\w+)\s+(?:is\s+)?(?:less\s+than|<|below)\s+(\d+(?:\.\d+)?)', 'less_than'),
                    (r'(\w+)\s+(?:is\s+)?(?:greater\s+than|>|above)\s+(\d+(?:\.\d+)?)', 'greater_than'),
                    (r'(\w+)\s+(?:starting\s+with|begins?\s+with)\s+(?:letter\s+)?([a-zA-Z])', 'starts_with'),
                    (r'(\w+)\s+(?:contains?|includes?)\s+["\']?([^"\']+)["\']?', 'contains'),
                    (r'(\w+)\s+(?:equals?|is)\s+["\']([^"\']+)["\']', 'text_equals'),
                ]
                
                query_lower = query.lower()
                
                for pattern, operation in filter_patterns:
                    matches = re.finditer(pattern, query_lower)
                    for match in matches:
                        col_hint, value = match.groups()
                        
                        matching_col = None
                        for col in df.columns:
                            if (col_hint in col.lower() or col.lower() in col_hint or
                                col_hint.replace('_', '') in col.lower().replace('_', '') or
                                col.lower().replace('_', '') in col_hint.replace('_', '')):
                                matching_col = col
                                break
                        
                        if matching_col and matching_col in df.columns:
                            if operation == 'less_than' and pd.api.types.is_numeric_dtype(df[matching_col]):
                                value = float(value)
                                viz_working_df = viz_working_df[viz_working_df[matching_col] < value]
                                viz_filters_applied.append(f"{matching_col} < {value}")
                            elif operation == 'greater_than' and pd.api.types.is_numeric_dtype(df[matching_col]):
                                value = float(value)
                                viz_working_df = viz_working_df[viz_working_df[matching_col] > value]
                                viz_filters_applied.append(f"{matching_col} > {value}")
                            elif operation == 'starts_with':
                                viz_working_df = viz_working_df[viz_working_df[matching_col].astype(str).str.upper().str.startswith(value.upper())]
                                viz_filters_applied.append(f"{matching_col} starts with '{value.upper()}'")
                            elif operation == 'contains':
                                viz_working_df = viz_working_df[viz_working_df[matching_col].astype(str).str.contains(value, case=False, na=False)]
                                viz_filters_applied.append(f"{matching_col} contains '{value}'")
                            elif operation == 'text_equals':
                                viz_working_df = viz_working_df[viz_working_df[matching_col].astype(str).str.lower() == value.lower()]
                                viz_filters_applied.append(f"{matching_col} = '{value}'")
                
                # CREATE VISUALIZATION WITH FILTERED DATA
                viz_agent = VisualizationAgent(AI_MODELS['ollama'])
                fig, message = viz_agent.create_intelligent_visualization(viz_working_df, query, context)
                
                if fig:
                    enhanced_message = message
                    if viz_filters_applied:
                        enhanced_message += f" (filtered: {', '.join(viz_filters_applied)})"
                    
                    return {
                        **base_result,
                        'visualization': fig,
                        'viz_message': enhanced_message,
                        'answer': f"📊 {enhanced_message}",
                        'confidence': min(context['confidence'] + 0.1, 1.0),
                        'method': 'visualization_specialist_pure_intent',
                        'intent_detected': 'visualize',
                        'filters_applied': viz_filters_applied,
                        'filtered_rows': len(viz_working_df),
                        'original_rows': len(df)
                    }
            
        except Exception as e:
            logger.warning(f"Intent-aware visualization specialist failed: {e}")


    
    # 🔮 PREDICTION SPECIALIST (Fourth Chair)
    if context['intent'] == 'predict' or any(word in query.lower() for word in ['predict', 'forecast', 'model', 'estimate']):
        try:
            pred_agent = PredictiveModelingAgent(AI_MODELS['ollama'], ollama_model)
            
            # Smart target column detection
            target_column = None
            if context['entities']:
                target_column = context['entities'][0]
            else:
                # Fallback: find column mentioned in query
                for col in df.columns:
                    if col.lower() in query.lower():
                        target_column = col
                        break
            
            if target_column and target_column in df.columns:
                # Use context for smarter feature selection
                suggested_features = context.get('suggested_columns', None)
                model_result, message = pred_agent.create_intelligent_prediction_model(
                    df, target_column, suggested_features
                )
                
                if model_result and 'error' not in str(model_result):
                    result = {
                        **base_result,
                        'prediction_model': model_result,
                        'answer': f"🔮 {message}",
                        'confidence': 0.9,
                        'method': 'prediction_specialist'
                    }
                    
                    if 'ai_insights' in model_result:
                        result['ai_insights'] = model_result['ai_insights']
                    
                    # Track user preferences
                    if 'user_preferences' in st.session_state:
                        st.session_state.user_preferences['common_columns'].append(target_column)
                        if len(st.session_state.user_preferences['common_columns']) > 10:
                            st.session_state.user_preferences['common_columns'] = st.session_state.user_preferences['common_columns'][-10:]
                    
                    return result
                else:
                    return {
                        **base_result,
                        'answer': f"❌ Prediction failed: {message}",
                        'confidence': 0.3,
                        'method': 'prediction_failed'
                    }
            else:
                return {
                    **base_result,
                    'answer': "❌ Could not identify target column for prediction. Please specify which column to predict.",
                    'confidence': 0.3,
                    'method': 'prediction_no_target'
                }
        except Exception as e:
            logger.error(f"Prediction specialist failed: {e}")
            return {
                **base_result,
                'answer': f"❌ Prediction error: {str(e)}",
                'confidence': 0.3,
                'method': 'prediction_error'
            }
    
    # === STEP 3: CONDUCTOR COORDINATES COMPLEX QUERIES ===
    
    # 🔍 MULTI-INTENT ANALYSIS (Conductor coordinates multiple specialists)
    analysis_performed = False
    
    # Correlation Analysis
    if context['intent'] == 'correlate' and len(context['entities']) >= 2:
        col1, col2 = context['entities'][:2]
        if col1 in df.columns and col2 in df.columns:
            try:
                stats_result = perform_statistical_analysis(df, col1, col2)
                base_result['analysis_results']['correlation'] = stats_result
                
                if 'correlation' in stats_result:
                    corr_data = stats_result['correlation']
                    base_result['answer'] = f"📈 Correlation between {col1} and {col2}: {corr_data['pearson_coefficient']:.3f} ({corr_data['strength']})"
                    base_result['confidence'] = 0.8
                    analysis_performed = True
            except Exception as e:
                logger.error(f"Correlation analysis failed: {e}")
    
    # Outlier Detection
    elif context['intent'] == 'detect' and context['entities']:
        col = context['entities'][0]
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            try:
                outlier_result, message = detect_outliers(df, col)
                if outlier_result:
                    base_result['analysis_results']['outliers'] = outlier_result
                    base_result['answer'] = f"🎯 Found {outlier_result['outlier_count']} outliers in {col} ({outlier_result['outlier_percentage']:.1f}%)"
                    base_result['confidence'] = 0.8
                    analysis_performed = True
            except Exception as e:
                logger.error(f"Outlier detection failed: {e}")
    
    # Clustering Analysis
    elif context['intent'] == 'cluster' and len(df.select_dtypes(include=[np.number]).columns) >= 2:
        try:
            features = context['entities'][:4] if context['entities'] else None
            cluster_result, message = perform_clustering(df, n_clusters=3, features=features)
            if cluster_result:
                base_result['analysis_results']['clustering'] = cluster_result
                base_result['answer'] = f"🎯 Clustering completed: {message}"
                base_result['confidence'] = 0.7
                analysis_performed = True
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
    
    # === STEP 4: FALLBACK TO TABULAR AGENT ===
    if not analysis_performed:
        try:
            tabular_agent = AgenticTabularProcessor(AI_MODELS['ollama'], ollama_model)
            fallback_result = tabular_agent.process_tabular_query(df, query, context)
            
            base_result['answer'] = fallback_result['answer']
            base_result['confidence'] = fallback_result['confidence']
            base_result['method'] = 'tabular_fallback'
            
            if 'analysis_data' in fallback_result:
                base_result['analysis_results']['fallback_analysis'] = fallback_result['analysis_data']
            
            # Add helpful hints for low confidence
            if fallback_result['confidence'] < 0.4:
                base_result['note'] = "💡 Try being more specific or rephrasing your question."
            elif fallback_result['confidence'] < 0.6:
                base_result['note'] = "💡 Results might be improved with more specific column names."
                
        except Exception as e:
            logger.error(f"All processing methods failed: {e}")
            base_result['answer'] = f"❌ Unable to process query: {str(e)}"
            base_result['confidence'] = 0.2
            base_result['method'] = 'complete_failure'
    
    return base_result

def _detect_statistical_intent(query):
    """Helper to detect statistical sub-intent"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['sum', 'total']):
        return 'aggregation_sum'
    elif any(word in query_lower for word in ['average', 'mean', 'avg']):
        return 'aggregation_mean'
    elif any(word in query_lower for word in ['count', 'number of']):
        return 'counting'
    elif any(word in query_lower for word in ['max', 'maximum']):
        return 'extremes_max'
    elif any(word in query_lower for word in ['min', 'minimum']):
        return 'extremes_min'
    else:
        return 'aggregation'
# ============================================================================
# 10. 📊 DATA QUALITY AND EXPLORATION
# ============================================================================
@enhanced_error_handling
def assess_data_quality(df):
    """Comprehensive data quality assessment - Enhanced for database data and safer"""
    
    try:
        if df is None or df.empty:
            return {
                'basic_stats': {
                    'total_rows': 0,
                    'total_columns': 0,
                    'duplicate_rows': 0,
                    'total_missing_values': 0
                },
                'missing_values': {},
                'missing_percentage': {},
                'data_types': {},
                'data_source': 'No data'
            }
        
        missing_data = df.isnull().sum()
        total_missing = missing_data.sum()
        
        # Handle potential memory issues with large datasets
        duplicate_count = 0
        try:
            if len(df) <= 50000:  # Only check duplicates for reasonable sized datasets
                duplicate_count = df.duplicated().sum()
            else:
                # For large datasets, sample for duplicate check
                sample_size = min(10000, len(df))
                sample_df = df.sample(n=sample_size, random_state=42)
                sample_duplicates = sample_df.duplicated().sum()
                duplicate_count = int(sample_duplicates * (len(df) / sample_size))  # Estimate
        except Exception as e:
            logger.warning(f"Duplicate detection failed: {e}")
            duplicate_count = 0
        
        return {
            'basic_stats': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'duplicate_rows': duplicate_count,
                'total_missing_values': int(total_missing)
            },
            'missing_values': missing_data[missing_data > 0].to_dict(),
            'missing_percentage': (missing_data / len(df) * 100).round(2).to_dict(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'data_source': st.session_state.get('data_source', 'Unknown')
        }
        
    except Exception as e:
        logger.error(f"Data quality assessment failed: {e}")
        return {
            'basic_stats': {
                'total_rows': len(df) if df is not None else 0,
                'total_columns': len(df.columns) if df is not None else 0,
                'duplicate_rows': 0,
                'total_missing_values': 0
            },
            'missing_values': {},
            'missing_percentage': {},
            'data_types': {},
            'data_source': 'Error in assessment'
        }

# ============================================================================
# 11. 🎨 USER INTERFACE COMPONENTS
# ============================================================================

def display_data_quality_report(quality_report):
    """Display data quality assessment"""
    
    st.subheader("📋 Data Quality Assessment")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", quality_report['basic_stats']['total_rows'])
    with col2:
        st.metric("Total Columns", quality_report['basic_stats']['total_columns'])
    with col3:
        st.metric("Duplicate Rows", quality_report['basic_stats']['duplicate_rows'])
    with col4:
        st.metric("Missing Values", quality_report['basic_stats']['total_missing_values'])
    
    if quality_report['missing_values']:
        st.markdown("#### Missing Values")
        missing_df = pd.DataFrame([
            {'Column': col, 'Missing Count': count, 'Missing %': quality_report['missing_percentage'][col]}
            for col, count in quality_report['missing_values'].items()
        ])
        
        fig = px.bar(missing_df, x='Column', y='Missing %', 
                    title="Missing Values by Column")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def display_enhanced_chart(fig, message):
    """Display chart with enhanced presentation"""
    
    if fig:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #00c851, #007e33); color: white; 
                    padding: 10px; border-radius: 8px; margin: 10px 0; font-weight: 500;">
            ✅ {message}
        </div>
        """, unsafe_allow_html=True)
        
        st.plotly_chart(fig, use_container_width=True, height=600)
    else:
        st.warning(f"⚠️ {message}")

def display_performance_metrics():
    """Display performance monitoring dashboard"""
    
    if st.session_state.performance_metrics:
        st.subheader("⚡ Performance Metrics")
        
        metrics_df = pd.DataFrame(st.session_state.performance_metrics)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_duration = metrics_df['duration'].mean()
            st.metric("Avg Operation Time", f"{avg_duration:.2f}s")
        with col2:
            total_operations = len(metrics_df)
            st.metric("Total Operations", total_operations)
        with col3:
            error_count = st.session_state.get('error_count', 0)
            st.metric("Errors", error_count)
        
        if len(metrics_df) > 1:
            fig = px.line(metrics_df, x='timestamp', y='duration', 
                         color='operation', title="Performance Over Time")
            st.plotly_chart(fig, use_container_width=True)

def display_enhanced_predictive_modeling_interface(df):
    """Enhanced predictive modeling interface with model selector"""
    
    st.subheader("🔮 Advanced Predictive Modeling")
    
    # Model engine selector
    col1, col2 = st.columns([1, 2])
    
    with col1:
        model_engine = st.selectbox(
            "Choose modeling engine:",
            ["Simplified (Recommended)", "Advanced (AI-Powered)"],
            help="Simplified is more reliable, Advanced has AI insights"
        )
    
    with col2:
        if model_engine == "Simplified (Recommended)":
            st.info("🛡️ More reliable, faster processing, based on your reference code")
        else:
            st.info("🤖 AI-powered insights, requires Ollama connection")
    
    # Model configuration
    col1, col2 = st.columns(2)
    
    with col1:
        # Target selection
        if model_engine == "Simplified (Recommended)":
            # For simplified, show all columns
            all_cols = df.columns.tolist()
            target_column = st.selectbox(
                "Select target variable to predict:",
                all_cols,
                help="Choose the column you want to predict"
            )
        else:
            # For advanced, only numeric for now
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            all_cols = numeric_cols + categorical_cols
            
            target_column = st.selectbox(
                "Select target variable to predict:",
                all_cols,
                help="Choose the column you want to predict"
            )
        
        # Model type selection (only for advanced)
        if model_engine == "Advanced (AI-Powered)":
            model_type = st.selectbox(
                "Model type:",
                ["auto", "regression", "classification"],
                help="Auto will determine the best type based on your target variable"
            )
        else:
            model_type = "auto"  # Simplified always uses auto-detection
    
    with col2:
        # Feature selection
        available_features = [col for col in df.columns if col != target_column]
        
        feature_selection_mode = st.radio(
            "Feature selection:",
            ["Auto (AI-recommended)", "Manual selection"]
        )
        
        if feature_selection_mode == "Manual selection":
            selected_features = st.multiselect(
                "Select features:",
                available_features,
                default=available_features[:min(10, len(available_features))],
                help="Choose which columns to use for prediction"
            )
        else:
            selected_features = None
    
    # Advanced options (only for advanced engine)
    if model_engine == "Advanced (AI-Powered)":
        with st.expander("🔧 Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                show_feature_importance = st.checkbox(
                    "Show feature importance analysis",
                    value=True
                )
            
            with col2:
                show_predictions_plot = st.checkbox(
                    "Show predictions vs actual plot",
                    value=True
                )
    
    # Train model button
    if st.button("🚀 Train Predictive Model", type="primary"):
        if target_column:
            with st.spinner("🔄 Training predictive model..."):
                try:
                    if model_engine == "Simplified (Recommended)":
                        # Use SimplifiedPredictiveModelingAgent
                        modeling_agent = SimplifiedPredictiveModelingAgent()
                        model_result, message = modeling_agent.create_predictive_model(
                            df, target_column, selected_features
                        )
                        
                        if model_result:
                            st.success(f"✅ {message}")
                            display_simplified_model_results(model_result)
                        else:
                            st.error(f"❌ {message}")
                    
                    else:
                        # Use existing PredictiveModelingAgent
                        pred_agent = PredictiveModelingAgent(
                            AI_MODELS.get('ollama'),
                            AI_MODELS.get('ollama_model', 'llama3.2')
                        )
                        
                        model_result, message = pred_agent.create_intelligent_prediction_model(
                            df, target_column, selected_features, model_type
                        )
                        
                        if model_result and 'error' not in str(model_result):
                            st.success(f"✅ {message}")
                            
                            # Use your existing comprehensive display function
                            display_model_results(model_result, 
                                                show_feature_importance, 
                                                show_predictions_plot, 
                                                True)
                        else:
                            st.error(f"❌ {message}")
                            
                except Exception as e:
                    st.error(f"❌ Model training failed: {str(e)}")
                    logger.error(f"Model training error: {e}")
        else:
            st.warning("Please select a target column to predict")

def display_model_results(model_result, show_feature_importance=True, show_predictions_plot=True, show_residuals=True):
    """Display comprehensive model results"""
    
    metrics = model_result['metrics']
    model_summary = model_result['model_summary']
    
    # Model Overview
    st.markdown("### 📊 Model Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Model Type", metrics['model_type'].title())
        st.metric("Features Used", model_summary['total_features'])
    
    with col2:
        st.metric("Training Samples", metrics['train_size'])
        st.metric("Test Samples", metrics['test_size'])
    
    with col3:
        if metrics['model_type'] == 'regression':
            st.metric("R² Score", f"{metrics['test_r2']:.3f}")
            st.metric("RMSE", f"{metrics['test_rmse']:.3f}")
        else:
            st.metric("Accuracy", f"{metrics['test_accuracy']:.3f}")
            st.metric("F1 Score", f"{metrics.get('f1_score', 0):.3f}")
    
    with col4:
        overfitting_status = "⚠️ Yes" if metrics.get('overfitting', False) else "✅ No"
        st.metric("Overfitting", overfitting_status)
        
        if metrics['model_type'] == 'regression':
            st.metric("MAE", f"{metrics.get('test_mae', 0):.3f}")
        else:
            st.metric("Precision", f"{metrics.get('precision', 0):.3f}")
    
    # Performance Analysis
    st.markdown("### 📈 Performance Analysis")
    
    if metrics['model_type'] == 'regression':
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Regression Metrics:**")
            st.write(f"• **R² Score (Test):** {metrics['test_r2']:.3f}")
            st.write(f"• **RMSE (Test):** {metrics['test_rmse']:.3f}")
            st.write(f"• **MAE (Test):** {metrics.get('test_mae', 0):.3f}")
            st.write(f"• **Mean Residual:** {metrics.get('mean_residual', 0):.3f}")
        
        with col2:
            st.markdown("**Model Interpretation:**")
            r2_score = metrics['test_r2']
            if r2_score > 0.8:
                st.success("🌟 Excellent model performance")
            elif r2_score > 0.6:
                st.info("👍 Good model performance")
            elif r2_score > 0.4:
                st.warning("⚠️ Moderate model performance")
            else:
                st.error("❌ Poor model performance")
            
            if metrics.get('overfitting', False):
                st.warning("⚠️ Model shows signs of overfitting")
            else:
                st.success("✅ Good generalization")
    
    else:  # Classification
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Classification Metrics:**")
            st.write(f"• **Accuracy:** {metrics['test_accuracy']:.3f}")
            st.write(f"• **Precision:** {metrics.get('precision', 0):.3f}")
            st.write(f"• **Recall:** {metrics.get('recall', 0):.3f}")
            st.write(f"• **F1 Score:** {metrics.get('f1_score', 0):.3f}")
        
        with col2:
            st.markdown("**Model Interpretation:**")
            accuracy = metrics['test_accuracy']
            if accuracy > 0.9:
                st.success("🌟 Excellent model performance")
            elif accuracy > 0.8:
                st.info("👍 Good model performance")
            elif accuracy > 0.7:
                st.warning("⚠️ Moderate model performance")
            else:
                st.error("❌ Poor model performance")
    
    # Feature Importance
    if show_feature_importance and 'feature_importance' in model_result:
        st.markdown("### 🎯 Feature Importance Analysis")
        
        importance_df = model_result['feature_importance'].head(15)
        
        fig_importance = px.bar(
            importance_df,
            x='importance',
            y='feature',
            orientation='h',
            title="Top 15 Most Important Features",
            color='importance',
            color_continuous_scale='viridis'
        )
        
        fig_importance.update_layout(
            height=600,
            margin=dict(l=150, r=50, t=80, b=50),
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig_importance, use_container_width=True)
        
        # Feature importance table
        st.markdown("#### Feature Details")
        importance_display = importance_df.copy()
        importance_display['importance'] = importance_display['importance'].round(4)
        st.dataframe(importance_display, use_container_width=True)
    
    # Predictions Analysis
    if show_predictions_plot and 'predictions' in model_result:
        st.markdown("### 🎯 Predictions Analysis")
        
        predictions_df = model_result['predictions']
        
        if metrics['model_type'] == 'regression':
            # Predictions vs Actual
            fig_pred = px.scatter(
                predictions_df,
                x='actual',
                y='predicted',
                title="Predictions vs Actual Values",
                trendline="ols",
                trendline_color_override="red"
            )
            
            # Add perfect prediction line
            min_val = min(predictions_df['actual'].min(), predictions_df['predicted'].min())
            max_val = max(predictions_df['actual'].max(), predictions_df['predicted'].max())
            
            fig_pred.add_trace(go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='Perfect Prediction',
                line=dict(dash='dash', color='green', width=2)
            ))
            
            fig_pred.update_layout(height=500)
            st.plotly_chart(fig_pred, use_container_width=True)
            
            # Residuals Analysis
            if show_residuals:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_residuals = px.scatter(
                        predictions_df,
                        x='predicted',
                        y='residuals',
                        title="Residuals vs Predicted Values"
                    )
                    fig_residuals.add_hline(y=0, line_dash="dash", line_color="red")
                    st.plotly_chart(fig_residuals, use_container_width=True)
                
                with col2:
                    fig_residuals_hist = px.histogram(
                        predictions_df,
                        x='residuals',
                        title="Residuals Distribution",
                        nbins=30
                    )
                    st.plotly_chart(fig_residuals_hist, use_container_width=True)
        
        else:  # Classification
            # Confusion Matrix-like visualization
            correct_predictions = predictions_df[predictions_df['correct'] == True]
            incorrect_predictions = predictions_df[predictions_df['correct'] == False]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Correct Predictions", len(correct_predictions))
                st.metric("Incorrect Predictions", len(incorrect_predictions))
            
            with col2:
                accuracy_pct = len(correct_predictions) / len(predictions_df) * 100
                st.metric("Accuracy %", f"{accuracy_pct:.1f}%")
                
                if 'confidence' in predictions_df.columns:
                    avg_confidence = predictions_df['confidence'].mean()
                    st.metric("Avg Confidence", f"{avg_confidence:.3f}")
    
    # AI Insights
    if 'ai_insights' in model_result:
        st.markdown("### 🧠 AI-Generated Insights")
        st.info(model_result['ai_insights'])
    
    # Data Summary
    with st.expander("📋 Data Processing Summary"):
        preprocessing = model_summary['data_preprocessing']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Initial rows:** {preprocessing['initial_rows']:,}")
            st.write(f"**Final rows:** {preprocessing['final_rows']:,}")
            st.write(f"**Rows dropped:** {preprocessing['rows_dropped']:,}")
        
        with col2:
            st.write(f"**Features encoded:** {preprocessing['categorical_features_encoded']}")
            st.write(f"**Train/Test split:** {preprocessing['train_test_split']}")
            st.write(f"**Target column:** {model_summary['target_column']}")

def display_simplified_model_results(model_result):
    """Display simplified model results"""
    
    metrics = model_result['metrics']
    
    # Model Overview
    st.markdown("### 📊 Model Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Model Type", metrics['model_type'].title())
        st.metric("Training Samples", metrics['train_size'])
    
    with col2:
        st.metric("Test Samples", metrics['test_size'])
        overfitting = "⚠️ Yes" if metrics.get('overfitting', False) else "✅ No"
        st.metric("Overfitting", overfitting)
    
    with col3:
        if metrics['model_type'] == 'regression':
            st.metric("R² Score", f"{metrics['test_r2']:.3f}")
            st.metric("RMSE", f"{metrics['test_rmse']:.3f}")
        else:
            st.metric("Accuracy", f"{metrics['test_accuracy']:.3f}")
            st.metric("F1 Score", f"{metrics.get('f1_score', 0):.3f}")
    
    with col4:
        if metrics['model_type'] == 'regression':
            st.metric("MAE", f"{metrics.get('test_mae', 0):.3f}")
        else:
            st.metric("Precision", f"{metrics.get('precision', 0):.3f}")
            st.metric("Recall", f"{metrics.get('recall', 0):.3f}")
    
    # Performance interpretation
    st.markdown("### 📈 Performance Interpretation")
    
    if metrics['model_type'] == 'regression':
        r2_score = metrics['test_r2']
        if r2_score > 0.8:
            st.success("🌟 Excellent model performance (R² > 0.8)")
        elif r2_score > 0.6:
            st.info("👍 Good model performance (R² > 0.6)")
        elif r2_score > 0.4:
            st.warning("⚠️ Moderate model performance (R² > 0.4)")
        else:
            st.error("❌ Poor model performance (R² ≤ 0.4)")
    else:
        accuracy = metrics['test_accuracy']
        if accuracy > 0.9:
            st.success("🌟 Excellent model performance (Accuracy > 90%)")
        elif accuracy > 0.8:
            st.info("👍 Good model performance (Accuracy > 80%)")
        elif accuracy > 0.7:
            st.warning("⚠️ Moderate model performance (Accuracy > 70%)")
        else:
            st.error("❌ Poor model performance (Accuracy ≤ 70%)")
    
    # Feature Importance
    if 'feature_importance' in model_result:
        st.markdown("### 🎯 Feature Importance")
        
        importance_df = model_result['feature_importance'].head(10)
        
        fig_importance = px.bar(
            importance_df,
            x='importance',
            y='feature',
            orientation='h',
            title="Top 10 Most Important Features",
            color='importance',
            color_continuous_scale='viridis'
        )
        
        fig_importance.update_layout(
            height=400,
            margin=dict(l=150, r=50, t=80, b=50),
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig_importance, use_container_width=True)
        
        # Feature importance table
        st.dataframe(importance_df, use_container_width=True)
    
    # Predictions Analysis
    if 'predictions' in model_result:
        st.markdown("### 🎯 Predictions vs Actual")
        
        predictions_df = model_result['predictions']
        
        if metrics['model_type'] == 'regression':
            # Predictions vs Actual scatter plot
            fig_pred = px.scatter(
                predictions_df,
                x='actual',
                y='predicted',
                title="Predictions vs Actual Values",
                trendline="ols"
            )
            
            # Add perfect prediction line
            min_val = min(predictions_df['actual'].min(), predictions_df['predicted'].min())
            max_val = max(predictions_df['actual'].max(), predictions_df['predicted'].max())
            
            fig_pred.add_trace({
                'type': 'scatter',
                'mode': 'lines',
                'x': [min_val, max_val],
                'y': [min_val, max_val],
                'name': 'Perfect Prediction',
                'line': {'dash': 'dash', 'color': 'red'}
            })
            
            st.plotly_chart(fig_pred, use_container_width=True)
            
            # Residuals plot
            col1, col2 = st.columns(2)
            
            with col1:
                fig_residuals = px.scatter(
                    predictions_df,
                    x='predicted',
                    y='residuals',
                    title="Residuals vs Predicted"
                )
                fig_residuals.add_hline(y=0, line_dash="dash", line_color="red")
                st.plotly_chart(fig_residuals, use_container_width=True)
            
            with col2:
                fig_residuals_hist = px.histogram(
                    predictions_df,
                    x='residuals',
                    title="Residuals Distribution",
                    nbins=20
                )
                st.plotly_chart(fig_residuals_hist, use_container_width=True)
        
        else:  # Classification
            # Accuracy metrics
            correct_predictions = predictions_df[predictions_df['correct'] == True]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Correct Predictions", len(correct_predictions))
                accuracy_pct = len(correct_predictions) / len(predictions_df) * 100
                st.metric("Accuracy %", f"{accuracy_pct:.1f}%")
            
            with col2:
                st.metric("Incorrect Predictions", len(predictions_df) - len(correct_predictions))
                st.metric("Total Predictions", len(predictions_df))
            
            # Confusion matrix visualization (if possible)
            try:
                actual_values = predictions_df['actual'].unique()
                predicted_values = predictions_df['predicted'].unique()
                
                if len(actual_values) <= 10 and len(predicted_values) <= 10:
                    
                    
                    cm = confusion_matrix(predictions_df['actual'], predictions_df['predicted'])
                    
                    fig, ax = plt.subplots(figsize=(8, 6))
                    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
                    ax.set_xlabel('Predicted')
                    ax.set_ylabel('Actual')
                    ax.set_title('Confusion Matrix')
                    
                    st.pyplot(fig)
            except:
                # If confusion matrix fails, show a simple comparison
                comparison_df = predictions_df.groupby(['actual', 'predicted']).size().reset_index(name='count')
                fig = px.bar(comparison_df, x='actual', y='count', color='predicted', 
                           title="Actual vs Predicted Distribution")
                st.plotly_chart(fig, use_container_width=True)
    
    # Model Summary
    with st.expander("📋 Model Details"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Features Used:**")
            for feature in model_result['features_used']:
                st.write(f"• {feature}")
        
        with col2:
            st.write("**Model Configuration:**")
            st.write(f"• Model Type: {metrics['model_type'].title()}")
            st.write(f"• Training Size: {metrics['train_size']} samples")
            st.write(f"• Test Size: {metrics['test_size']} samples")
            st.write(f"• Features: {len(model_result['features_used'])}")
# ============================================================================
# 12. 🏠 MAIN APPLICATION PAGES
# ============================================================================

def display_data_analysis_page(df, quality_report):
    """Enhanced main data analysis page with predictive modeling"""
    
    # Data quality report
    display_data_quality_report(quality_report)
    
    st.markdown("---")
    
    # Data preview
    st.subheader("👀 Data Preview")
    preview_rows = st.slider("Rows to preview:", 5, 50, 10)
    st.dataframe(df.head(preview_rows), use_container_width=True)
    
    st.markdown("---")
    
    # Analysis tabs
    tab1, tab2, tab3 = st.tabs(["🤖 AI Query Interface", "🔮 Predictive Modeling", "📊 Advanced Analytics"])
    
    with tab1:
        # AI Query Interface
        st.subheader("🤖 AI-Powered Analysis")
        
        # Initialize suggestion agent
        suggestion_agent = SmartSuggestionAgent(AI_MODELS.get('embed_model'))
        suggestions = suggestion_agent.generate_smart_suggestions(df)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_input(
                "Ask about your data:",
                placeholder="e.g., 'show sales by region' or 'predict customer churn'",
                help="Use natural language to explore your data or build predictive models"
            )
        
        with col2:
            st.markdown("**💡 Smart Suggestions:**")
            for i, suggestion in enumerate(suggestions[:3]):
                if st.button(suggestion, key=f"main_suggest_{i}"):
                    query = suggestion
                    st.session_state.selected_query = suggestion
        
        # Process query
        if query or st.session_state.get('selected_query'):
            if st.session_state.get('selected_query'):
                query = st.session_state.selected_query
                st.session_state.selected_query = None
            
            with st.spinner("🔄 Analyzing your request..."):
                # Add to history
                if query not in st.session_state.query_history:
                    st.session_state.query_history.insert(0, query)
                    if len(st.session_state.query_history) > 10:
                        st.session_state.query_history.pop()
                
                # Process query
                results = process_enhanced_query(df, query)
                
                # Display results
                if 'answer' in results:
                    st.markdown("### 🤖 AI Response")
                    confidence = results.get('confidence', 0.0)
                    if confidence > 0.7:
                        st.success(f"**Answer:** {results['answer']}")
                    elif confidence > 0.4:
                        st.info(f"**Answer:** {results['answer']}")
                    else:
                        st.warning(f"**Answer:** {results['answer']} (Low confidence)")
                    
                    if 'ai_reasoning' in results and results['ai_reasoning']:
                        with st.expander("🧠 AI Reasoning"):
                            st.write(results['ai_reasoning'])
                
                # Display visualizations
                if 'visualization' in results:
                    st.markdown("### 📊 Visualization")
                    display_enhanced_chart(results['visualization'], results.get('viz_message', ''))
                
                # Display prediction results
                if 'prediction_model' in results:
                    st.markdown("### 🔮 Predictive Model Results")
                    display_model_results(results['prediction_model'])
                
                # Display other analysis results
                if results.get('analysis_results'):
                    #st.markdown("### 📈 Analysis Results")
                    
                    for analysis_type, analysis_data in results['analysis_results'].items():
                        #st.markdown(f"#### {analysis_type.title()}")
                        
                        if analysis_type == 'correlation' and 'correlation' in analysis_data:
                            corr_data = analysis_data['correlation']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Correlation", f"{corr_data['pearson_coefficient']:.3f}")
                            with col2:
                                st.metric("P-value", f"{corr_data['p_value']:.6f}")
                            with col3:
                                st.metric("Strength", corr_data['strength'])
                            
                            if corr_data['is_significant']:
                                st.success("✅ Statistically significant correlation")
                            else:
                                st.warning("⚠️ Not statistically significant")
                        
                        elif analysis_type == 'outliers':
                            outlier_data = analysis_data
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Outliers Found", outlier_data['outlier_count'])
                            with col2:
                                st.metric("Percentage", f"{outlier_data['outlier_percentage']:.2f}%")
                            
                            if outlier_data['outlier_count'] > 0:
                                st.dataframe(outlier_data['outliers'].head(), use_container_width=True)
                        
                        elif analysis_type == 'clustering':
                            cluster_data = analysis_data
                            
                            # Display cluster statistics
                            stats_data = []
                            for cluster_name, stats in cluster_data['cluster_stats'].items():
                                stats_data.append({
                                    'Cluster': cluster_name.replace('_', ' ').title(),
                                    'Size': stats['size'],
                                    'Percentage': f"{stats['percentage']:.1f}%"
                                })
                            
                            st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
                            
                            if cluster_data.get('silhouette_score'):
                                st.metric("Silhouette Score", f"{cluster_data['silhouette_score']:.3f}")
    
    with tab2:
        # Predictive Modeling Interface
        display_enhanced_predictive_modeling_interface(df)
    
    with tab3:
        # Advanced Analytics

        st.subheader("📊 Advanced Analytics Suite")
        analysis_type = st.selectbox("Choose analysis type:", [
            "Statistical Analysis",
            "Correlation Analysis", 
            "Outlier Detection",
            "Clustering Analysis",
            "Data Distribution"
        ])
        
        if analysis_type == "Statistical Analysis":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                selected_col = st.selectbox("Select column:", numeric_cols)
                
                if st.button("Run Statistical Analysis"):
                    with st.spinner("Performing statistical analysis..."):
                        stats_result = perform_statistical_analysis(df, selected_col)
                        
                        if 'descriptive_stats' in stats_result:
                            stats = stats_result['descriptive_stats']
                            
                            st.markdown("### 📈 Descriptive Statistics")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Mean", f"{stats['mean']:.3f}")
                                st.metric("Std Dev", f"{stats['std']:.3f}")
                            with col2:
                                st.metric("Median", f"{stats['median']:.3f}")
                                st.metric("Min", f"{stats['min']:.3f}")
                            with col3:
                                st.metric("Max", f"{stats['max']:.3f}")
                                st.metric("Skewness", f"{stats['skewness']:.3f}")
                            with col4:
                                st.metric("Kurtosis", f"{stats['kurtosis']:.3f}")
                                st.metric("Count", f"{stats['count']}")
                            
                            # Create histogram
                            fig = px.histogram(df, x=selected_col, title=f"Distribution of {selected_col}")
                            st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No numeric columns found for statistical analysis")
        
        elif analysis_type == "Correlation Analysis":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    var1 = st.selectbox("Variable 1:", numeric_cols)
                with col2:
                    var2 = st.selectbox("Variable 2:", [col for col in numeric_cols if col != var1])
                
                if st.button("Analyze Correlation"):
                    with st.spinner("Analyzing correlation..."):
                        corr_result = perform_statistical_analysis(df, var1, var2)
                        
                        if 'correlation' in corr_result:
                            corr_data = corr_result['correlation']
                            
                            st.markdown("### 🔗 Correlation Analysis")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Correlation", f"{corr_data['pearson_coefficient']:.3f}")
                            with col2:
                                st.metric("P-value", f"{corr_data['p_value']:.6f}")
                            with col3:
                                st.metric("Strength", corr_data['strength'])
                            
                            if corr_data['is_significant']:
                                st.success("✅ Statistically significant correlation")
                            else:
                                st.warning("⚠️ Not statistically significant")
                            
                            # Scatter plot with trendline
                            fig = px.scatter(df, x=var1, y=var2, trendline="ols", 
                                        title=f"Correlation between {var1} and {var2}")
                            st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Need at least 2 numeric columns for correlation analysis")
        
        elif analysis_type == "Outlier Detection":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                col1, col2 = st.columns(2)
                with col1:
                    selected_col = st.selectbox("Select column:", numeric_cols)
                with col2:
                    method = st.selectbox("Detection method:", ["iqr", "zscore"])
                
                if st.button("Detect Outliers"):
                    with st.spinner("Detecting outliers..."):
                        outlier_result, message = detect_outliers(df, selected_col, method)
                        
                        if outlier_result:
                            st.success(message)
                            
                            st.markdown("### 🎯 Outlier Detection Results")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Outliers Found", outlier_result['outlier_count'])
                            with col2:
                                st.metric("Percentage", f"{outlier_result['outlier_percentage']:.2f}%")
                            with col3:
                                st.metric("Method Used", outlier_result['method_used'].upper())
                            
                            if outlier_result['outlier_count'] > 0:
                                st.markdown("#### Outlier Records")
                                st.dataframe(outlier_result['outliers'].head(20), use_container_width=True)
                                
                                # Box plot to visualize outliers
                                fig = px.box(df, y=selected_col, title=f"Box Plot of {selected_col} (Outliers Highlighted)")
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("No outliers detected in the selected column")
                        else:
                            st.error(message)
            else:
                st.warning("No numeric columns found for outlier detection")
        
        elif analysis_type == "Clustering Analysis":
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    n_clusters = st.slider("Number of clusters:", min_value=2, max_value=10, value=3)
                with col2:
                    selected_features = st.multiselect(
                        "Select features for clustering:",
                        numeric_cols,
                        default=numeric_cols[:min(4, len(numeric_cols))]
                    )
                
                if st.button("Perform Clustering"):
                    if len(selected_features) >= 2:
                        with st.spinner("Performing clustering analysis..."):
                            cluster_result, message = perform_clustering(df, n_clusters, selected_features)
                            
                            if cluster_result:
                                st.success(message)
                                
                                st.markdown("### 🎯 Clustering Results")
                                
                                # Cluster statistics
                                stats_data = []
                                for cluster_name, stats in cluster_result['cluster_stats'].items():
                                    stats_data.append({
                                        'Cluster': cluster_name.replace('_', ' ').title(),
                                        'Size': stats['size'],
                                        'Percentage': f"{stats['percentage']:.1f}%"
                                    })
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
                                
                                with col2:
                                    if cluster_result['silhouette_score']:
                                        st.metric("Silhouette Score", f"{cluster_result['silhouette_score']:.3f}")
                                        if cluster_result['silhouette_score'] > 0.5:
                                            st.success("✅ Good clustering quality")
                                        elif cluster_result['silhouette_score'] > 0.3:
                                            st.warning("⚠️ Moderate clustering quality")
                                        else:
                                            st.error("❌ Poor clustering quality")
                                
                                # Visualize clusters (2D projection)
                                if len(selected_features) >= 2:
                                    clustered_data = cluster_result['clustered_data']
                                    fig = px.scatter(
                                        clustered_data, 
                                        x=selected_features[0], 
                                        y=selected_features[1],
                                        color='Cluster',
                                        title=f"Clusters visualization ({selected_features[0]} vs {selected_features[1]})"
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.error(message)
                    else:
                        st.warning("Please select at least 2 features for clustering")
            else:
                st.warning("Need at least 2 numeric columns for clustering analysis")
        
        elif analysis_type == "Data Distribution":
            all_cols = df.columns.tolist()
            selected_col = st.selectbox("Select column for distribution analysis:", all_cols)
            
            if st.button("Analyze Distribution"):
                with st.spinner("Analyzing data distribution..."):
                    dist_result, message = perform_data_distribution_analysis(df, selected_col)
                    
                    if dist_result:
                        st.success(message)
                        
                        st.markdown("### 📊 Distribution Analysis")
                        
                        if dist_result['type'] == 'numeric':
                            stats = dist_result['statistics']
                            
                            # Display statistics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Mean", f"{stats['mean']:.3f}")
                                st.metric("Median", f"{stats['median']:.3f}")
                            with col2:
                                st.metric("Std Dev", f"{stats['std']:.3f}")
                                st.metric("Skewness", f"{stats['skewness']:.3f}")
                            with col3:
                                st.metric("Min", f"{stats['min']:.3f}")
                                st.metric("Max", f"{stats['max']:.3f}")
                            with col4:
                                st.metric("Q25", f"{stats['q25']:.3f}")
                                st.metric("Q75", f"{stats['q75']:.3f}")
                            
                            # Normality test
                            if stats.get('shapiro_test'):
                                st.markdown("#### 📈 Normality Test")
                                if stats['shapiro_test']['is_normal']:
                                    st.success("✅ Data appears to be normally distributed")
                                else:
                                    st.warning("⚠️ Data does not appear to be normally distributed")
                                st.write(f"Shapiro-Wilk p-value: {stats['shapiro_test']['p_value']:.6f}")
                            
                            # Create histogram and box plot
                            col1, col2 = st.columns(2)
                            with col1:
                                fig_hist = px.histogram(df, x=selected_col, title=f"Histogram of {selected_col}")
                                st.plotly_chart(fig_hist, use_container_width=True)
                            
                            with col2:
                                fig_box = px.box(df, y=selected_col, title=f"Box Plot of {selected_col}")
                                st.plotly_chart(fig_box, use_container_width=True)
                        
                        else:  # Categorical
                            stats = dist_result['statistics']
                            value_counts = dist_result['value_counts']
                            
                            # Display statistics
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Count", stats['count'])
                                st.metric("Unique Values", stats['unique_values'])
                            with col2:
                                st.metric("Most Frequent", stats['most_frequent'])
                                st.metric("Frequency", stats['most_frequent_count'])
                            
                            # Value counts chart
                            fig = px.bar(
                                x=list(value_counts.keys()), 
                                y=list(value_counts.values()),
                                title=f"Value Distribution of {selected_col}"
                            )
                            fig.update_layout(xaxis_title=selected_col, yaxis_title="Count")
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(message)

def display_data_explorer_page(df):
    """Interactive data explorer page"""

    st.subheader("🔍 Interactive Data Explorer")

    # Generate a truly unique key prefix using UUID
    uid = str(uuid.uuid4())

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_columns = st.multiselect(
            "Select columns:",
            df.columns.tolist(),
            default=df.columns.tolist()[:5],
            key=f"explorer_select_columns_{uid}"
        )

    with col2:
        # Filtering
        filter_column = st.selectbox(
            "Filter by:", 
            ["None"] + df.columns.tolist(), 
            key=f"explorer_filter_column_{uid}"
        )
        if filter_column != "None":
            if df[filter_column].dtype == 'object':
                filter_values = st.multiselect(
                    f"Select {filter_column} values:",
                    df[filter_column].unique(),
                    key=f"explorer_filter_values_{filter_column}_{uid}"
                )
            else:
                min_val, max_val = float(df[filter_column].min()), float(df[filter_column].max())
                filter_range = st.slider(
                    f"{filter_column} range:",
                    min_val,
                    max_val,
                    (min_val, max_val),
                    key=f"explorer_filter_slider_{filter_column}_{uid}"
                )

    with col3:
        sort_column = st.selectbox(
            "Sort by:", 
            ["None"] + df.columns.tolist(), 
            key=f"explorer_sort_column_{uid}"
        )
        if sort_column != "None":
            sort_order = st.radio(
                "Order:", 
                ["Ascending", "Descending"], 
                key=f"explorer_sort_order_{uid}"
            )

        max_rows = st.number_input(
            "Max rows:", 
            min_value=10, 
            max_value=1000, 
            value=100,
            key=f"explorer_max_rows_{uid}"
        )

    # Apply filters
    filtered_df = df[selected_columns] if selected_columns else df

    if filter_column != "None":
        if df[filter_column].dtype == 'object' and 'filter_values' in locals():
            filtered_df = filtered_df[df[filter_column].isin(filter_values)]
        elif df[filter_column].dtype != 'object' and 'filter_range' in locals():
            filtered_df = filtered_df[
                (df[filter_column] >= filter_range[0]) & 
                (df[filter_column] <= filter_range[1])
            ]

    if sort_column != "None":
        ascending = sort_order == "Ascending"
        filtered_df = filtered_df.sort_values(sort_column, ascending=ascending)

    # Display results
    filtered_df = filtered_df.head(max_rows)

    st.markdown(f"#### 📊 Showing {len(filtered_df)} rows")
    st.dataframe(filtered_df, height=400, use_container_width=True)

    # Quick statistics
    numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        st.markdown("#### 📈 Quick Statistics")
        st.dataframe(filtered_df[numeric_cols].describe(), use_container_width=True)

def display_welcome_page():
    """Welcome page with instructions"""
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; margin: 2rem 0; color: white;">
        <h1>🤖 AI Data Analyst NooB v3.0</h1>
        <h3>Production-Ready Analytics with AI Agents</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 **Enhanced Features**
        
        **🤖 AI-Powered Analysis**
        - Intelligent query understanding
        - Dynamic visualization recommendations
        - Context-aware responses
        
        **📊 Advanced Analytics**
        - Statistical analysis & correlations
        - Outlier detection & clustering
        - Predictive modeling capabilities
        
        **📄 Multi-Format Support**
        - CSV, Excel, PDF processing
        - Database connectivity
        - Smart data type detection
        """)
    
    with col2:
        st.markdown("""
        ### 💡 **Getting Started**
        
        **1. Upload Your Data**
        - Drag & drop CSV/Excel files
        - Connect to MySQL databases
        - Process PDF documents
        
        **2. Ask Natural Questions**
        - "Show sales trends by region"
        - "Find outliers in customer data"
        - "What's the correlation between price and sales?"
        
        **3. Explore Insights**
        - Interactive visualizations
        - AI-generated recommendations
        - Export analysis results
        """)
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0; padding: 1rem; 
                background: #343a40; border-radius: 10px; border-left: 4px solid #007bff;">
        <h4>🎯 Ready to Discover Insights?</h4>
        <p>Upload your data file above to begin AI-powered analysis!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # System status
    st.markdown("### 🔧 System Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if AI_MODELS['embed_available']:
            st.success("✅ Embeddings Ready")
        else:
            st.error("❌ Embeddings Unavailable")
    
    with col2:
        if AI_MODELS['tapas_available']:
            st.success("✅ TAPAS Ready")
        else:
            st.error("❌ TAPAS Unavailable")
    
    with col3:
        if AI_MODELS['ollama_available']:
            st.success("✅ Ollama Connected")
        else:
            st.warning("⚠️ Ollama Disconnected")

def display_pdf_explorer(pdf_content):
    """Display PDF document explorer"""
    
    tab1, tab2, tab3 = st.tabs(["📝 Text Content", "📊 Tables", "🖼️ Images"])
    
    with tab1:
        st.markdown("#### Document Text Chunks")
        chunks = pdf_content.get('chunks', [])
        
        if chunks:
            # Show chunks with pagination
            chunks_per_page = 5
            total_pages = (len(chunks) + chunks_per_page - 1) // chunks_per_page
            
            if total_pages > 1:
                page_num = st.selectbox(
                    f"Page (showing {chunks_per_page} chunks per page):",
                    range(1, total_pages + 1),
                    key="chunks_pagination"
                )
                start_idx = (page_num - 1) * chunks_per_page
                end_idx = start_idx + chunks_per_page
                display_chunks = chunks[start_idx:end_idx]
            else:
                display_chunks = chunks
            
            for i, chunk in enumerate(display_chunks):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Chunk {chunk['id'] + 1}**")
                    with col2:
                        st.caption(f"Page {chunk.get('page', 'N/A')} • {chunk['word_count']} words")
                    
                    st.text_area(
                        "Content",
                        chunk['content'],
                        height=120,
                        key=f"chunk_display_{chunk['id']}_{i}",
                        disabled=True
                    )
                    st.markdown("---")
        else:
            st.info("No text chunks found")
    
    with tab2:
        st.markdown("#### Extracted Tables")
        tables = pdf_content.get('tables', [])
        
        if tables:
            for i, table in enumerate(tables):
                st.markdown(f"**Table {i+1} (Page {table['page']})**")
                st.caption(f"Shape: {table['shape'][0]} rows × {table['shape'][1]} columns")
                
                # Display table
                df_table = table['dataframe']
                st.dataframe(df_table, use_container_width=True)
                
                # Download option
                csv = df_table.to_csv(index=False)
                st.download_button(
                    f"📥 Download Table {i+1} as CSV",
                    csv,
                    f"table_{i+1}_page_{table['page']}.csv",
                    "text/csv",
                    key=f"download_table_{i}"
                )
                st.markdown("---")
        else:
            st.info("No tables found in the document")
    
    with tab3:
        st.markdown("#### Images and OCR Results")
        images = pdf_content.get('images', [])
        
        if images:
            for i, img in enumerate(images):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"**Image {i+1}**")
                    st.write(f"📍 Page: {img['page']}")
                    st.write(f"📏 Size: {img['size'][0]}×{img['size'][1]}px")
                    
                    if img['has_text']:
                        st.success("✅ Text detected")
                    else:
                        st.info("ℹ️ No text detected")
                
                with col2:
                    if img['has_text'] and img['ocr_text']:
                        st.markdown("**OCR Text:**")
                        st.text_area(
                            "Extracted text",
                            img['ocr_text'],
                            height=100,
                            key=f"ocr_text_{i}",
                            disabled=True
                        )
                    else:
                        st.caption("This image appears to be graphical content")
                
                st.markdown("---")
        else:
            st.info("No images found in the document")
# ============================================================================
# 13. 🔧 MAIN APPLICATION
# ============================================================================
def main():
    initialize_session_state()

    # --- Custom CSS Header ---
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">🤖 AI Data Analyst NooB v3.0</h1>
        <p style="color: white; margin: 0;">Production-Ready Analytics with AI Agents</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Sidebar Navigation ---
    with st.sidebar:
        page = st.selectbox("Choose a page:", ["📊 Data Analysis", "🔍 Data Explorer", "⚡ Performance Monitor"])
        st.markdown("---")

        # Model status
        if AI_MODELS['embed_available']:
            st.success("✅ Embeddings: Ready")
        else:
            st.error("❌ Embeddings: Not Available")

        if AI_MODELS['tapas_available']:
            st.success("✅ TAPAS: Ready")
        else:
            st.error("❌ TAPAS: Not Available")

        if AI_MODELS['ollama_available']:
            st.success(f"✅ Ollama: {AI_MODELS.get('ollama_model', 'Connected')}")
        else:
            st.warning("⚠️ Ollama: Disconnected")

        st.markdown("---")

        # Show data info
        if st.session_state.current_df is not None:
            st.subheader("📋 Data Info")
            df = st.session_state.current_df
            st.metric("Rows", f"{len(df):,}")
            st.metric("Columns", len(df.columns))

        elif st.session_state.current_pdf_content is not None:
            st.subheader("📄 PDF Info")
            metadata = st.session_state.current_pdf_content.get('metadata', {})
            st.metric("Text Chunks", metadata.get('total_chunks', 0))
            st.metric("Tables Found", metadata.get('total_tables', 0))
            st.metric("Images", metadata.get('total_images', 0))

    # --- Data Source Selection ---
    st.subheader("📤 Upload Your Data")
    data_source = st.radio("Data Source:", ["Upload File", "Connect to Database"] if DATABASE_AVAILABLE else ["Upload File"])

    # --- Upload File Block ---
    if data_source == "Upload File":
        file_types = ["csv", "xlsx", "xls"]
        if PDF_PROCESSING_AVAILABLE:
            file_types.append("pdf")

        uploaded_file = st.file_uploader("Choose your file", type=file_types)

        if uploaded_file:
            file_type = uploaded_file.name.split('.')[-1].lower()
            with st.spinner(f"🔄 Processing {file_type.upper()} file..."):
                if file_type == "pdf" and PDF_PROCESSING_AVAILABLE:
                    success = handle_pdf_file_upload(uploaded_file)
                    if success and isinstance(st.session_state.current_pdf_content, dict):
                        doc = st.session_state.current_pdf_content
                        st.session_state['document_json'] = doc.get('document_json')
                    else:
                        st.error("❌ Failed to process PDF.")
                else:
                    df = load_and_validate_data(uploaded_file)
                    if df is not None:
                        st.session_state.current_df = df
                        st.session_state.file_type = 'tabular'
                        st.session_state.current_pdf_content = None
                        st.success("✅ File uploaded successfully. Use the sidebar to navigate.")
                        #st.rerun()

    # --- Connect to Database Block ---
    elif data_source == "Connect to Database" and DATABASE_AVAILABLE:
        st.markdown("#### 🗃️ Database Connection")
        col1, col2 = st.columns(2)
        with col1:
            db_host = st.text_input("Host", value="localhost", key="db_host")
            db_user = st.text_input("Username", key="db_user")
            db_name = st.text_input("Database", key="db_name")
        with col2:
            db_port = st.text_input("Port", value="3306", key="db_port")
            db_password = st.text_input("Password", type="password", key="db_password")

        if st.button("Connect to Database", key="connect_db_btn"):
            try:
                conn_str = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                engine = create_engine(conn_str)
                with engine.connect() as conn:
                    tables = pd.read_sql("SHOW TABLES", conn)
                    st.session_state["available_tables"] = tables.iloc[:, 0].tolist()
                    st.session_state["db_engine"] = engine
                    st.success("✅ Connected successfully. Now select and load a table.")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")

        if "available_tables" in st.session_state:
            selected_table = st.selectbox("Select Table:", st.session_state["available_tables"], key="selected_table")
            if st.button("Load Table", key="load_table_btn"):
                try:
                    df = pd.read_sql(f"SELECT * FROM `{selected_table}`", st.session_state["db_engine"])
                    st.session_state.current_df = df
                    st.session_state.file_type = 'tabular'
                    st.success(f"✅ Loaded {len(df):,} rows from '{selected_table}'.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to load table: {e}")

    # --- Route Page Based on State ---
    if st.session_state.current_df is None and st.session_state.current_pdf_content is None:
        display_welcome_page()
    elif page == "📊 Data Analysis" and st.session_state.current_df is not None:
        quality_report = assess_data_quality(st.session_state.current_df)
        display_data_analysis_page(st.session_state.current_df, quality_report)
    elif page == "🔍 Data Explorer" and st.session_state.current_df is not None:
        display_data_explorer_page(st.session_state.current_df)
    elif page == "⚡ Performance Monitor":
        display_performance_metrics()
# ============================================================================
# 14. 🚀 APPLICATION ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application crashed: {traceback.format_exc()}")
        
        # Error recovery options
        st.markdown("### 🔧 Error Recovery")
        if st.button("Reset Application"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        if st.button("Clear Cache"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()




