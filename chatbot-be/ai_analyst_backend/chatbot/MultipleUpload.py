
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
Version: 3.0 (Demo Ready) __NAYAN GHOSH& AI TOOLS - CLAUDE/GPT
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
import hashlib
from pathlib import Path
from datetime import date
import threading
################## Add ons ######################## 26-08-2025 ##########################
from pdf2image import convert_from_bytes
import pytesseract



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

########################## Advanced Word Processor added on 18-08-2025 ##########################

try:
    import docx
    from docx import Document
    WORD_PROCESSING_AVAILABLE = True
    
    # Advanced Word processing with docx2txt (if available)
    try:
        import docx2txt
        DOCX2TXT_AVAILABLE = True
    except ImportError:
        DOCX2TXT_AVAILABLE = False
        
except ImportError:
    WORD_PROCESSING_AVAILABLE = False
    DOCX2TXT_AVAILABLE = False

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
    max_pdf_pages: int = 25
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

###################### Modified as on 20-08-2025 ######################################
def initialize_session_state():
    """Initialize Streamlit session state variables - Enhanced safety with Auth Manager"""
    
    # Define default values
    defaults = {
        'query_history': [],
        'favorite_queries': [],
        'performance_metrics': [],
        'analysis_results': {},
        'chat_history': [],
        'current_df': None,
        'current_pdf_content': None,
        'current_word_content': None,
        'file_type': None,
        'user_preferences': {'preferred_viz': [], 'common_columns': []},
        'connected': False,
        'selected_query': None,
        'error_count': 0,
        'pdf_question_history': [],
        'word_question_history': [],
        'db_connected': False,
        'db_tables': [],
        'data_source': 'None',
        'just_loaded_data': False,
        'page_selection': "📊 Data Analysis",
        # Authentication states
        'authenticated': False,
        'username': None,
        'show_login': True,
        # In initialize_session_state(), add this line to the defaults dictionary:
        'current_csv_content': None,
        'csv_chat_history': [],
        'csv_qa_setup_done': False
    }
    
    # Initialize only if not already present
    for key, default_value in defaults.items():
        if key not in st.session_state:
            try:
                st.session_state[key] = default_value
            except Exception as e:
                logger.warning(f"Failed to initialize session state key '{key}': {e}")
                # Continue with other keys even if one fails

    # Initialize Authentication Manager and related objects
    if 'auth_manager' not in st.session_state:
        try:
            st.session_state.auth_manager = AuthManager()
            logger.info("✅ AuthManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AuthManager: {e}")
            # Create a fallback auth manager
            st.session_state.auth_manager = None

    if 'conv_manager' not in st.session_state:
        try:
            if st.session_state.auth_manager is not None:
                st.session_state.conv_manager = ConversationManager(st.session_state.auth_manager)
                logger.info("✅ ConversationManager initialized successfully")
            else:
                st.session_state.conv_manager = None
        except Exception as e:
            logger.error(f"Failed to initialize ConversationManager: {e}")
            st.session_state.conv_manager = None

    if 'usage_tracker' not in st.session_state:
        try:
            st.session_state.usage_tracker = UsageTracker()
            logger.info("✅ UsageTracker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize UsageTracker: {e}")
            st.session_state.usage_tracker = None

######################################################################################################
# ============================================================================
# 3. 🤖 AI MODELS AND SERVICES INITIALIZATION
# ============================================================================

@st.cache_resource
def load_ai_models():
    # """Load and cache AI models with comprehensive error handling"""
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

def check_concurrent_user_support():
    """Verify that the app supports concurrent users properly"""
    
    session_id = id(st.session_state)
    current_time = datetime.now().isoformat()
    
    # Log session info for debugging
    logger.info(f"Session ID: {session_id}, Time: {current_time}")
    
    # Check if session state is properly isolated
    if 'session_check' not in st.session_state:
        st.session_state.session_check = {
            'session_id': session_id,
            'created_at': current_time,
            'username': st.session_state.get('username', 'anonymous')
        }
    
    return True
# ============================================================================
# 5. 🤖 AI AGENT CLASSES
# ===============================================================================
################## New AuthManager/ConvManager/UsageTracker Class for User Authentication and Management. Added on 20-08-2025 ##################
class AuthManager:
    def __init__(self, users_dir="users"):
        self.users_dir = Path(users_dir)
        self.users_dir.mkdir(exist_ok=True)
        self.users_file = self.users_dir / "users.json"
        self.ensure_users_file()
    
    def ensure_users_file(self):
        """Create users.json if it doesn't exist"""
        if not self.users_file.exists():
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_users(self, users):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def register_user(self, username, password, email=""):
        """Register a new user"""
        users = self.load_users()
        
        if username in users:
            return False, "Username already exists"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Create user data
        users[username] = {
            "password_hash": self.hash_password(password),
            "email": email,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        self.save_users(users)
        
        # Create user's personal folder
        user_folder = self.users_dir / username
        user_folder.mkdir(exist_ok=True)
        
        # Create user's conversation history file
        conv_file = user_folder / "conversations.json"
        with open(conv_file, 'w') as f:
            json.dump({"conversations": []}, f)
        
        return True, "User registered successfully"
    
    def login_user(self, username, password):
        """Authenticate user login"""
        users = self.load_users()
        
        if username not in users:
            return False, "Username not found"
        
        if users[username]["password_hash"] != self.hash_password(password):
            return False, "Invalid password"
        
        # Update last login
        users[username]["last_login"] = datetime.now().isoformat()
        self.save_users(users)
        
        return True, "Login successful"
    
    def get_user_folder(self, username):
        """Get user's folder path"""
        return self.users_dir / username

class ConversationManager:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
    
    def get_user_conversations_file(self, username):
        """Get path to user's conversations file"""
        user_folder = self.auth_manager.get_user_folder(username)
        return user_folder / "conversations.json"
    
    def load_user_conversations(self, username):
        """Load user's conversation history"""
        conv_file = self.get_user_conversations_file(username)
        try:
            with open(conv_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure conversations key exists
                if "conversations" not in data:
                    data["conversations"] = []
                return data
        except FileNotFoundError:
            # Create file if it doesn't exist
            logger.info(f"Creating new conversations file for user: {username}")
            return {"conversations": []}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {username}: {e}")
            # Backup corrupted file and start fresh
            try:
                import shutil
                backup_file = conv_file.with_suffix('.json.backup')
                shutil.copy2(conv_file, backup_file)
                logger.info(f"Backed up corrupted file to {backup_file}")
            except Exception as backup_error:
                logger.error(f"Failed to backup corrupted file: {backup_error}")
            return {"conversations": []}
        except Exception as e:
            logger.error(f"Error loading conversations for {username}: {e}")
            return {"conversations": []}
    
    def save_conversation(self, username, conversation_type, query, response, confidence=0.0, file_type=None, feedback=None):
        """Save a conversation to user's history - SIMPLIFIED AND MORE RELIABLE"""
        
        # Input validation first
        if not username or not username.strip():
            logger.error("❌ SAVE: Invalid username provided")
            return False
        
        if not query or not response:
            logger.error("❌ SAVE: Query or response is empty")
            return False
        
        try:
            # Clean and validate inputs
            username = str(username).strip()
            query = str(query).strip()[:1000]  # Limit query length
            response = str(response).strip()[:2000]  # Limit response length
            confidence = float(confidence) if confidence else 0.0
            file_type = str(file_type) if file_type else "unknown"
            #feedback = feedback
            
            logger.info(f"🔍 SAVE: Starting save for user: {username}")
            
            # Ensure user folder exists
            user_folder = self.auth_manager.get_user_folder(username)
            try:
                user_folder.mkdir(parents=True, exist_ok=True)
            except Exception as folder_error:
                logger.error(f"❌ SAVE: Cannot create user folder: {folder_error}")
                return False
            
            # Get conversation file path
            conv_file = self.get_user_conversations_file(username)
            
            # Load existing conversations - SIMPLIFIED
            try:
                conv_data = self.load_user_conversations(username)
                logger.info(f"🔍 SAVE: Loaded {len(conv_data.get('conversations', []))} existing conversations")
            except Exception as load_error:
                logger.warning(f"⚠️ SAVE: Load failed, creating new: {load_error}")
                conv_data = {"conversations": []}
            
            # Ensure conversations key exists
            if "conversations" not in conv_data:
                conv_data["conversations"] = []
            
            # Create new conversation entry - SIMPLIFIED
            try:
                conversation = {
                    "id": len(conv_data["conversations"]) + 1,
                    "timestamp": datetime.now().isoformat(),
                    "date": date.today().isoformat(),
                    "type": str(conversation_type),
                    "query": query,
                    "response": response,
                    "confidence": float(confidence),
                    "file_type": file_type,
                    "feedback": feedback,  # NEW: Store feedback (thumbs up/down)
                    "feedback_timestamp": None
                }
                
                # Quick validation - just try to serialize
                json.dumps(conversation, ensure_ascii=False)
                logger.info(f"🔍 SAVE: Conversation object validated")
                
            except Exception as conv_error:
                logger.error(f"❌ SAVE: Failed to create conversation object: {conv_error}")
                return False
            
            # Add to conversations list
            conv_data["conversations"].append(conversation)
            logger.info(f"🔍 SAVE: Added conversation. Total conversations: {len(conv_data['conversations'])}")
            
            # Keep only last 1000 conversations per user
            if len(conv_data["conversations"]) > 1000:
                conv_data["conversations"] = conv_data["conversations"][-1000:]
                logger.info(f"🔍 SAVE: Trimmed to last 1000 conversations")
            
            # SIMPLIFIED SAVE APPROACH - Direct write with backup
            success = self._save_conversations_safely(conv_file, conv_data)
            
            if success:
                logger.info(f"✅ SAVE: Successfully saved conversation for {username}")
                return True
            else:
                logger.error(f"❌ SAVE: Failed to save conversation for {username}")
                return False
                
        except Exception as e:
            logger.error(f"❌ SAVE: Critical failure saving conversation for {username}: {e}")
            return False
        
    def update_conversation_feedback(self, username, conversation_id, feedback):
        """Update feedback for a specific conversation - NEW METHOD"""
        
        try:
            conv_data = self.load_user_conversations(username)
            
            # Find the conversation by ID
            for conversation in conv_data["conversations"]:
                if conversation.get("id") == conversation_id:
                    conversation["feedback"] = feedback
                    conversation["feedback_timestamp"] = datetime.now().isoformat()
                    
                    # Save updated conversations
                    # success = self._save_conversations_safely(conv_data, username)
                    conv_file = self.get_user_conversations_file(username)
                    success = self._save_conversations_safely(conv_file, conv_data)
                    
                    if success:
                        logger.info(f"✅ Updated feedback for conversation {conversation_id}: {feedback}")
                        return True
                    else:
                        logger.error(f"❌ Failed to save feedback update")
                        return False
            
            logger.warning(f"⚠️ Conversation {conversation_id} not found for feedback update")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to update conversation feedback: {e}")
            return False
    
    def _save_conversations_safely(self, conv_file, conv_data):
        """Simplified but safe file saving approach"""
        
        try:
            # Create backup if file exists
            backup_created = False
            if conv_file.exists():
                try:
                    backup_file = conv_file.with_suffix('.bak')
                    import shutil
                    shutil.copy2(conv_file, backup_file)
                    backup_created = True
                    logger.info(f"🔍 SAVE: Created backup")
                except Exception as backup_error:
                    logger.warning(f"⚠️ SAVE: Backup creation failed: {backup_error}")
            
            # Try direct write first (simpler approach)
            try:
                with open(conv_file, 'w', encoding='utf-8') as f:
                    json.dump(conv_data, f, indent=2, ensure_ascii=False)
                    f.flush()
                    # Force write to disk if possible
                    try:
                        import os
                        if hasattr(os, 'fsync'):
                            os.fsync(f.fileno())
                    except:
                        pass  # fsync not critical
                
                logger.info(f"🔍 SAVE: Direct write successful")
                
                # Quick verification
                try:
                    with open(conv_file, 'r', encoding='utf-8') as f:
                        verification = json.load(f)
                        if len(verification.get("conversations", [])) == len(conv_data["conversations"]):
                            logger.info(f"✅ SAVE: Verification successful")
                            return True
                        else:
                            raise ValueError("Conversation count mismatch")
                except Exception as verify_error:
                    logger.error(f"❌ SAVE: Verification failed: {verify_error}")
                    # Try to restore from backup if we have one
                    if backup_created:
                        try:
                            backup_file = conv_file.with_suffix('.bak')
                            if backup_file.exists():
                                import shutil
                                shutil.copy2(backup_file, conv_file)
                                logger.info("🔄 SAVE: Restored from backup due to verification failure")
                        except Exception as restore_error:
                            logger.error(f"❌ SAVE: Backup restore failed: {restore_error}")
                    return False
                    
            except (PermissionError, OSError) as file_error:
                logger.error(f"❌ SAVE: File operation failed: {file_error}")
                
                # Try alternative approach with temp file
                return self._save_with_temp_file(conv_file, conv_data)
                
        except Exception as e:
            logger.error(f"❌ SAVE: Safe save failed: {e}")
            return False
    
    def _save_with_temp_file(self, conv_file, conv_data):
        """Fallback save method using temporary file"""
        
        try:
            import tempfile
            import shutil
            
            # Use system temp directory
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.json') as temp_f:
                json.dump(conv_data, temp_f, indent=2, ensure_ascii=False)
                temp_f.flush()
                temp_file_path = temp_f.name
            
            logger.info(f"🔍 SAVE: Created temp file: {temp_file_path}")
            
            # Verify temp file
            try:
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    verification = json.load(f)
                    if len(verification.get("conversations", [])) != len(conv_data["conversations"]):
                        raise ValueError("Temp file verification failed")
            except Exception as verify_error:
                logger.error(f"❌ SAVE: Temp file verification failed: {verify_error}")
                try:
                    import os
                    os.unlink(temp_file_path)
                except:
                    pass
                return False
            
            # Move temp file to final location
            try:
                shutil.move(temp_file_path, conv_file)
                logger.info(f"✅ SAVE: Temp file method successful")
                return True
            except Exception as move_error:
                logger.error(f"❌ SAVE: Temp file move failed: {move_error}")
                try:
                    import os
                    os.unlink(temp_file_path)
                except:
                    pass
                return False
                
        except Exception as e:
            logger.error(f"❌ SAVE: Temp file method failed: {e}")
            return False
    
    def get_conversations_by_date(self, username, target_date=None):
        """Get conversations for a specific date"""
        if target_date is None:
            target_date = date.today().isoformat()
        
        try:
            conv_data = self.load_user_conversations(username)
            conversations = [conv for conv in conv_data["conversations"] if conv.get("date") == target_date]
            logger.info(f"🔍 Found {len(conversations)} conversations for {username} on {target_date}")
            return conversations
        except Exception as e:
            logger.error(f"Error getting conversations by date for {username}: {e}")
            return []
    
    def get_recent_conversations(self, username, limit=10):
        """Get recent conversations"""
        try:
            conv_data = self.load_user_conversations(username)
            recent = conv_data["conversations"][-limit:] if conv_data["conversations"] else []
            logger.info(f"🔍 Retrieved {len(recent)} recent conversations for {username}")
            return recent
        except Exception as e:
            logger.error(f"Error getting recent conversations for {username}: {e}")
            return []
    
    def get_conversation_dates(self, username):
        """Get all dates with conversations"""
        try:
            conv_data = self.load_user_conversations(username)
            conversations = conv_data.get("conversations", [])
            
            if not conversations:
                logger.info(f"🔍 No conversations found for {username}")
                return []
            
            dates = list(set(conv.get("date", date.today().isoformat()) for conv in conversations))
            sorted_dates = sorted(dates, reverse=True)
            logger.info(f"🔍 Found conversations on {len(sorted_dates)} different dates for {username}")
            return sorted_dates
        except Exception as e:
            logger.error(f"Error getting conversation dates for {username}: {e}")
            return []
    
    def debug_conversation_status(self, username):
        """Debug method to check conversation saving status"""
        try:
            user_folder = self.auth_manager.get_user_folder(username)
            conv_file = self.get_user_conversations_file(username)
            
            debug_info = {
                "user_folder_exists": user_folder.exists(),
                "user_folder_writable": False,
                "conv_file_exists": conv_file.exists(),
                "conv_file_size": 0,
                "conversation_count": 0,
                "last_conversation": None
            }
            
            if user_folder.exists():
                try:
                    import os
                    debug_info["user_folder_writable"] = os.access(user_folder, os.W_OK)
                except:
                    pass
            
            if conv_file.exists():
                try:
                    debug_info["conv_file_size"] = conv_file.stat().st_size
                    conv_data = self.load_user_conversations(username)
                    debug_info["conversation_count"] = len(conv_data.get("conversations", []))
                    if conv_data.get("conversations"):
                        debug_info["last_conversation"] = conv_data["conversations"][-1]
                except Exception as file_error:
                    debug_info["file_error"] = str(file_error)
            
            logger.info(f"🔍 DEBUG: Conversation status for {username}: {debug_info}")
            return debug_info
            
        except Exception as e:
            logger.error(f"Debug conversation status failed for {username}: {e}")
            return {"error": str(e)}

class UsageTracker:
    def __init__(self, log_file="app_usage.log"):
        self.log_file = Path(log_file)
        self.ensure_log_file()
    
    def ensure_log_file(self):
        """Create log file if it doesn't exist"""
        if not self.log_file.exists():
            with open(self.log_file, 'w') as f:
                json.dump({"usage_logs": []}, f)
    
    def log_activity(self, username, activity_type, details=None):
        """Log user activity"""
        try:
            # Load existing logs
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        except:
            logs = {"usage_logs": []}
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "activity_type": activity_type,  # 'login', 'query', 'file_upload', 'logout'
            "details": details or {}
        }
        
        logs["usage_logs"].append(log_entry)
        
        # Keep only last 10000 logs
        if len(logs["usage_logs"]) > 10000:
            logs["usage_logs"] = logs["usage_logs"][-10000:]
        
        # Save logs
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def log_login(self, username):
        """Log user login"""
        self.log_activity(username, "login")
    
    def log_query(self, username, query, response, confidence, file_type=None):
        """Log user query"""
        details = {
            "query": query[:200],  # Limit query length in logs
            "response_length": len(response),
            "confidence": confidence,
            "file_type": file_type
        }
        self.log_activity(username, "query", details)
    
    def log_file_upload(self, username, file_name, file_type, file_size_mb):
        """Log file upload"""
        details = {
            "file_name": file_name,
            "file_type": file_type,
            "file_size_mb": file_size_mb
        }
        self.log_activity(username, "file_upload", details)
    
    def get_usage_stats(self, username=None, days=7):
        """Get usage statistics"""
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        except:
            return {}
        
        # Filter by user if specified
        if username:
            user_logs = [log for log in logs["usage_logs"] if log["username"] == username]
        else:
            user_logs = logs["usage_logs"]
        
        # Count activities
        stats = {
            "total_activities": len(user_logs),
            "logins": len([log for log in user_logs if log["activity_type"] == "login"]),
            "queries": len([log for log in user_logs if log["activity_type"] == "query"]),
            "file_uploads": len([log for log in user_logs if log["activity_type"] == "file_upload"])
        }
        
        return stats

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

        c = len(common_columns)
        
        if common_columns:
            for col in common_columns[:c]:
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

class AdvancedPDFProcessor:
    """Advanced PDF processing with Docling and ColPali integration"""
    """Fast and efficient PDF processing agent with Ollama integration"""
    
    def __init__(self, ollama_client=None, ollama_model='llama3.2'):
        self.ollama = ollama_client
        self.ollama_model = ollama_model
        self.max_chunk_size = 1000
        self.max_pages = 25  # Limit for performance
        self.ocr_available = self._check_ocr_dependencies() #Added OCR check on 26-08-2025

    def _ocr_page(self, pdf_bytes: bytes, page_number: int) -> str: #Added OCR Page on 26-08-2025
        """Extract text from a specific page using OCR"""
        
        try:
            # Convert specific page to image
            images = convert_from_bytes(
                pdf_bytes,
                first_page=page_number + 1,
                last_page=page_number + 1,
                dpi=300
            )
            
            if not images:
                return ""
            
            # Apply OCR
            page_text = pytesseract.image_to_string(
                images[0],
                config='--oem 3 --psm 6'
            )
            
            return self._clean_ocr_text(page_text)
            
        except Exception as e:
            logger.warning(f"OCR failed for page {page_number + 1}: {e}")
            return ""
        
    def _clean_ocr_text(self, text: str) -> str: #Added OCR Text Cleaning on 26-08-2025
        """Clean OCR text output"""
        
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors
        text = text.replace('|', 'I')
        text = text.replace('0', 'O') if text.count('0') < text.count('O') else text
        
        # Remove artifacts but keep business terms
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\"\'•\d]', ' ', text)
        
        return text.strip()
    
    def _check_ocr_dependencies(self) -> bool: #Added OCR Dependency Check on 26-08-2025
        """Check if OCR dependencies are available"""
        
        try:
            import shutil
            # Check if tesseract is installed
            tesseract_available = shutil.which('tesseract') is not None
            
            # Check if pdf2image is available
            try:
                import pdf2image
                pdf2image_available = True
            except ImportError:
                pdf2image_available = False
            
            if not tesseract_available:
                logger.warning("Tesseract OCR not found. Install with: sudo apt-get install tesseract-ocr")
            
            if not pdf2image_available:
                logger.warning("pdf2image not found. Install with: pip install pdf2image")
            
            return tesseract_available and pdf2image_available
            
        except Exception as e:
            logger.error(f"OCR dependency check failed: {e}")
            return False
        
    def process_pdf_fast(self, pdf_file) -> Dict[str, Any]: #Modified on 26-08-2025 ofr OCR
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
                    'content_length': len(text_content),
                    'ocr_available': self.ocr_available, 
                    'likely_image_based': len(text_content) < 500
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
    
    def _extract_text_pymupdf(self, pdf_bytes: bytes) -> str: #Modified on 26-08-2025 for OCR
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

                    # NEW: If very little text extracted, try OCR
                    if len(cleaned_text.strip()) < 50:  # Threshold for image-based pages
                        logger.info(f"Page {page_num + 1} appears to be image-based, applying OCR...")
                        ocr_text = self._ocr_page(pdf_bytes, page_num)
                        if len(ocr_text.strip()) > len(cleaned_text.strip()):
                            cleaned_text = ocr_text
                    
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

class AdvancedWordProcessor:
    """Advanced Word document processing with Ollama integration - Similar to PDF processor"""
    
    def __init__(self, ollama_client=None, ollama_model='llama3.2'):
        self.ollama = ollama_client
        self.ollama_model = ollama_model
        self.max_chunk_size = 1000
        
    def process_word_fast(self, word_file) -> Dict[str, Any]:
        """Fast Word processing with immediate Q&A capability - Mirror of PDF processor"""
        
        start_time = datetime.now()
        
        try:
            # Reset file pointer
            word_file.seek(0)
            
            # Step 1: Extract text content
            text_content = self._extract_text_docx(word_file)
            
            # Step 2: Extract tables
            tables = self._extract_tables_docx(word_file)
            
            # Step 3: Extract images (basic metadata)
            images = self._extract_images_docx(word_file)
            
            # Step 4: Create semantic chunks for Q&A
            chunks = self._create_smart_chunks(text_content)
            
            # Step 5: Build searchable index
            searchable_content = self._build_searchable_index(chunks, tables)
            
            # Step 6: Structured JSON fallback
            document_json = self._generate_structured_json_fallback(text_content, tables)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'text_content': text_content,
                'tables': tables,
                'images': images,
                'chunks': chunks,
                'searchable_content': searchable_content,
                'document_json': document_json,
                'metadata': {
                    'processing_time': processing_time,
                    'total_chunks': len(chunks),
                    'total_tables': len(tables),
                    'total_images': len(images),
                    'content_length': len(text_content)
                },
                'status': 'success'
            }
            
            logger.info(f"Word document processed in {processing_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Word processing failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'text_content': '',
                'tables': [],
                'images': [],
                'chunks': [],
                'searchable_content': {},
                'document_json': {},
                'metadata': {}
            }
    
    def _extract_text_docx(self, word_file) -> str:
        """Extract text from Word document"""
        
        try:
            word_file.seek(0)
            
            # Method 1: Use python-docx for structured extraction
            try:
                doc = Document(word_file)
                full_text = ""
                
                for i, paragraph in enumerate(doc.paragraphs):
                    if paragraph.text.strip():
                        # Detect headings and structure
                        if paragraph.style.name.startswith('Heading'):
                            full_text += f"\n=== {paragraph.text.strip()} ===\n"
                        else:
                            full_text += paragraph.text.strip() + "\n"
                
                return self._clean_text(full_text)
                
            except Exception as e:
                logger.warning(f"python-docx extraction failed: {e}")
                
                # Method 2: Fallback to docx2txt
                if DOCX2TXT_AVAILABLE:
                    word_file.seek(0)
                    text = docx2txt.process(word_file)
                    return self._clean_text(text)
                
                return f"Error extracting text: {str(e)}"
                
        except Exception as e:
            logger.error(f"Word text extraction failed: {e}")
            return f"Error extracting text: {str(e)}"
    
    def _extract_tables_docx(self, word_file) -> List[Dict[str, Any]]:
        """Extract tables from Word document"""
        
        tables = []
        
        try:
            word_file.seek(0)
            doc = Document(word_file)
            
            for table_idx, table in enumerate(doc.tables):
                try:
                    # Extract table data
                    table_data = []
                    for row in table.rows:
                        row_data = []
                        for cell in row.cells:
                            cell_text = cell.text.strip()
                            row_data.append(cell_text)
                        table_data.append(row_data)
                    
                    if len(table_data) > 1:  # Must have at least header + 1 row
                        processed_table = self._process_word_table(table_data, table_idx)
                        if processed_table:
                            tables.append(processed_table)
                            
                except Exception as e:
                    logger.warning(f"Table processing failed for table {table_idx}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Word table extraction failed: {e}")
        
        return tables
    
    def _extract_images_docx(self, word_file) -> List[Dict[str, Any]]:
        """Extract image metadata from Word document"""
        
        images = []
        
        try:
            word_file.seek(0)
            doc = Document(word_file)
            
            # Count inline shapes (images)
            image_count = 0
            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                    if run._element.xpath('.//pic:pic'):
                        image_count += 1
                        
                        images.append({
                            'index': image_count,
                            'paragraph_index': len(images),
                            'has_text': False,  # Word images don't have OCR in this implementation
                            'ocr_text': '',
                            'type': 'embedded_image'
                        })
                        
        except Exception as e:
            logger.warning(f"Word image extraction failed: {e}")
        
        return images
    
    def _process_word_table(self, table_data: List[List], table_idx: int) -> Optional[Dict[str, Any]]:
        """Process raw Word table into structured format - Mirror of PDF table processing"""
        
        try:
            # Clean headers
            headers = table_data[0] if table_data else []
            clean_headers = []
            
            for i, header in enumerate(headers):
                if header and str(header).strip():
                    clean_headers.append(str(header).strip())
                else:
                    clean_headers.append(f"Column_{i+1}")
            
            # Process data rows
            data_rows = table_data[1:] if len(table_data) > 1 else []
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
                        'table_index': table_idx,
                        'index': table_idx,
                        'dataframe': df,
                        'text_summary': f"Word table {table_idx + 1}: {df.shape[0]} rows, {df.shape[1]} columns",
                        'columns': df.columns.tolist(),
                        'shape': df.shape
                    }
            
            return None
            
        except Exception as e:
            logger.warning(f"Word table processing error: {e}")
            return None
    
    # Reuse methods from PDF processor (they work for any text)
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text - Reuse from PDF processor"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\"\']+', ' ', text)
        
        # Fix common issues
        text = text.replace('`', "'")
        text = text.replace('"', '"').replace('"', '"')
        
        return text.strip()
    
    def _create_smart_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Create semantic chunks optimized for Q&A - Reuse from PDF processor"""
        
        if not text:
            return []
        
        chunks = []
        
        # Split by sections (headings)
        sections = text.split('===')
        
        for section_idx, section_content in enumerate(sections):
            if not section_content.strip():
                continue
            
            # Extract section title if present
            lines = section_content.strip().split('\n')
            section_title = lines[0].strip() if lines else f"Section {section_idx}"
            content = '\n'.join(lines[1:]) if len(lines) > 1 else section_content.strip()
            
            if len(content) <= self.max_chunk_size:
                # Small content, keep as single chunk
                chunks.append({
                    'id': len(chunks),
                    'section': section_title,
                    'content': content,
                    'word_count': len(content.split()),
                    'type': 'section_content'
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
                                'section': section_title,
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
                        'section': section_title,
                        'content': current_chunk.strip(),
                        'word_count': len(current_chunk.split()),
                        'type': 'text_chunk'
                    })
        
        return chunks
    
    def _build_searchable_index(self, chunks: List[Dict], tables: List[Dict]) -> Dict[str, Any]:
        """Build searchable index for fast Q&A - Reuse from PDF processor"""
        
        searchable = {
            'text_chunks': chunks,
            'tables': [],
            'keywords': set(),
            'section_map': {}
        }
        
        # Index chunks by section
        for chunk in chunks:
            section = chunk.get('section', 'Unknown')
            if section not in searchable['section_map']:
                searchable['section_map'][section] = []
            searchable['section_map'][section].append(chunk['id'])
            
            # Extract keywords
            content = chunk['content'].lower()
            words = re.findall(r'\b\w+\b', content)
            searchable['keywords'].update(words)
        
        # Index tables
        for table in tables:
            table_summary = {
                'table_index': table['table_index'],
                'text_summary': table['text_summary'],
                'columns': table['columns'],
                'shape': table['shape']
            }
            searchable['tables'].append(table_summary)
        
        searchable['keywords'] = list(searchable['keywords'])
        return searchable
    
    def _generate_structured_json_fallback(self, text: str, tables: List[Dict]) -> Dict:
        """Generate structured JSON from Word document - Reuse from PDF processor"""
        
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

                # Detect section titles (enhanced for Word documents)
                if (line.startswith('===') and line.endswith('===')) or re.match(r'^[A-Z ]{5,}$', line):
                    # Save previous section
                    if current_section["title"]:
                        structured["sections"].append(current_section)
                    current_section = {"title": line.replace('=', '').strip(), "content": ""}
                else:
                    current_section["content"] += line + " "

                # Detect key-value patterns
                if ":" in line and len(line.split(":")[0].strip()) < 40:
                    k, v = line.split(":", 1)
                    structured["key_value_pairs"][k.strip()] = v.strip()

            # Add last section
            if current_section["title"]:
                structured["sections"].append(current_section)

            return structured

        except Exception as e:
            logger.warning(f"Word JSON fallback structuring failed: {e}")
            return {}
    
    def answer_question(self, question: str, word_content: Dict[str, Any]) -> Dict[str, Any]:
        """Answer questions about the Word document using Ollama - Mirror of PDF Q&A"""
        
        if not self.ollama:
            return {
                'answer': 'Ollama not available for Word Q&A',
                'confidence': 0.0,
                'method': 'error'
            }
        
        if not word_content or word_content.get('status') != 'success':
            return {
                'answer': 'Word document content not available',
                'confidence': 0.0,
                'method': 'error'
            }
        
        try:
            # Step 1: Find relevant chunks
            relevant_chunks = self._find_relevant_content(question, word_content)
            
            # Step 2: Prepare context
            context = self._prepare_context(relevant_chunks, word_content)
            
            # Step 3: Generate answer with Ollama
            answer = self._generate_answer_ollama(question, context)
            
            return {
                'answer': answer['response'],
                'confidence': answer['confidence'],
                'method': 'ollama_rag',
                'relevant_sections': answer.get('sections', []),
                'context_length': len(context)
            }
            
        except Exception as e:
            logger.error(f"Word Q&A failed: {e}")
            return {
                'answer': f'Error processing question: {str(e)}',
                'confidence': 0.0,
                'method': 'error'
            }
    
    def _find_relevant_content(self, question: str, word_content: Dict[str, Any]) -> List[Dict]:
        """Find relevant chunks for the question - Reuse from PDF processor logic"""
        
        question_lower = question.lower()
        question_words = set(re.findall(r'\b\w+\b', question_lower))
        
        chunks = word_content.get('chunks', [])
        relevant_chunks = []
        
        # Score chunks by keyword overlap
        for chunk in chunks:
            content_lower = chunk['content'].lower()
            content_words = set(re.findall(r'\b\w+\b', content_lower))
            
            # Calculate similarity score
            overlap = len(question_words.intersection(content_words))
            
            if overlap > 0:
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
    
    def _prepare_context(self, relevant_chunks: List[Dict], word_content: Dict[str, Any]) -> str:
        """Prepare context for Ollama - Reuse from PDF processor"""
        
        context_parts = []
        
        # Add text chunks
        for chunk in relevant_chunks:
            section = chunk.get('section', 'Unknown')
            content = chunk['content']
            context_parts.append(f"[Section: {section}] {content}")
        
        # Add relevant table information
        tables = word_content.get('tables', [])
        for table in tables[:2]:  # Limit to 2 tables
            table_summary = table.get('text_summary', '')
            if table_summary:
                context_parts.append(f"[Table] {table_summary}")
        
        return "\n\n".join(context_parts)
    
    def _generate_answer_ollama(self, question: str, context: str) -> Dict[str, Any]:
        """Generate answer using Ollama - Reuse from PDF processor"""
        
        prompt = f"""Based on the following Word document content, answer the user's question accurately and concisely.

DOCUMENT CONTENT:
{context}

USER QUESTION: {question}

Instructions:
- Answer based only on the provided document content
- If the answer is not in the document, say "I cannot find this information in the document"
- Be specific and cite sections when possible
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
            
            # Extract section references
            section_refs = re.findall(r'[Ss]ection[:\s]+([^,\n]+)', answer_text)
            sections = list(set(section_refs))
            
            # Estimate confidence based on answer quality
            confidence = self._estimate_answer_confidence(answer_text, context)
            
            return {
                'response': answer_text,
                'confidence': confidence,
                'sections': sections
            }
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return {
                'response': f"Error generating answer: {str(e)}",
                'confidence': 0.0,
                'sections': []
            }
    
    def _estimate_answer_confidence(self, answer: str, context: str) -> float:
        """Estimate confidence in the answer - Reuse from PDF processor"""
        
        # Simple confidence estimation
        if "cannot find" in answer.lower() or "not in the document" in answer.lower():
            return 0.2
        
        # Check if answer contains specific information
        if any(keyword in answer.lower() for keyword in ['section', 'table', 'figure']):
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

class AdvancedCSVProcessor:
    """Advanced CSV/Excel processing with Ollama integration for Q&A"""
    
    def __init__(self, ollama_client=None, ollama_model='llama3.2'):
        self.ollama = ollama_client
        self.ollama_model = ollama_model
        self.max_chunk_size = 1000
        
    def process_csv_fast(self, df, file_name=None) -> Dict[str, Any]:
        """Fast CSV/Excel processing with immediate Q&A capability"""
        
        start_time = datetime.now()
        
        try:
            # Step 1: Create data summary and structure
            data_summary = self._create_data_summary(df)
            
            # Step 2: Generate semantic chunks for different aspects
            chunks = self._create_data_chunks(df, data_summary)
            
            # Step 3: Build searchable index
            searchable_content = self._build_searchable_index(chunks, df)
            
            # Step 4: Create JSON representation for context
            data_json = self._generate_structured_json(df, data_summary)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'data_summary': data_summary,
                'chunks': chunks,
                'searchable_content': searchable_content,
                'data_json': data_json,
                'dataframe': df,  # Include the actual dataframe
                'metadata': {
                    'processing_time': processing_time,
                    'total_chunks': len(chunks),
                    'file_name': file_name,
                    'rows': len(df),
                    'columns': len(df.columns)
                },
                'status': 'success'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"CSV processing failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'data_summary': {},
                'chunks': [],
                'searchable_content': {},
                'data_json': {},
                'metadata': {}
            }
    
    def _create_data_summary(self, df):
        """Create comprehensive data summary"""
        
        summary = {
            'basic_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
            },
            'data_types': {},
            'statistics': {},
            'sample_data': {},
            'missing_data': {}
        }
        
        # Data types analysis
        for col in df.columns:
            dtype = str(df[col].dtype)
            summary['data_types'][col] = dtype
            
            # Get sample values
            non_null_values = df[col].dropna()
            if len(non_null_values) > 0:
                summary['sample_data'][col] = non_null_values.head(3).tolist()
            
            # Missing data
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                summary['missing_data'][col] = {
                    'count': int(missing_count),
                    'percentage': float(missing_count / len(df) * 100)
                }
        
        # Statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            try:
                summary['statistics'][col] = {
                    'mean': float(df[col].mean()),
                    'median': float(df[col].median()),
                    'std': float(df[col].std()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'unique_count': int(df[col].nunique())
                }
            except:
                continue
        
        # Top categories for categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            try:
                value_counts = df[col].value_counts().head(5)
                summary['statistics'][col] = {
                    'unique_count': int(df[col].nunique()),
                    'top_values': dict(value_counts)
                }
            except:
                continue
        
        return summary
    
    def _create_data_chunks(self, df, summary):
        """Create semantic chunks with ACTUAL DATA and advanced analytics for Q&A"""
        
        chunks = []
        dataset_size = len(df)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        # Chunk 1: PRIORITY - Calculations and essential data
        # Keep this chunk focused and context-efficient
        max_display_rows = min(30, dataset_size)  # Never show more than 30 rows
        
        if dataset_size <= 30:
            data_display = df.to_string(index=True, max_cols=8)
            data_label = "COMPLETE DATASET"
        else:
            # Strategic sampling for larger datasets
            try:
                sample_df = pd.concat([
                    df.head(15),
                    df.tail(15)
                ]).drop_duplicates()
                data_display = sample_df.to_string(index=True, max_cols=8)
                data_label = f"KEY DATA SAMPLE ({len(sample_df)} of {dataset_size:,} rows)"
            except Exception:
                data_display = df.head(20).to_string(index=True, max_cols=8)
                data_label = "DATA SAMPLE (first 20 rows)"
        
        # Build primary chunk with calculations FIRST
        overview_text = f"""Dataset: {dataset_size:,} rows × {len(df.columns)} columns

        IMMEDIATE CALCULATIONS - ALL NUMERIC STATISTICS:"""

        # Add all numeric column totals upfront
        if len(numeric_cols) > 0:
            for col in numeric_cols:
                try:
                    total = df[col].sum()
                    mean = df[col].mean()
                    minimum = df[col].min()
                    maximum = df[col].max()
                    median = df[col].median()
                    count = df[col].count()
                    overview_text += f"\n\n• {col.upper()} COLUMN COMPLETE ANALYSIS:"
                    overview_text += f"\n  - MINIMUM VALUE (CHEAPEST): {minimum:,.2f}"
                    overview_text += f"\n  - MAXIMUM VALUE (MOST EXPENSIVE): {maximum:,.2f}"
                    overview_text += f"\n  - AVERAGE/MEAN VALUE: {mean:,.2f}"
                    overview_text += f"\n  - MEDIAN VALUE: {median:,.2f}"
                    overview_text += f"\n  - TOTAL SUM: {total:,.2f}"
                    overview_text += f"\n  - TOTAL COUNT: {count:,}"
                except Exception as e:
                    overview_text += f"\n• {col.upper()}: Calculation failed ({str(e)})"
        else:
            overview_text += "\n(No numeric columns found for calculations)"

        # Add column information
        overview_text += f"\n\nDATASET STRUCTURE:"
        overview_text += f"\nAll Columns: {', '.join(df.columns.tolist())}"
        overview_text += f"\nNumeric Columns: {', '.join(numeric_cols.tolist()) if len(numeric_cols) > 0 else 'None'}"

        # Add sample data last
        overview_text += f"\n\n{data_label}:\n{data_display}"
        
        chunks.append({
            'id': len(chunks),
            'type': 'complete_data_with_calculations',
            'content': overview_text.strip(),
            'metadata': {'section': 'primary_data', 'priority': 1}
        })
        
        # Chunk 2: Quick reference totals (redundancy for reliability)
        if len(numeric_cols) > 0:
            quick_totals = "QUICK REFERENCE - ALL CALCULATIONS:\n"
            for col in numeric_cols:
                try:
                    total = df[col].sum()
                    mean = df[col].mean()
                    minimum = df[col].min()
                    maximum = df[col].max()
                    median = df[col].median()
                    quick_totals += f"\n{col.upper()} QUICK STATS:"
                    quick_totals += f"\n  CHEAPEST/MIN = {minimum:,.2f}"
                    quick_totals += f"\n  MOST_EXPENSIVE/MAX = {maximum:,.2f}"
                    quick_totals += f"\n  AVERAGE = {mean:,.2f}"
                    quick_totals += f"\n  MEDIAN = {median:,.2f}"
                    quick_totals += f"\n  TOTAL = {total:,.2f}"
                except Exception as e:
                    quick_totals += f"\n{col} = ERROR ({str(e)})"
            
            chunks.append({
                'id': len(chunks),
                'type': 'quick_totals',
                'content': quick_totals.strip(),
                'metadata': {'section': 'totals', 'priority': 2}
            })
        
        # Chunk 3: Additional data rows if dataset is larger
        if dataset_size > 30:
            try:
                # Show middle section of data
                start_idx = max(15, dataset_size // 2 - 10)
                end_idx = min(dataset_size - 15, dataset_size // 2 + 10)
                
                if start_idx < end_idx:
                    middle_data = df.iloc[start_idx:end_idx]
                    additional_text = f"ADDITIONAL DATA ROWS (rows {start_idx}-{end_idx-1}):\n"
                    additional_text += middle_data.to_string(index=True, max_cols=8)
                    
                    chunks.append({
                        'id': len(chunks),
                        'type': 'additional_data',
                        'content': additional_text,
                        'metadata': {'section': 'data', 'priority': 3}
                    })
            except Exception as e:
                pass  # Skip if middle data extraction fails
        
        # Chunk 4: Statistical details (only for small number of numeric columns)
        if len(numeric_cols) > 0 and len(numeric_cols) <= 5:
            stats_text = "STATISTICAL DETAILS:\n"
            for col in numeric_cols:
                try:
                    stats_text += f"\n{col}:\n"
                    stats_text += f"  Min: {df[col].min():,.2f} | Max: {df[col].max():,.2f}\n"
                    stats_text += f"  Median: {df[col].median():,.2f} | Std Dev: {df[col].std():,.2f}\n"
                    stats_text += f"  Non-null: {df[col].count():,} | Missing: {df[col].isnull().sum():,}\n"
                except Exception as e:
                    stats_text += f"\n{col}: Statistics error - {str(e)}\n"
            
            chunks.append({
                'id': len(chunks),
                'type': 'detailed_statistics',
                'content': stats_text.strip(),
                'metadata': {'section': 'statistics', 'priority': 4}
            })
        
        # Chunk 5: Categorical analysis (if not too many categories)
        if len(categorical_cols) > 0 and len(categorical_cols) <= 3:
            categorical_text = "CATEGORICAL DATA:\n"
            
            for col in categorical_cols:
                try:
                    value_counts = df[col].value_counts()
                    categorical_text += f"\n{col} ({df[col].nunique()} unique values):\n"
                    
                    # Show top 3 values only to save space
                    for idx, (value, count) in enumerate(value_counts.head(3).items()):
                        percentage = (count / len(df)) * 100
                        categorical_text += f"  {idx+1}. '{value}': {count:,} ({percentage:.1f}%)\n"
                        
                except Exception as e:
                    categorical_text += f"\n{col}: Analysis failed - {str(e)}\n"
            
            chunks.append({
                'id': len(chunks),
                'type': 'categorical_analysis',
                'content': categorical_text.strip(),
                'metadata': {'section': 'categorical', 'priority': 5}
            })
        
        # Chunk 6: Basic data quality (compact version)
        missing_info = []
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_pct = (missing_count / len(df)) * 100
                missing_info.append(f"{col}: {missing_count} missing ({missing_pct:.1f}%)")
        
        quality_text = f"DATA QUALITY:\n"
        quality_text += f"Total rows: {len(df):,} | Complete rows: {df.dropna().shape[0]:,}\n"
        
        if missing_info:
            quality_text += f"Missing data:\n" + "\n".join(missing_info[:5])  # Limit to 5 columns
        else:
            quality_text += "No missing data detected"
        
        chunks.append({
            'id': len(chunks),
            'type': 'data_quality',
            'content': quality_text.strip(),
            'metadata': {'section': 'quality', 'priority': 6}
        })
        
        return chunks
    
    def answer_question(self, question: str, csv_content: Dict[str, Any]) -> Dict[str, Any]:
        """Answer questions about CSV/Excel data using Ollama with data context"""
        
        if not self.ollama:
            return {
                'answer': 'Ollama not available for CSV Q&A',
                'confidence': 0.0,
                'method': 'error'
            }
        
        if not csv_content or csv_content.get('status') != 'success':
            return {
                'answer': 'CSV content not available',
                'confidence': 0.0,
                'method': 'error'
            }
        
        try:
            # Get the first chunk which should contain all calculations
            chunks = csv_content.get('chunks', [])
            if not chunks:
                return {
                    'answer': 'No processed data available',
                    'confidence': 0.0,
                    'method': 'error'
                }
            
            # Use the primary chunk with all calculations
            primary_chunk = chunks[0]  # This contains complete calculations
            context = primary_chunk['content']
            
            # Detect if it's a calculation question
            calc_keywords = [
                'total', 'sum', 'amount', 'calculate', 'mean', 'average', 'count',
                'cheapest', 'expensive', 'minimum', 'maximum', 'min', 'max',
                'median', 'lowest', 'highest', 'cost', 'price'
            ]
            is_calculation = any(word in question.lower() for word in calc_keywords)
            
            # Create enhanced prompt
            if is_calculation:
                prompt = f"""You are analyzing a dataset. All statistics have been pre-calculated and are provided below.

    COMPLETE DATASET ANALYSIS WITH PRE-CALCULATED VALUES:
    {context}

    USER QUESTION: {question}

    CRITICAL INSTRUCTIONS:
    - Use ONLY the exact pre-calculated values shown above
    - For "cheapest", "lowest", "minimum": Look for "MINIMUM VALUE" or "MIN ="
    - For "most expensive", "highest", "maximum": Look for "MAXIMUM VALUE" or "MAX ="
    - For "average", "mean": Look for "AVERAGE/MEAN VALUE" or "AVERAGE ="
    - For "total", "sum": Look for "TOTAL SUM" or "TOTAL ="
    - Always provide the specific numeric value with proper formatting
    - Be precise and cite which column you're using

    ANSWER:"""
            else:
                prompt = f"""Based on the following dataset analysis, answer the user's question.

    DATASET ANALYSIS:
    {context}

    USER QUESTION: {question}

    Provide a clear answer based on the information provided.

    ANSWER:"""
            
            # Generate response with Ollama
            try:
                response = self.ollama.generate(
                    model=self.ollama_model,
                    prompt=prompt,
                    options={
                        "temperature": 0.1,  # Very low for precise calculations
                        "top_p": 0.9,
                        "num_predict": 400
                    }
                )
                
                answer_text = response['response'].strip()
                
                # Higher confidence for calculation queries that mention specific values
                if is_calculation and any(word in answer_text.lower() for word in ['minimum', 'maximum', 'average']):
                    confidence = 0.95
                else:
                    confidence = 0.8
                
                return {
                    'answer': answer_text,
                    'confidence': confidence,
                    'method': 'ollama_csv_rag',
                    'relevant_sections': ['calculations'],
                    'context_length': len(context)
                }
                
            except Exception as e:
                logger.error(f"Ollama generation failed: {e}")
                return {
                    'answer': f'Error generating answer: {str(e)}',
                    'confidence': 0.0,
                    'method': 'error'
                }
                
        except Exception as e:
            logger.error(f"CSV Q&A failed: {e}")
            return {
                'answer': f'Error processing question: {str(e)}',
                'confidence': 0.0,
                'method': 'error'
            }

    def _build_searchable_index(self, chunks: List[Dict], df) -> Dict[str, Any]:
        """Build searchable index for CSV Q&A"""
        
        searchable = {
            'text_chunks': chunks,
            'data_summary': {},
            'keywords': set(),
            'column_map': {}
        }
        
        # Index chunks
        for chunk in chunks:
            content = chunk['content'].lower()
            words = re.findall(r'\b\w+\b', content)
            searchable['keywords'].update(words)
        
        # Index columns
        for col in df.columns:
            searchable['column_map'][col] = {
                'type': str(df[col].dtype),
                'unique_count': df[col].nunique(),
                'has_nulls': df[col].isnull().any()
            }
        
        searchable['keywords'] = list(searchable['keywords'])
        return searchable

    def _generate_structured_json(self, df, summary) -> Dict:
        """Generate structured JSON representation of the data"""
        
        structured = {
            "data_overview": summary['basic_info'],
            "columns": {},
            "sample_records": []
        }
        
        # Column details
        for col in df.columns:
            structured["columns"][col] = {
                "type": str(df[col].dtype),
                "sample_values": df[col].dropna().head(3).tolist() if not df[col].empty else [],
                "unique_count": int(df[col].nunique()),
                "null_count": int(df[col].isnull().sum())
            }
        
        # Sample records
        try:
            structured["sample_records"] = df.head(3).to_dict('records')
        except Exception as e:
            logger.warning(f"Could not generate sample records: {e}")
            structured["sample_records"] = []
        
        return structured

    def _find_relevant_content(self, question: str, csv_content: Dict[str, Any]) -> List[Dict]:
        """Find relevant chunks for the question"""
        
        question_lower = question.lower()
        question_words = set(re.findall(r'\b\w+\b', question_lower))
        
        chunks = csv_content.get('chunks', [])
        relevant_chunks = []

        # PRIORITY: For calculation questions, always include calculation chunks first
        is_calculation_query = any(word in question_lower for word in [
            'total', 'sum', 'amount', 'calculate', 'mean', 'average', 'count', 
            'cheapest', 'expensive', 'minimum', 'maximum', 'min', 'max', 'median', 
            'price', 'lowest', 'highest', 'cost'
        ])
        
        # Score chunks by keyword overlap
        for chunk in chunks:
            content_lower = chunk['content'].lower()
            content_words = set(re.findall(r'\b\w+\b', content_lower))
            
            # Calculate similarity score
            overlap = len(question_words.intersection(content_words))
            
            if overlap > 0:
                similarity = overlap / len(question_words) if len(question_words) > 0 else 0
                
                # BOOST calculation-related chunks for calculation queries
                if is_calculation_query:
                    chunk_type = chunk.get('type', '')
                    if chunk_type in ['complete_data_with_calculations', 'quick_totals']:
                        similarity += 0.9  # High boost
                    elif chunk_type in ['detailed_statistics']:
                        similarity += 0.5  # Medium boost

                # Add context bonus for certain keywords
                if any(keyword in content_lower for keyword in ['column', 'data', 'statistics', 'values', 'price', 'min', 'max', 'total']):
                    similarity += 0.1
                
                if similarity > 0.1:  # Minimum relevance threshold
                    chunk_with_score = chunk.copy()
                    chunk_with_score['relevance_score'] = similarity
                    relevant_chunks.append(chunk_with_score)
        
        # Sort by relevance and return top chunks
        relevant_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_chunks[:5]  # Top 5 most relevant chunks

    def _prepare_context(self, question: str, relevant_chunks: List[Dict], csv_content: Dict[str, Any], df) -> str:
        context_parts = []
        max_context_length = 15000  # Adjust based on your model's limits
        # PRIORITY: For calculation questions, include targeted data
        if any(word in question.lower() for word in [
            'total', 'sum', 'amount', 'calculate', 'mean', 'average', 'count', 
            'how many', 'cheapest', 'expensive', 'minimum', 'maximum', 'min', 'max', 
            'median', 'lowest', 'highest', 'cost', 'price'
        ]):
            
            # Find the most relevant chunk with calculations (should be chunk 0 or 1)
            calc_chunk = None
            for chunk in relevant_chunks:
                if chunk.get('type') in ['complete_data_with_calculations', 'quick_totals']:
                    calc_chunk = chunk
                    break
            
            if calc_chunk:
                context_parts.insert(0, f"[PRIORITY_CALCULATIONS]\n{calc_chunk['content']}")
            else:
                # Fallback: include essential data
                essential_data = f"ESSENTIAL DATA FOR CALCULATIONS:\n{df.head(20).to_string(index=True)}\n\nCOMPLETE TOTALS:\n"
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    try:
                        essential_data += f"{col}: TOTAL={df[col].sum():,.2f} | MIN={df[col].min():,.2f} | MAX={df[col].max():,.2f} | AVG={df[col].mean():,.2f}\n"
                    except:
                        pass
                context_parts.insert(0, essential_data)
        
        # Add other relevant chunks (but limit total context)
        current_length = len(context_parts[0]) if context_parts else 0
        for chunk in relevant_chunks[:3]:  # Limit chunks to manage context size
            chunk_content = f"[{chunk.get('type', 'unknown').upper()}]\n{chunk['content']}"
            if current_length + len(chunk_content) < max_context_length:
                context_parts.append(chunk_content)
                current_length += len(chunk_content)
            else:
                break
        
        return "\n\n".join(context_parts)

    def _generate_answer_ollama(self, question: str, context: str) -> Dict[str, Any]:
        # Detect calculation queries
        is_calculation = any(word in question.lower() for word in [
            'total', 'sum', 'amount', 'calculate', 'mean', 'average', 'count', 
            'how many', 'cheapest', 'expensive', 'minimum', 'maximum', 'min', 'max', 
            'median', 'lowest', 'highest', 'cost', 'price'
        ])
        
        if is_calculation:
            prompt = f"""You are analyzing a dataset to answer calculation questions. The data and pre-calculated statistics are provided below.

        DATASET WITH CALCULATIONS:
        {context}

        USER QUESTION: {question}

        CRITICAL INSTRUCTIONS FOR CALCULATIONS:
        - Use the exact pre-calculated values shown above
        - For "cheapest", "lowest", "minimum" questions: use the MINIMUM value from the relevant column
        - For "most expensive", "highest", "maximum" questions: use the MAXIMUM value from the relevant column  
        - For "average", "mean" questions: use the AVERAGE/MEAN value from the relevant column
        - For "total", "sum" questions: use the TOTAL SUM from the relevant column
        - Always provide the exact numeric answer with proper formatting
        - Be specific about which column you're referencing
        - Format large numbers with commas (e.g., 1,234,567.89)

        ANSWER:"""
        else:
            prompt = f"""Based on the following dataset information, answer the user's question accurately and concisely.

    DATASET INFORMATION:
    {context}

    USER QUESTION: {question}

    Instructions:
    - Answer based only on the provided dataset information
    - Be specific about data types, statistics, and patterns when relevant
    - Keep the answer concise but informative

    ANSWER:"""

        try:
            response = self.ollama.generate(
                model=self.ollama_model,
                prompt=prompt,
                options={
                    "temperature": 0.3,  # Lower temperature for more precise calculations
                    "top_p": 0.95,
                    "num_predict": 600
                }
            )
            
            answer_text = response['response'].strip()
            
            # Estimate confidence based on answer quality
            confidence = self._estimate_answer_confidence(answer_text, context)
            
            return {
                'response': answer_text,
                'confidence': confidence,
                'sections': []  # Could extract mentioned columns/sections
            }
            
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return {
                'response': f"Error generating answer: {str(e)}",
                'confidence': 0.0,
                'sections': []
            }
    def _estimate_answer_confidence(self, answer: str, context: str) -> float:
        """Estimate confidence in the answer"""
        
        # Simple confidence estimation
        if "would need to analyze" in answer.lower() or "not shown" in answer.lower():
            return 0.3
        
        # Check if answer contains specific information
        if any(keyword in answer.lower() for keyword in ['column', 'rows', 'data', 'values']):
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
            return 0.4
        
# ============================================================================
# 6 . DATA LOADING AND VALIDATION
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
        
        #logger.info(f"Data loaded successfully: {len(df)} rows, {len(df.columns)} columns")
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

# ============================================================================
# 7. 📄 DOCUMENT PROCESSING WORD/EXCEL/CSV AND TRACKING
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
        
        #st.success(f"✅ PDF processed in {processing_time:.2f} seconds")
        
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
        
        # if info_parts:
        #     st.info(f"📄 Extracted: {', '.join(info_parts)}")
        
        # Store the PDF agent in session state for Q&A
        st.session_state['pdf_agent'] = pdf_agent
        
        return content
    
    elif content and content['status'] == 'error':
        st.error(f"❌ PDF processing failed: {content.get('error', 'Unknown error')}")
        return None
    
    else:
        st.error("❌ PDF processing failed: Unknown error")
        return None

@enhanced_error_handling
def extract_comprehensive_word_content(word_file):
    """Extract Word content using AdvancedWordProcessor"""
    
    if not WORD_PROCESSING_AVAILABLE:
        st.error("Word processing libraries not available")
        return None
    
    # Initialize AdvancedWordProcessor with Ollama
    word_agent = AdvancedWordProcessor(
        ollama_client=AI_MODELS.get('ollama'),
        ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
    )
    
    with st.spinner("🔄 Processing Word document..."):
        content = word_agent.process_word_fast(word_file)
    
    if content and content['status'] == 'success':
        # Display processing info
        metadata = content.get('metadata', {})
        processing_time = metadata.get('processing_time', 0)
        
        #st.success(f"✅ Word document processed in {processing_time:.2f} seconds")
        
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
        
        # if info_parts:
        #     st.info(f"📄 Extracted: {', '.join(info_parts)}")
        
        # Store the Word agent in session state for Q&A
        st.session_state['word_agent'] = word_agent
        
        return content
    
    elif content and content['status'] == 'error':
        st.error(f"❌ Word processing failed: {content.get('error', 'Unknown error')}")
        return None
    
    else:
        st.error("❌ Word processing failed: Unknown error")
        return None

def track_file_upload(username, file_name, file_type, file_size_mb):
    """Enhanced file upload tracking with error handling"""
    try:
        if not username or not st.session_state.get('usage_tracker'):
            logger.warning(f"⚠️ Cannot track upload - Username: {username}, Tracker available: {st.session_state.get('usage_tracker') is not None}")
            return
        
        # Log the upload
        st.session_state.usage_tracker.log_file_upload(
            username=username,
            file_name=str(file_name),
            file_type=str(file_type),
            file_size_mb=float(file_size_mb)
        )
        
        logger.info(f"✅ File upload tracked: {file_name} ({file_type}, {file_size_mb:.1f}MB) for {username}")
        
    except Exception as e:
        logger.error(f"❌ File upload tracking failed: {e}")

# ==================================================================================
# 8. 🎯 PROCESS CONVERSATION AND SAVE
# ==================================================================================

@track_performance("AI Query Processing")
def process_enhanced_query(df, query, conversation_history=None):
    """Simplified query processing for interactive tabular analysis"""
    
    if not query or len(query.strip()) == 0:
        return {
            'answer': 'Please provide a valid query',
            'confidence': 0.0,
            'method': 'validation_error'
        }
    
    try:
        query_lower = query.lower()
        
        # Simple query processing for basic stats
        if any(word in query_lower for word in ['count', 'how many', 'rows']):
            answer = f"The dataset contains {len(df):,} rows and {len(df.columns)} columns"
            confidence = 0.9
        elif any(word in query_lower for word in ['columns', 'column names']):
            cols = list(df.columns)
            answer = f"Dataset has {len(cols)} columns: {', '.join(cols[:10])}{'...' if len(cols) > 10 else ''}"
            confidence = 0.9
        elif any(word in query_lower for word in ['summary', 'describe', 'overview']):
            numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
            categorical_cols = len(df.select_dtypes(include=['object', 'category']).columns)
            answer = f"Dataset overview: {len(df):,} rows, {len(df.columns)} columns ({numeric_cols} numeric, {categorical_cols} categorical)"
            confidence = 0.8
        else:
            answer = "For detailed analysis of your data, please use the Q&A Chat mode which provides advanced AI-powered insights."
            confidence = 0.5
        
        result = {
            'answer': answer,
            'confidence': confidence,
            'method': 'simple_tabular'
        }
        
        # Save conversation
        _save_conversation_immediately(query, result)
        return result
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        result = {
            'answer': f"Error processing query: {str(e)}",
            'confidence': 0.1,
            'method': 'error'
        }
        _save_conversation_immediately(query, result)
        return result

def _save_conversation_immediately(query, result):
    """GUARANTEED conversation saving - NEW HELPER FUNCTION"""
    
    try:
        # Enhanced safety checks with detailed logging
        is_authenticated = st.session_state.get('authenticated', False)
        username = st.session_state.get('username')
        conv_manager = st.session_state.get('conv_manager')
        
        logger.info(f"💾 IMMEDIATE SAVE - Auth: {is_authenticated}, User: {username}, ConvMgr: {conv_manager is not None}")
        
        if not is_authenticated:
            logger.warning("❌ SAVE SKIPPED: User not authenticated")
            return False
        
        if not username or username.strip() == "":
            logger.warning("❌ SAVE SKIPPED: Username is empty or None")
            return False
        
        if not conv_manager:
            logger.warning("❌ SAVE SKIPPED: ConversationManager not available")
            return False
        
        if 'answer' not in result:
            logger.warning("❌ SAVE SKIPPED: No answer in result")
            return False
        
        # Prepare safe data for saving
        safe_query = str(query)[:500] if query else "Unknown query"
        safe_answer = str(result['answer'])[:1000] if result.get('answer') else "No answer"
        safe_confidence = float(result.get('confidence', 0.0))
        safe_file_type = str(st.session_state.get('file_type', 'unknown'))
        
        logger.info(f"💾 ATTEMPTING IMMEDIATE SAVE for user: {username}")
        logger.info(f"💾 Query: {safe_query[:50]}...")
        logger.info(f"💾 Answer: {safe_answer[:50]}...")
        logger.info(f"💾 File type: {safe_file_type}")
        
        # Attempt to save conversation
        save_success = conv_manager.save_conversation(
            username=username,
            conversation_type='data_query',
            query=safe_query,
            response=safe_answer,
            confidence=safe_confidence,
            file_type=safe_file_type,
            feedback=None
        )
        
        if save_success:
            logger.info("✅ IMMEDIATE SAVE: Conversation saved successfully")
            
            # Also save usage tracking
            try:
                usage_tracker = st.session_state.get('usage_tracker')
                if usage_tracker:
                    usage_tracker.log_query(
                        username=username,
                        query=safe_query,
                        response=safe_answer,
                        confidence=safe_confidence,
                        file_type=safe_file_type
                    )
                    logger.info("✅ IMMEDIATE SAVE: Usage tracking saved")
                else:
                    logger.warning("⚠️ IMMEDIATE SAVE: Usage tracker not available")
            except Exception as usage_error:
                logger.error(f"❌ IMMEDIATE SAVE: Usage tracking failed: {usage_error}")
            
            return True
        else:
            logger.error("❌ IMMEDIATE SAVE: Conversation save returned False")
            return False
            
    except Exception as e:
        logger.error(f"❌ IMMEDIATE SAVE: Critical failure: {e}")
        import traceback
        logger.error(f"❌ IMMEDIATE SAVE: Full traceback: {traceback.format_exc()}")
        return False
         
# ============================================================================
# 9. 🎨 USER INTERFACE COMPONENTS with Feedback
# ============================================================================

def display_authentication():
    """Display login/registration interface with professional styling"""
    
    if st.session_state.auth_manager is None:
        st.error("❌ Authentication system not available. Please refresh the page.")
        if st.button("🔄 Refresh Page"):
            st.rerun()
        return
    
    # Center the content with custom CSS
    st.markdown("""
    <style>
        .auth-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .auth-header {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
        }
        .stTextInput > div > div > input {
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-header">
        <h1>🤖 AI Data NooB </h1>
        <h3>Please Login or Register to Continue</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create centered container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab1:
            st.subheader("Login to Your Account")
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
                with submit_col2:
                    login_submitted = st.form_submit_button("🔑 Login", type="primary", use_container_width=True)
                
                if login_submitted:
                    if username and password:
                        success, message = st.session_state.auth_manager.login_user(username, password)
                        
                        if success:
                            # IMPORTANT: Ensure session state is properly set
                            st.session_state.authenticated = True
                            st.session_state.username = username  # Use the actual input username
                            st.session_state.current_user = username  # Add backup reference
                            st.session_state.show_login = False
                            
                            # Validate that username is correctly stored
                            if st.session_state.username != username:
                                st.error("⚠️ Session state error. Please try logging in again.")
                                return
                            
                            if st.session_state.usage_tracker:
                                st.session_state.usage_tracker.log_login(username)
                            
                            st.success(f"✅ Welcome back, {username}!")
                            time.sleep(1)  # Brief pause for user to see success message
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("Please enter both username and password")
        
        with tab2:
            st.subheader("Create New Account")
            
            # Add Terms and Conditions checkbox
            show_terms = st.checkbox("📋 Show Terms and Conditions")
            
            if show_terms:
                with st.expander("📄 Terms and Conditions", expanded=True):
                    try:
                        # Try to load terms from file
                        with open("END USER LICENSE AGREEMENT.txt", "r", encoding="utf-8") as f:
                            terms_content = f.read()
                        st.text_area("", terms_content, height=300, disabled=True)
                    except FileNotFoundError:
                        st.warning("Terms and Conditions document not found. Please contact administrator.")
                        terms_content = "Terms and Conditions document not available."
            
            with st.form("register_form"):
                new_username = st.text_input("Choose Username", placeholder="Enter desired username")
                new_email = st.text_input("Email (optional)", placeholder="your.email@example.com")
                new_password = st.text_input("Choose Password", type="password", placeholder="Enter secure password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                
                # Terms agreement checkbox
                terms_agreed = st.checkbox("I agree to the Terms and Conditions", key="terms_agreement")
                
                submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
                with submit_col2:
                    register_submitted = st.form_submit_button("📝 Register", type="primary", use_container_width=True)
                
                if register_submitted:
                    if not terms_agreed:
                        st.error("❌ Please agree to the Terms and Conditions to register")
                    elif new_username and new_password:
                        if new_password != confirm_password:
                            st.error("❌ Passwords don't match")
                        else:
                            success, message = st.session_state.auth_manager.register_user(
                                new_username, new_password, new_email
                            )
                            
                            if success:
                                st.success(f"✅ {message}. You can now login!")
                            else:
                                st.error(f"❌ {message}")
                    else:
                        st.error("Please enter username and password")

def display_conversation_history_sidebar():
    """Display conversation history in sidebar - ENHANCED FIX"""
    
    # Enhanced safety checks
    if (not st.session_state.get('authenticated', False) or 
        not st.session_state.get('username') or 
        not st.session_state.get('conv_manager')):
        return
    
    username = st.session_state.username
    
    try:
        st.sidebar.markdown("---")
        st.sidebar.subheader("💬 Conversation History")
        
        # Get conversation dates with error handling
        try:
            conv_dates = st.session_state.conv_manager.get_conversation_dates(username)
            logger.info(f"🔍 Found {len(conv_dates)} conversation dates for {username}")
        except Exception as e:
            logger.error(f"Failed to get conversation dates: {e}")
            st.sidebar.error("Error loading conversation dates")
            return
        
        if conv_dates:
            # Date selector
            selected_date = st.sidebar.selectbox(
                "Select Date:",
                conv_dates,
                format_func=lambda x: datetime.fromisoformat(x).strftime("%B %d, %Y"),
                key="conv_date_selector"
            )
            
            # Get conversations for selected date
            try:
                conversations = st.session_state.conv_manager.get_conversations_by_date(username, selected_date)
                logger.info(f"🔍 Found {len(conversations)} conversations for {username} on {selected_date}")
            except Exception as e:
                logger.error(f"Failed to get conversations: {e}")
                st.sidebar.error("Error loading conversations")
                return
            
            if conversations:
                st.sidebar.markdown(f"**{len(conversations)} conversations on {selected_date}**")
                
                # Display conversations (show last 10, most recent first)
                recent_conversations = conversations[-10:][::-1]  # Last 10, reversed
                
                for i, conv in enumerate(recent_conversations):
                    try:
                        # Extract time from timestamp
                        timestamp = conv.get('timestamp', '00:00:00')
                        if 'T' in timestamp:
                            time_part = timestamp.split('T')[1][:5]  # Get HH:MM
                        else:
                            time_part = timestamp[11:16] if len(timestamp) > 16 else timestamp[:5]
                        
                        # Create expander title
                        conv_type = conv.get('type', 'query')
                        expander_title = f"{conv_type} - {time_part}"
                        
                        with st.sidebar.expander(expander_title, expanded=False):
                            # Display query (truncated)
                            query_text = conv.get('query', 'No query')
                            st.write(f"**Q:** {query_text[:80]}{'...' if len(query_text) > 80 else ''}")
                            
                            # Display response (truncated)
                            response_text = conv.get('response', 'No response')
                            st.write(f"**A:** {response_text[:80]}{'...' if len(response_text) > 80 else ''}")
                            
                            # Display confidence if available
                            confidence = conv.get('confidence', 0)
                            if confidence > 0:
                                confidence_color = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.4 else "🔴"
                                st.write(f"**Confidence:** {confidence_color} {confidence:.2f}")
                            
                            # Display file type if available
                            file_type = conv.get('file_type')
                            if file_type and file_type != 'unknown':
                                st.write(f"**File Type:** {file_type}")
                    
                    except Exception as conv_error:
                        logger.error(f"Error displaying conversation {i}: {conv_error}")
                        continue
            else:
                st.sidebar.info(f"No conversations found on {selected_date}")
        else:
            st.sidebar.info("No conversation history available yet")
            st.sidebar.caption("Start asking questions to build your history!")
        
        # Usage statistics section
        try:
            if st.session_state.get('usage_tracker'):
                stats = st.session_state.usage_tracker.get_usage_stats(username)
                if stats and stats.get('queries', 0) > 0:
                    st.sidebar.markdown("---")
                    st.sidebar.markdown("### 📊 Your Usage Stats")
                    
                    col1, col2 = st.sidebar.columns(2)
                    with col1:
                        st.metric("Total Queries", stats.get('queries', 0))
                    with col2:
                        st.metric("Files Uploaded", stats.get('file_uploads', 0))
                    
                    st.metric("Login Sessions", stats.get('logins', 0))
        except Exception as stats_error:
            logger.error(f"Error loading usage stats: {stats_error}")
            
    except Exception as e:
        logger.error(f"Critical error in conversation history sidebar: {e}")
        st.sidebar.error("Error loading conversation history")

def display_user_info_sidebar():
    """Display user info and logout in sidebar - FIXED"""
    
    # Check if user is authenticated and components are available
    if (st.session_state.get('authenticated', False) and 
        st.session_state.get('username') and
        st.session_state.get('conv_manager')):
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **Logged in as:** {st.session_state.username}")
        
        if st.sidebar.button("🚪 Logout"):
            # Clear authentication
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.show_login = True
            
            # Clear any sensitive data
            st.session_state.current_df = None
            st.session_state.current_pdf_content = None
            st.session_state.current_word_content = None
            
            st.rerun()

def display_document_feedback_system(query, response_msg, unique_suffix):
    """Feedback system specifically for document Q&A - FIXED"""
    
    # Check if feedback was already given (using session state to track)
    feedback_key = f"feedback_given_{unique_suffix}"
    if st.session_state.get(feedback_key, False):
        st.caption("✅ Feedback already recorded")
        return
    
    st.markdown("**Was this response helpful?**")
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("👍", key=f"doc_thumbs_up_{unique_suffix}", help="Good response"):
            if save_document_feedback(query, response_msg, "thumbs_up"):
                st.session_state[feedback_key] = True  # Mark as feedback given
                st.success("Thank you for your feedback! 👍")
                st.rerun()
    
    with col2:
        if st.button("👎", key=f"doc_thumbs_down_{unique_suffix}", help="Poor response"):
            if save_document_feedback(query, response_msg, "thumbs_down"):
                st.session_state[feedback_key] = True  # Mark as feedback given
                st.success("Thank you for your feedback! We'll improve. 👎")
                st.rerun()
    
    with col3:
        st.caption("Please rate this response")

def save_document_feedback(query, response_msg, feedback_type):
    """Save user feedback for document Q&A - IMPROVED"""
    
    try:
        if (not st.session_state.get('authenticated') or 
            not st.session_state.get('username') or 
            not st.session_state.get('conv_manager')):
            logger.warning("Cannot save document feedback - user not authenticated")
            return False
        
        username = st.session_state.username
        conv_manager = st.session_state.conv_manager
        
        # Load conversations to find the most recent one matching this query
        conv_data = conv_manager.load_user_conversations(username)
        
        # Find the most recent conversation with this query (search from end)
        target_conversation = None
        for conversation in reversed(conv_data["conversations"]):
            if conversation.get("query", "").strip() == query.strip():
                target_conversation = conversation
                break
        
        if not target_conversation:
            logger.warning(f"⚠️ No matching conversation found for feedback: {query[:50]}...")
            return False
        
        # Check if feedback already exists for this specific conversation
        if target_conversation.get("feedback") == feedback_type:
            logger.info(f"ℹ️ Feedback already exists: {feedback_type} for conversation {target_conversation.get('id')}")
            return True  # Already saved, treat as success
        
        # Update this conversation with feedback
        success = conv_manager.update_conversation_feedback(
            username, 
            target_conversation["id"], 
            feedback_type
        )
        
        if success:
            logger.info(f"✅ Document feedback saved: {feedback_type} for conversation {target_conversation.get('id')}")
        else:
            logger.error(f"❌ Failed to save document feedback for conversation {target_conversation.get('id')}")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Failed to save document feedback: {e}")
        return False

def check_document_feedback(query):
    """Check if feedback already exists for this document query - ENHANCED"""
    
    try:
        if (not st.session_state.get('authenticated') or 
            not st.session_state.get('username') or 
            not st.session_state.get('conv_manager')):
            return None
        
        username = st.session_state.username
        conv_manager = st.session_state.conv_manager
        
        # Load conversations
        conv_data = conv_manager.load_user_conversations(username)
        
        # Find the most recent conversation with this query
        for conversation in reversed(conv_data["conversations"]):
            if conversation.get("query", "").strip() == query.strip():
                feedback = conversation.get("feedback")
                if feedback:
                    return feedback  # Return the actual feedback value
                break
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Failed to check existing document feedback: {e}")
        return None

def display_feedback_system(query, results):
    """Alias for document feedback system to use in data analysis"""
    # Generate a unique suffix for data analysis queries
    query_hash = abs(hash(query)) % (10**8)
    unique_suffix = f"data_analysis_{query_hash}"
    
    # Reuse the existing document feedback system
    display_document_feedback_system(query, results, unique_suffix) 

################################################################################################################################
# ============================================================================
# 10. 🏠 MAIN APPLICATION PAGES
# ============================================================================

def display_data_analysis_page(df, quality_report=None):
    """Simplified data analysis page for interactive tabular mode"""
    
    # Data quality report (optional)
    if quality_report:
        display_data_quality_report(quality_report)
        st.markdown("---")
    
    # Data preview
    st.subheader("👀 Data Preview")
    preview_rows = st.slider("Rows to preview:", 5, 50, 10)
    st.dataframe(df.head(preview_rows), use_container_width=True)
    
    st.markdown("---")
    
    # Simple query interface
    st.subheader("🤖 Basic Data Queries")
    
    query = st.text_input(
        "Ask a simple question about your data:",
        placeholder="e.g., 'how many rows' or 'what columns do we have'",
        help="Basic queries about data structure and simple statistics"
    )
    
    if query:
        # Check if this query was already processed to prevent duplicates
        if 'last_processed_query' not in st.session_state:
            st.session_state.last_processed_query = None
        
        # Only process if it's a different query
        if st.session_state.last_processed_query != query:
            with st.spinner("🔄 Processing query..."):
                # Process query with simplified function
                results = process_enhanced_query(df, query)
                
                # Mark this query as processed
                st.session_state.last_processed_query = query
                st.session_state.last_query_results = results
        else:
            # Use cached results
            results = st.session_state.get('last_query_results', {})
        
        # Display results
        if 'answer' in results:
            confidence = results.get('confidence', 0.0)
            if confidence > 0.7:
                st.success(f"**Answer:** {results['answer']}")
            elif confidence > 0.4:
                st.info(f"**Answer:** {results['answer']}")
            else:
                st.warning(f"**Answer:** {results['answer']} (Low confidence)")
            
            # Show feedback system
            display_feedback_system(query, results)
    
    st.markdown("---")
    
    # Basic data info
    st.subheader("📊 Dataset Information")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
        st.metric("Numeric Columns", numeric_cols)
    with col4:
        categorical_cols = len(df.select_dtypes(include=['object', 'category']).columns)
        st.metric("Text Columns", categorical_cols)
    
    # Column information
    with st.expander("📋 Column Details"):
        col_info = []
        for col in df.columns:
            col_info.append({
                'Column': col,
                'Type': str(df[col].dtype),
                'Non-Null Count': f"{df[col].count():,}",
                'Null Count': f"{df[col].isnull().sum():,}"
            })
        st.dataframe(pd.DataFrame(col_info), use_container_width=True)
    
    # Quick stats for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        with st.expander("🔢 Numeric Column Statistics"):
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)

def display_welcome_page():
    """Welcome page with instructions + bottom chat for generic Ollama convo"""

    # 1) Existing two-column welcome content
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

    st.markdown("---")

    # 2) Generic chat area (always visible on Welcome page)
    st.subheader("💬 Chat with your Documents")
    st.caption("Tip: No data loaded yet — upload/integrate to get document-aware answers. You can still chat generically below.")

    # Init chat state
    if "generic_chat_history" not in st.session_state:
        st.session_state.generic_chat_history = []

    if "generic_chat_system" not in st.session_state:
        st.session_state.generic_chat_system = [
            {"role": "system", "content": "You are a helpful AI data analyst. Keep answers concise unless asked for depth."}
        ]

    # 👉 FIXED: Get username properly with validation
    def get_current_username():
        """Safely get the current logged-in username"""
        # Try primary username storage
        username = st.session_state.get('username')
        if username and username.strip():
            return username.strip()
        
        # Try backup storage
        current_user = st.session_state.get('current_user')
        if current_user and current_user.strip():
            return current_user.strip()
        
        # If authenticated but no username found, there's an issue
        if st.session_state.get('authenticated', False):
            st.error("⚠️ Username not found in session. Please log in again.")
            return "User"  # Fallback
        
        return "Guest"  # Should not happen if authentication is working
    
    username = get_current_username()
    
    # 👉 Seed the very first assistant message once
    if not st.session_state.get("welcome_seeded", False):
        first_ai = (
            f"👋 Welcome, **{username}**! "
            "I'm your AI Data Assistant. Upload or integrate your data to start analyzing, "
            "or feel free to ask me general questions about data science and analytics."
        )
        st.session_state.generic_chat_history.append({"role": "assistant", "content": first_ai})
        st.session_state.welcome_seeded = True

    # 👉 IMPORTANT: Reset welcome message if username changes
    elif st.session_state.generic_chat_history and len(st.session_state.generic_chat_history) > 0:
        # Check if the first message needs updating with correct username
        first_msg = st.session_state.generic_chat_history[0]
        if first_msg["role"] == "assistant" and "Welcome," in first_msg["content"]:
            # Update the welcome message with correct username
            updated_welcome = (
                f"👋 Welcome, **{username}**! "
                "I'm your AI Data Assistant. Upload or integrate your data to start analyzing, "
                "or feel free to ask me general questions about data science and analytics."
            )
            st.session_state.generic_chat_history[0]["content"] = updated_welcome

    # Render previous messages (will include the seeded welcome as the first AI reply)
    for msg in st.session_state.generic_chat_history:
        st.chat_message("user" if msg["role"] == "user" else "assistant").write(msg["content"])

    # Bottom chat input
    user_input = st.chat_input("Type a message…")
    if user_input:
        # Show user msg
        st.session_state.generic_chat_history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Call Ollama -> llama3.2 with a Thinking spinner
        ai_reply = None
        try:
            from ollama import Client
            client = Client()

            # Build message list (system + history)
            messages = st.session_state.generic_chat_system + st.session_state.generic_chat_history

            with st.spinner("🤖 Thinking..."):
                resp = client.chat(model="llama3.2", messages=messages)
                ai_reply = resp["message"]["content"]
        except Exception as e:
            ai_reply = f"⚠️ Ollama error: {e}"

        # Show assistant msg
        st.session_state.generic_chat_history.append({"role": "assistant", "content": ai_reply})
        st.chat_message("assistant").write(ai_reply)

# Alternative: Reset welcome message function
def reset_welcome_message():
    """Call this function when user logs in to reset the welcome message"""
    if "welcome_seeded" in st.session_state:
        st.session_state.welcome_seeded = False
    if "generic_chat_history" in st.session_state:
        st.session_state.generic_chat_history = []

#########################################################################################################
# ============================================================================
# 11. 🔧 MAIN APPLICATION
# ============================================================================
###################### Modified on 20-08-2025 ##########################
def display_unified_chat_interface(content_data, file_type, filename=None):
    """Unified chat interface for all file types with plotting capabilities"""
    
    st.markdown("### 💬 Chat with your Data/Documents")
    
    # Initialize unified chat history
    chat_key = f'unified_chat_history_{file_type}'
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    # Clear button
    col_clear, col_info = st.columns([1, 4])
    with col_clear:
        if st.button("🗑️ Clear Chat", key=f"clear_{file_type}_chat"):
            st.session_state[chat_key] = []
            st.rerun()
    
    with col_info:
        if st.session_state[chat_key]:
            st.caption(f"💬 {len(st.session_state[chat_key])//2} questions asked")
    
    # Render chat history
    for i, msg in enumerate(st.session_state[chat_key]):
        if msg['role'] == 'user':
            with st.chat_message("user"):
                st.markdown(msg['message'])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg['message'])
                
                # Show plot if exists
                if 'plot' in msg:
                    st.plotly_chart(msg['plot'], use_container_width=True)
                
                # Confidence indicator
                if 'confidence' in msg:
                    confidence = msg['confidence']
                    if confidence > 0.7:
                        st.caption("🟢 High confidence")
                    elif confidence > 0.4:
                        st.caption("🟡 Medium confidence")
                    else:
                        st.caption("🔴 Low confidence")
                
                # Feedback system
                if 'query' in msg:
                    display_document_feedback_system(msg['query'], msg, f"{file_type}_{i}")
    
    # Generate smart suggestions based on file type
    suggestions = _generate_smart_suggestions(content_data, file_type)
    
    if suggestions:
        with st.expander("💡 Try a suggested question", expanded=len(st.session_state[chat_key]) == 0):
            cols = st.columns(2)
            for i, q in enumerate(suggestions[:4]):
                button_key = f"{file_type}_sugg_{i}_{len(st.session_state[chat_key])}"
                if cols[i % 2].button(q, key=button_key, use_container_width=True):
                    _process_unified_question(q, content_data, file_type, chat_key)
                    st.rerun()
    
    # Chat input
    # Chat input
    if prompt := st.chat_input(f"Ask about your {file_type} data/document, or request plots..."):
        # Add user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state[chat_key].append({'role': 'user', 'message': prompt.strip()})
        
        # Process and respond
        with st.chat_message("assistant"):
            with st.spinner("🤖 Processing..."):
                response_data = _process_unified_question(prompt.strip(), content_data, file_type, chat_key, show_in_chat=False)
                
                # Show response
                st.markdown(response_data['message'])
                
                # Show plot if generated
                if 'plot' in response_data:
                    st.plotly_chart(response_data['plot'], use_container_width=True)
                
                # Show confidence
                if 'confidence' in response_data:
                    confidence = response_data['confidence']
                    if confidence > 0.7:
                        st.caption("🟢 High confidence")
                    elif confidence > 0.4:
                        st.caption("🟡 Medium confidence")
                    else:
                        st.caption("🔴 Low confidence")
                
                # Add assistant response to chat history
                st.session_state[chat_key].append({
                    'role': 'assistant', 
                    'message': response_data['message'],
                    'confidence': response_data.get('confidence', 0.0),
                    'query': prompt.strip()
                })
                
                # Add feedback system
                display_document_feedback_system(prompt.strip(), response_data, f"{file_type}_new_{len(st.session_state[chat_key])}")

def _generate_smart_suggestions(content_data, file_type):
    """Generate suggestions based on content type"""
    if file_type == 'csv_qa' and 'dataframe' in content_data:
        df = content_data['dataframe']
        suggestions = [
            "What does this dataset contain?",
            "Show me a summary of the data",
            "Create a visualization of the main trends"
        ]
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            suggestions.append(f"Plot {numeric_cols[0]} distribution")
        
        return suggestions
    
    elif file_type in ['pdf', 'word']:
        return [
            "What is the main topic?",
            "Summarize key findings",
            "What data is in the tables?",
            "Show me important statistics"
        ]
    
    elif file_type == 'knowledge_base':
        return [
            "What are the main topics across all documents?",
            "Summarize key findings from all files",
            "What data is available in the tables?",
            "Compare information between documents"
        ]
    
    return []

def _process_unified_question(question, content_data, file_type, chat_key, show_in_chat=True):
    """Process question with plotting capability - FIXED with None checks"""
    
    # Initialize with safe defaults
    response_data = {'message': 'Processing...', 'confidence': 0.0, 'query': ''}
    
    try:
        # Validate inputs
        if not question:
            question = "No question provided"
        
        question = str(question).strip() if question else "No question provided"
        
        # Check if it's a plotting request
        plot_keywords = ['plot', 'chart', 'graph', 'visualize', 'show trend', 'histogram', 'scatter']
        is_plot_request = any(keyword in question.lower() for keyword in plot_keywords)
        
        if file_type == 'csv_qa' and content_data and 'dataframe' in content_data and is_plot_request:
            # Handle plotting for CSV data
            df = content_data['dataframe']
            plot_fig = _generate_plot_from_query(question, df)
            
            if plot_fig:
                response_data = {
                    'message': "Here's the visualization based on your request:",
                    'plot': plot_fig,
                    'confidence': 0.9,
                    'query': question
                }
            else:
                response_data = {
                    'message': "I couldn't generate a plot from your request. Please be more specific about which columns to visualize.",
                    'confidence': 0.3,
                    'query': question
                }
        elif file_type == 'knowledge_base':
            # Handle knowledge base questions
            answer_result = _process_knowledge_base_question(question, content_data)
            response_data = {
                'message': answer_result.get('answer', 'No answer available'),
                'confidence': answer_result.get('confidence', 0.0),
                'query': question
            }
        else:
            # Use existing Q&A agents
            answer_result = None
            
            if file_type == 'csv_qa' and content_data and 'agent' in content_data:
                answer_result = content_data['agent'].answer_question(question, content_data)
            elif file_type == 'pdf' and 'pdf_agent' in st.session_state:
                answer_result = st.session_state.pdf_agent.answer_question(question, content_data)
            elif file_type == 'word' and 'word_agent' in st.session_state:
                answer_result = st.session_state.word_agent.answer_question(question, content_data)
            else:
                answer_result = {'answer': 'Agent not available', 'confidence': 0.0}
            
            # Safely extract answer
            answer = answer_result.get('answer', 'No answer available') if answer_result else 'No answer available'
            confidence = answer_result.get('confidence', 0.0) if answer_result else 0.0
            
            response_data = {
                'message': str(answer) if answer else 'No answer available',
                'confidence': float(confidence) if confidence else 0.0,
                'query': question
            }
        
        # Add to chat history if requested
        if show_in_chat and chat_key in st.session_state:
            st.session_state[chat_key].append(response_data)
        
        # Save conversation safely
        try:
            if (st.session_state.get('authenticated') and 
                st.session_state.get('username') and 
                st.session_state.get('conv_manager')):
                
                safe_message = str(response_data.get('message', ''))[:1000]  # Limit length
                safe_confidence = float(response_data.get('confidence', 0.0))
                
                st.session_state.conv_manager.save_conversation(
                    username=st.session_state.username,
                    conversation_type=f'{file_type}_unified',
                    query=question,
                    response=safe_message,
                    confidence=safe_confidence,
                    file_type=file_type
                )
        except Exception as save_error:
            logger.error(f"Failed to save conversation: {save_error}")
    
    except Exception as e:
        logger.error(f"Error in _process_unified_question: {e}")
        response_data = {
            'message': f"Error processing question: {str(e)}",
            'confidence': 0.0,
            'query': str(question) if question else 'Unknown question'
        }
        
        if show_in_chat and chat_key in st.session_state:
            st.session_state[chat_key].append(response_data)
    
    return response_data

# def _generate_plot_from_query(query, df):
#     """AI-powered plot generation using Ollama to interpret requests dynamically"""
    
#     try:
#         # Get basic info about the dataset
#         numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
#         categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
#         all_cols = df.columns.tolist()
        
#         # Create a data summary for Ollama
#         data_summary = f"""
# Dataset Overview:
# - Total rows: {len(df):,}
# - Numeric columns: {', '.join(numeric_cols) if numeric_cols else 'None'}
# - Categorical columns: {', '.join(categorical_cols) if categorical_cols else 'None'}
# - All columns: {', '.join(all_cols)}

# Sample data (first 3 rows):
# {df.head(3).to_string()}
#         """
        
#         # Use Ollama to determine the best plot type and parameters
#         if AI_MODELS.get('ollama') and AI_MODELS.get('ollama_model'):
#             plot_instruction = _get_plot_instruction_from_ollama(query, data_summary)
            
#             if plot_instruction:
#                 return _execute_plot_instruction(plot_instruction, df)
        
#         # Fallback to simple heuristics if Ollama fails
#         return _fallback_plot_generation(query, df)
        
#     except Exception as e:
#         logger.error(f"AI-powered plot generation failed: {e}")
#         return _fallback_plot_generation(query, df)

# def _get_plot_instruction_from_ollama(query, data_summary):
#     """Use Ollama to interpret the plot request and return structured instructions"""
    
#     prompt = f"""Based on the user's request and dataset information, determine the best way to create a visualization.

# DATASET INFORMATION:
# {data_summary}

# USER REQUEST: {query}

# Analyze the request and respond with a JSON object containing plot instructions. Use this exact format:

# {{
#     "plot_type": "histogram|bar|scatter|line|box|pie",
#     "x_column": "column_name_or_null",
#     "y_column": "column_name_or_null", 
#     "title": "Chart Title",
#     "reasoning": "Brief explanation of why this plot was chosen"
# }}

# Rules:
# - Use ONLY column names that exist in the dataset
# - For "unique" requests, use bar plots with value counts
# - For distribution requests, use histograms for numeric data
# - For comparisons, use bar or box plots
# - If request is unclear, choose the most meaningful visualization
# - Return ONLY the JSON object, no other text

# JSON Response:"""

#     try:
#         response = AI_MODELS['ollama'].generate(
#             model=AI_MODELS['ollama_model'],
#             prompt=prompt,
#             options={
#                 "temperature": 0.3,
#                 "top_p": 0.9,
#                 "num_predict": 200
#             }
#         )
        
#         # Parse the JSON response
#         import json
#         plot_instruction = json.loads(response['response'].strip())
#         return plot_instruction
        
#     except Exception as e:
#         logger.error(f"Ollama plot instruction failed: {e}")
#         return None

# def _execute_plot_instruction(instruction, df):
#     """Execute the plot instruction returned by Ollama"""
    
#     try:
#         plot_type = instruction.get('plot_type', '').lower()
#         x_col = instruction.get('x_column')
#         y_col = instruction.get('y_column')
#         title = instruction.get('title', 'Data Visualization')
        
#         # Validate columns exist
#         if x_col and x_col not in df.columns:
#             x_col = None
#         if y_col and y_col not in df.columns:
#             y_col = None
        
#         # Generate the appropriate plot
#         if plot_type == 'histogram' and x_col:
#             fig = px.histogram(df, x=x_col, title=title)
            
#         elif plot_type == 'bar' and x_col:
#             if df[x_col].dtype in ['object', 'category']:
#                 # For categorical data, show value counts
#                 value_counts = df[x_col].value_counts().head(20)
#                 fig = px.bar(
#                     x=value_counts.index, 
#                     y=value_counts.values, 
#                     title=title,
#                     labels={'x': x_col, 'y': 'Count'}
#                 )
#                 fig.update_xaxis(tickangle=45)
#             else:
#                 fig = px.histogram(df, x=x_col, title=title)
                
#         elif plot_type == 'scatter' and x_col and y_col:
#             fig = px.scatter(df, x=x_col, y=y_col, title=title)
            
#         elif plot_type == 'box' and x_col and y_col:
#             fig = px.box(df, x=x_col, y=y_col, title=title)
#             fig.update_xaxis(tickangle=45)
            
#         elif plot_type == 'line' and x_col and y_col:
#             fig = px.line(df, x=x_col, y=y_col, title=title)
            
#         elif plot_type == 'pie' and x_col:
#             value_counts = df[x_col].value_counts().head(10)
#             fig = px.pie(
#                 values=value_counts.values, 
#                 names=value_counts.index, 
#                 title=title
#             )
            
#         else:
#             return None
            
#         return fig
        
#     except Exception as e:
#         logger.error(f"Plot execution failed: {e}")
#         return None

# def _fallback_plot_generation(query, df):
#     """Simple fallback plot generation if AI approach fails"""
    
#     query_lower = query.lower()
#     numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
#     categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
#     # Basic keyword matching
#     if 'unique' in query_lower or 'count' in query_lower:
#         if categorical_cols:
#             col = categorical_cols[0]
#             value_counts = df[col].value_counts().head(15)
#             fig = px.bar(
#                 x=value_counts.index, 
#                 y=value_counts.values,
#                 title=f'Count of {col.replace("_", " ").title()}'
#             )
#             fig.update_xaxis(tickangle=45)
#             return fig
    
#     elif 'distribution' in query_lower or 'histogram' in query_lower:
#         if numeric_cols:
#             col = numeric_cols[0]
#             fig = px.histogram(df, x=col, title=f'Distribution of {col}')
#             return fig
    
#     # Default: most meaningful plot
#     if numeric_cols and categorical_cols:
#         fig = px.box(df, x=categorical_cols[0], y=numeric_cols[0])
#         fig.update_xaxis(tickangle=45)
#         return fig
#     elif categorical_cols:
#         col = categorical_cols[0]
#         value_counts = df[col].value_counts().head(10)
#         fig = px.bar(x=value_counts.index, y=value_counts.values)
#         fig.update_xaxis(tickangle=45)
#         return fig
    
#     return None

def _process_knowledge_base_question(question, combined_content):
    """Process questions against the entire knowledge base - IMPROVED"""
    
    try:
        # Validate inputs
        if not question:
            return {
                'answer': "No question was provided.",
                'confidence': 0.1
            }
        
        if not combined_content:
            return {
                'answer': "No knowledge base content available.",
                'confidence': 0.1
            }
        
        question = str(question).strip()
        question_lower = question.lower()
        question_words = set(re.findall(r'\b\w+\b', question_lower))
        
        relevant_chunks = []
        
        # Score chunks from all files
        for chunk in combined_content.get('chunks', []):
            content_lower = chunk['content'].lower()
            content_words = set(re.findall(r'\b\w+\b', content_lower))
            
            overlap = len(question_words.intersection(content_words))
            if overlap > 0:
                similarity = overlap / len(question_words)
                if similarity > 0.1:
                    chunk_with_score = chunk.copy()
                    chunk_with_score['relevance_score'] = similarity
                    relevant_chunks.append(chunk_with_score)
        
        # ENHANCED: Also search in individual file data
        if 'knowledge_base' in st.session_state and 'files' in st.session_state.knowledge_base:
            for filename, file_content in st.session_state.knowledge_base['files'].items():
                # Check if question mentions this filename
                filename_lower = filename.lower()
                if any(word in filename_lower for word in question_words):
                    # Add filename-specific context
                    file_info = {
                        'id': len(relevant_chunks),
                        'content': f"File: {filename}\nType: {file_content.get('file_type', 'unknown')}\nStatus: {file_content.get('status', 'unknown')}",
                        'source_file': filename,
                        'relevance_score': 0.8,
                        'type': 'file_info'
                    }
                    relevant_chunks.append(file_info)
                    
                    # If it's CSV data, add data summary
                    if file_content.get('file_type') == 'csv_qa' and 'data_summary' in file_content:
                        data_summary = file_content['data_summary']
                        if 'basic_info' in data_summary:
                            summary_text = f"CSV Data: {filename}\n"
                            summary_text += f"Rows: {data_summary['basic_info'].get('rows', 0)}\n"
                            summary_text += f"Columns: {', '.join(data_summary['basic_info'].get('column_names', []))}"
                            
                            csv_info = {
                                'id': len(relevant_chunks),
                                'content': summary_text,
                                'source_file': filename,
                                'relevance_score': 0.9,
                                'type': 'csv_summary'
                            }
                            relevant_chunks.append(csv_info)
        
        # Sort by relevance
        relevant_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        if not relevant_chunks:
            return {
                'answer': "I couldn't find relevant information in the knowledge base for your question.",
                'confidence': 0.2
            }
        
        # Build context from top relevant chunks
        context_parts = []
        for chunk in relevant_chunks[:7]:  # Top 7 chunks
            source_file = chunk.get('source_file', 'Unknown')
            content = chunk['content']
            context_parts.append(f"[From {source_file}] {content}")
        
        context = "\n\n".join(context_parts)
        
        # Use Ollama if available
        if AI_MODELS.get('ollama') and AI_MODELS.get('ollama_model'):
            try:
                prompt = f"""Based on the following information from multiple documents, answer the user's question accurately and concisely.

DOCUMENT INFORMATION:
{context}

USER QUESTION: {question}

Instructions:
- Answer based only on the provided information
- Cite which documents/files the information comes from when possible
- If the answer spans multiple documents, mention that
- If you find file names or data references, include them
- Keep the answer concise but complete

ANSWER:"""

                response = AI_MODELS['ollama'].generate(
                    model=AI_MODELS['ollama_model'],
                    prompt=prompt,
                    options={"temperature": 0.5, "top_p": 0.95, "num_predict": 600}
                )
                
                answer_text = response['response'].strip()
                confidence = 0.8 if len(relevant_chunks) > 2 else 0.6
                
                return {
                    'answer': answer_text,
                    'confidence': confidence
                }
                
            except Exception as e:
                logger.error(f"Ollama failed for knowledge base: {e}")
        
        # Fallback response
        sources = list(set(chunk.get('source_file', 'Unknown') for chunk in relevant_chunks[:3]))
        answer = f"Based on the information from {', '.join(sources)}, I found relevant content but need Ollama to provide a complete answer. Found {len(relevant_chunks)} relevant pieces of information."
        
        return {
            'answer': answer,
            'confidence': 0.4
        }
        
    except Exception as e:
        logger.error(f"Knowledge base question processing failed: {e}")
        return {
            'answer': f"Error processing question: {str(e)}",
            'confidence': 0.1
        }

def find_file_by_partial_name(partial_name, knowledge_base_files):
    """Find files that match a partial name (case insensitive)"""
    partial_lower = partial_name.lower()
    matches = []
    
    for filename in knowledge_base_files.keys():
        filename_lower = filename.lower()
        # Remove common suffixes and check for matches
        clean_filename = filename_lower.replace('.pdf', '').replace('.csv', '').replace('.xlsx', '').replace('.docx', '')
        
        if partial_lower in clean_filename or clean_filename in partial_lower:
            matches.append(filename)
    
    return matches
    
def combine_knowledge_base():
    """Combine all processed files into a unified knowledge base"""
    if not st.session_state.knowledge_base['files']:
        return None
    
    combined = {
        'text_content': '',
        'tables': [],
        'chunks': [],
        'searchable_content': {'keywords': set(), 'text_chunks': []},
        'files_info': []
    }
    
    for filename, content in st.session_state.knowledge_base['files'].items():
        if content.get('status') == 'success':
            # Combine text content
            if content.get('text_content'):
                combined['text_content'] += f"\n=== FILE: {filename} ===\n{content['text_content']}\n"
            
            # Combine tables
            if content.get('tables'):
                for table in content['tables']:
                    table['source_file'] = filename
                    combined['tables'].append(table)
            
            # Combine chunks
            if content.get('chunks'):
                for chunk in content['chunks']:
                    chunk['source_file'] = filename
                    chunk['id'] = len(combined['chunks'])
                    combined['chunks'].append(chunk)
            
            # Track file info
            combined['files_info'].append({
                'filename': filename,
                'type': content.get('file_type', 'unknown'),
                'chunks': len(content.get('chunks', [])),
                'tables': len(content.get('tables', []))
            })
    
    combined['searchable_content']['keywords'] = list(combined['searchable_content']['keywords'])
    combined['status'] = 'success'
    return combined

def main():
    initialize_session_state()
    check_concurrent_user_support()
    
    # Check authentication first
    if not st.session_state.authenticated:
        display_authentication()
        return
    
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
        <h1 style="color: white; margin: 0;">🤖 AI Data NooB </h1>
        <p style="color: white; margin: 0;">Plug & Play Analytics with AI Agents</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Sidebar Navigation --- 
    with st.sidebar:
        display_user_info_sidebar()
        page = st.selectbox("Choose a page:", ["📊 Data Analysis"])
        data_source = st.radio("Data Source:", ["Upload File", "Connect to Database"] if DATABASE_AVAILABLE else ["Upload File"])
        display_conversation_history_sidebar()

        # Model status
        if AI_MODELS['embed_available']:
            st.success("✅ Embeddings: Ready")
        else:
            st.error("❌ Embeddings: Not Available")

        if AI_MODELS['ollama_available']:
            st.success(f"✅ SLM: {AI_MODELS.get('ollama_model', 'Connected')}")
        else:
            st.warning("⚠️ SLM: Disconnected")

        st.markdown("---")

    # --- Upload File Block ---
    if data_source == "Upload File":
        # Show available formats
        available_formats = ["CSV", "Excel (.xlsx, .xls)"]
        if PDF_PROCESSING_AVAILABLE:
            available_formats.append("PDF")
        if WORD_PROCESSING_AVAILABLE:
            available_formats.append("Word (.docx, .doc)")
        
        st.info(f"📋 Supported formats: {', '.join(available_formats)}")

        # Multiple file uploader
        uploaded_files = st.file_uploader(
            "Choose your files (multiple files supported)",
            accept_multiple_files=True,
            help=f"Supported: {', '.join(available_formats)} | Max size: 200MB per file"
        )

        # Initialize knowledge base in session state
        if 'knowledge_base' not in st.session_state:
            st.session_state.knowledge_base = {
                'files': {},
                'combined_content': None
            }

        if uploaded_files:
            # Show summary of all files
            st.info(f"Processing {len(uploaded_files)} file(s)")
            
            # Process each file
            processed_count = 0
            for file_idx, uploaded_file in enumerate(uploaded_files):
                #st.markdown(f"### Processing file {file_idx + 1}: {uploaded_file.name}")
                
                # Manual file type detection for each file
                file_name = uploaded_file.name.lower()
                file_extension = file_name.split('.')[-1] if '.' in file_name else ''
                
                # Show file info
                file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📁 File", uploaded_file.name)
                with col2:
                    st.metric("📊 Size", f"{file_size_mb:.1f} MB")
                with col3:
                    st.metric("🔖 Extension", f".{file_extension}")
                
                # Validate file size
                if file_size_mb > 200:
                    st.error(f"❌ File {uploaded_file.name} too large! Maximum size is 200MB.")
                    continue
                
                # Process based on file extension
                with st.spinner(f"🔄 Processing {file_extension.upper()} file: {uploaded_file.name}..."):
                    try:
                        success = False
                        
                        # PDF Processing
                        if file_extension == "pdf" and PDF_PROCESSING_AVAILABLE:
                            pdf_content = extract_comprehensive_pdf_content(uploaded_file)
                            if pdf_content and pdf_content['status'] == 'success':
                                st.session_state.knowledge_base['files'][uploaded_file.name] = pdf_content
                                st.session_state.knowledge_base['files'][uploaded_file.name]['file_type'] = 'pdf'
                                # Store agents for individual access
                                if 'pdf_agent' in st.session_state:
                                    st.session_state.knowledge_base['files'][uploaded_file.name]['agent'] = st.session_state['pdf_agent']
                                success = True

                        # Word Processing
                        elif file_extension in ["docx", "doc"] and WORD_PROCESSING_AVAILABLE:
                            word_content = extract_comprehensive_word_content(uploaded_file)
                            if word_content and word_content['status'] == 'success':
                                st.session_state.knowledge_base['files'][uploaded_file.name] = word_content
                                st.session_state.knowledge_base['files'][uploaded_file.name]['file_type'] = 'word'
                                # Store agents for individual access
                                if 'word_agent' in st.session_state:
                                    st.session_state.knowledge_base['files'][uploaded_file.name]['agent'] = st.session_state['word_agent']
                                success = True
                        
                        # CSV/Excel Processing
                        elif file_extension in ["csv", "xlsx", "xls"]:
                            df = load_and_validate_data(uploaded_file)
                            if df is not None:
                                # Initialize CSV processor
                                csv_agent = AdvancedCSVProcessor(
                                    ollama_client=AI_MODELS.get('ollama'),
                                    ollama_model=AI_MODELS.get('ollama_model', 'llama3.2')
                                )
                                
                                # Process CSV for Q&A
                                csv_content = csv_agent.process_csv_fast(df, uploaded_file.name)
                                
                                if csv_content and csv_content['status'] == 'success':
                                    csv_content['dataframe'] = df  # Add dataframe to content
                                    st.session_state.knowledge_base['files'][uploaded_file.name] = csv_content
                                    st.session_state.knowledge_base['files'][uploaded_file.name]['file_type'] = 'csv_qa'
                                    st.session_state.knowledge_base['files'][uploaded_file.name]['agent'] = csv_agent
                                    success = True
                        
                        else:
                            st.error(f"❌ Unsupported file type: .{file_extension}")
                            continue
                        
                        if success:
                            processed_count += 1
                            #st.success(f"✅ {uploaded_file.name} processed successfully!")
                            
                            # Track upload
                            if st.session_state.get('authenticated') and st.session_state.get('username'):
                                track_file_upload(
                                    username=st.session_state.username,
                                    file_name=uploaded_file.name,
                                    file_type=file_extension,
                                    file_size_mb=file_size_mb
                                )
                        else:
                            st.error(f"❌ Failed to process {uploaded_file.name}")
                            
                    except Exception as e:
                        st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                        logger.error(f"File processing error for {uploaded_file.name}: {e}")
                
                #st.markdown("---")
            
            # Show knowledge base summary and unified interface
            if processed_count > 0:
                st.success(f"✅ Successfully processed {processed_count} out of {len(uploaded_files)} files")
                
                # Combine knowledge base
                combined_content = combine_knowledge_base()
                if combined_content:
                    st.session_state.current_knowledge_base = combined_content
                    st.session_state.file_type = 'knowledge_base'
                    
                    # Clear individual content states
                    st.session_state.current_df = None
                    st.session_state.current_pdf_content = None
                    st.session_state.current_word_content = None
                    st.session_state.current_csv_content = None
                    
                    # Show summary
                    st.markdown("### 📚 Knowledge Base Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Files", len(combined_content['files_info']))
                    with col2:
                        st.metric("Text Chunks", len(combined_content['chunks']))
                    with col3:
                        st.metric("Tables", len(combined_content['tables']))
                    with col4:
                        total_chars = len(combined_content['text_content'])
                        st.metric("Total Content", f"{total_chars:,} chars")
                    
                    # File breakdown
                    with st.expander("📋 File Breakdown"):
                        for file_info in combined_content['files_info']:
                            st.write(f"**{file_info['filename']}** ({file_info['type']}): {file_info['chunks']} chunks, {file_info['tables']} tables")
                    
                    # Display unified chat interface for knowledge base
                    display_unified_chat_interface(combined_content, 'knowledge_base', 'Knowledge Base')

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
    if (st.session_state.current_df is None and 
        st.session_state.current_pdf_content is None and 
        st.session_state.current_word_content is None and
        st.session_state.current_csv_content is None and
        st.session_state.get('current_knowledge_base') is None):
        display_welcome_page()
    elif page == "📊 Data Analysis":
        # Handle different file types
        if st.session_state.current_df is not None and st.session_state.file_type == 'tabular':
            # Traditional data analysis page for interactive mode only
            display_data_analysis_page(st.session_state.current_df)
        elif st.session_state.get('current_knowledge_base') and st.session_state.file_type == 'knowledge_base':
            # Knowledge base is already displayed in the upload section
            pass
# ============================================================================
# 12. 🚀 APPLICATION ENTRY POINT
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




