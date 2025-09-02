# import cv2
# import numpy as np
# import tempfile
# import os
# import concurrent.futures
# import yt_dlp
# from fer import FER
# from scipy.ndimage import gaussian_filter
# import uuid
# from pathlib import Path
# import urllib.request
# from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage

# def download_youtube_video(url, output_path=None):
#     """
#     Download a YouTube video using yt-dlp
    
#     Parameters:
#     - url: YouTube URL
#     - output_path: Directory to save the video (uses temp dir if None)
    
#     Returns:
#     - Dictionary with download status and info
#     """
#     try:
#         if not url:
#             return {
#                 "success": False,
#                 "error": "No URL provided"
#             }
            
#         # Create output directory if needed
#         if output_path is None:
#             output_path = tempfile.mkdtemp()
#         elif not os.path.exists(output_path):
#             os.makedirs(output_path)
            
#         # Create a random filename to avoid conflicts
#         random_filename = f"video_{uuid.uuid4().hex}.mp4"
#         output_file = os.path.join(output_path, random_filename)
        
#         # yt-dlp options
#         ydl_opts = {
#             'format': 'best[ext=mp4]',
#             'outtmpl': output_file,
#             'noplaylist': True,
#             'quiet': True,
#             'no_warnings': True,
#             'noprogress': True,
#         }
        
#         # Download info first to get metadata
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(url, download=False)
#             video_title = info.get('title', 'Unknown Title')
#             thumbnail_url = info.get('thumbnail', '')
            
#             # Now download the video
#             ydl.download([url])
        
#         # Make sure file exists
#         if not os.path.exists(output_file):
#             return {
#                 "success": False,
#                 "error": "Download completed but file not found"
#             }
            
#         return {
#             "success": True,
#             "video_path": output_file,
#             "title": video_title,
#             "thumbnail": thumbnail_url
#         }
        
#     except Exception as e:
#         return {
#             "success": False,
#             "error": f"Error downloading video: {str(e)}"
#         }

# def extract_frames(video_path, interval_secs=2):
#     frames = []
#     timestamps = []
    
#     try:
#         video = cv2.VideoCapture(video_path)
#         fps = video.get(cv2.CAP_PROP_FPS)
#         total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
#         duration = total_frames / fps
        
#         # Calculate frame indices to extract based on interval
#         frame_interval = int(fps * interval_secs)
#         frame_indices = list(range(0, total_frames, frame_interval))
        
#         for i in frame_indices:
#             video.set(cv2.CAP_PROP_POS_FRAMES, i)
#             ret, frame = video.read()
            
#             if ret:
#                 # Convert BGR to RGB
#                 rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 timestamp = i / fps  # Calculate timestamp in seconds
                
#                 frames.append(rgb_frame)
#                 timestamps.append(timestamp)
        
#         video.release()
        
#         return {
#             "success": True,
#             "frames": frames,
#             "timestamps": timestamps,
#             "total_duration": duration,
#             "total_frames": total_frames
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "error": str(e)
#         }

# def detect_blur(image, threshold=100):
#     # Convert to grayscale
#     if len(image.shape) == 3:
#         gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
#     else:
#         gray = image
    
#     # Calculate the Laplacian variance
#     lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
#     # Return blur score and whether image is blurry
#     return {
#         "blur_score": lap_var,
#         "is_blurry": lap_var < threshold
#     }

# def stabilize_image(image):
#     # Apply light Gaussian blur to reduce noise
#     stabilized = gaussian_filter(image, sigma=0.5)
#     return stabilized

# def enhance_image(image):
#     # Convert to LAB color space
#     lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    
#     # Split the LAB channels
#     l, a, b = cv2.split(lab)
    
#     # Apply CLAHE to L channel
#     clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
#     cl = clahe.apply(l)
    
#     # Merge the CLAHE enhanced L channel with original A and B channels
#     enhanced_lab = cv2.merge((cl, a, b))
    
#     # Convert back to RGB color space
#     enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
    
#     return enhanced_rgb

# def load_face_detector():
#     # Load pre-trained face detection model (Haar Cascade)
#     model_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
#     face_cascade = cv2.CascadeClassifier(model_path)
#     return face_cascade

# def detect_faces(image, face_cascade, min_confidence=0.5):
#     # Convert to grayscale for Haar cascade
#     gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
#     # Detect faces
#     # faces = face_cascade.detectMultiScale(
#     #     gray, 
#     #     scaleFactor=1.1, 
#     #     minNeighbors=5, 
#     #     minSize=(30, 30),
#     #     flags=cv2.CASCADE_SCALE_IMAGE
#     # )
#     faces = face_cascade.detectMultiScale(
#     gray, 
#     scaleFactor=1.05,  # Reduced from 1.1 (more sensitive)
#     minNeighbors=3,    # Reduced from 5
#     minSize=(20, 20),  # Smaller minimum face size
#     flags=cv2.CASCADE_SCALE_IMAGE
# )
    
#     # Calculate face locations and areas
#     face_locations = []
#     face_areas = []
    
#     for (x, y, w, h) in faces:
#         face_locations.append((y, x+w, y+h, x))  # Convert to (top, right, bottom, left) format
#         face_areas.append(w * h)
    
#     return face_locations, face_areas

# def format_time(seconds):
#     minutes, seconds = divmod(int(seconds), 60)
#     hours, minutes = divmod(minutes, 60)
#     if hours > 0:
#         return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
#     else:
#         return f"{minutes:02d}:{seconds:02d}"

# def process_frame(frame_data):
#     frame, timestamp, face_threshold, face_coverage, emotion_detector, selected_emotions, face_cascade = frame_data[:7]
#     include_emotions = frame_data[7] if len(frame_data) > 7 else True
#     blur_threshold = frame_data[8] if len(frame_data) > 8 else 100
#     enable_stabilization = frame_data[9] if len(frame_data) > 9 else False
    
#     # Stabilize image if enabled
#     if enable_stabilization:
#         frame = stabilize_image(frame)
    
#     # Check for blur
#     blur_result = detect_blur(frame, threshold=blur_threshold)
#     if blur_result["is_blurry"]:
#         return {
#             "success": False,
#             "is_blurry": True,
#             "blur_score": blur_result["blur_score"],
#             "timestamp": timestamp
#         }
    
#     # Detect faces using OpenCV
#     face_locations, face_areas = detect_faces(frame, face_cascade, min_confidence=face_threshold)
    
#     if not face_locations:
#         return {
#             "success": False,
#             "has_face": False,
#             "is_blurry": False,
#             "timestamp": timestamp,
#             "blur_score": blur_result["blur_score"]
#         }
    
#     # Calculate face coverage
#     frame_area = frame.shape[0] * frame.shape[1]
#     max_face_index = np.argmax(face_areas) if face_areas else -1
    
#     if max_face_index >= 0:
#         max_face_area = face_areas[max_face_index]
#         max_face_location = face_locations[max_face_index]
#         face_coverage_percent = (max_face_area / frame_area) * 100
#     else:
#         return {
#             "success": False,
#             "has_face": False,
#             "is_blurry": False,
#             "timestamp": timestamp,
#             "blur_score": blur_result["blur_score"]
#         }
    
#     # Check if face meets coverage criteria
#     if face_coverage_percent < face_coverage:
#         return {
#             "success": True,
#             "has_face": True,
#             "meets_coverage": False,
#             "is_blurry": False,
#             "face_coverage": face_coverage_percent,
#             "timestamp": timestamp,
#             "blur_score": blur_result["blur_score"]
#         }
    
#     # Skip emotion detection if not required
#     if not include_emotions:
#         return {
#             "success": True,
#             "has_face": True,
#             "meets_coverage": True,
#             "has_emotion": False,
#             "emotion_match": True,
#             "is_blurry": False,
#             "face_coverage": face_coverage_percent,
#             "frame": frame,
#             "timestamp": timestamp,
#             "blur_score": blur_result["blur_score"],
#             "face_location": max_face_location,
#             "dominant_emotion": "No emotion detection"
#         }
    
#     # Only perform emotion detection if include_emotions is True
#     bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
#     # Detect emotions
#     emotions_result = emotion_detector.detect_emotions(bgr_frame)
    
#     if not emotions_result:
#         return {
#             "success": True,
#             "has_face": True,
#             "meets_coverage": True,
#             "has_emotion": False,
#             "emotion_match": False,
#             "is_blurry": False,
#             "face_coverage": face_coverage_percent,
#             "frame": frame,
#             "timestamp": timestamp,
#             "blur_score": blur_result["blur_score"],
#             "face_location": max_face_location,
#             "dominant_emotion": "No emotions detected"
#         }
    
#     # Get dominant emotion
#     emotion_scores = emotions_result[0]["emotions"]
#     dominant_emotion = max(emotion_scores, key=emotion_scores.get)
    
#     # Check if emotion matches selected emotions
#     emotion_match = dominant_emotion.lower() in [e.lower() for e in selected_emotions]
    
#     return {
#         "success": True,
#         "has_face": True,
#         "meets_coverage": True,
#         "has_emotion": True,
#         "emotion_match": emotion_match,
#         "is_blurry": False,
#         "face_coverage": face_coverage_percent,
#         "dominant_emotion": dominant_emotion,
#         "emotion_scores": emotion_scores,
#         "frame": frame,
#         "timestamp": timestamp,
#         "blur_score": blur_result["blur_score"],
#         "face_location": max_face_location
#     }

# def prepare_frame_data(frames, timestamps, face_threshold, face_coverage, emotion_detector, 
#                      selected_emotions, face_cascade, include_emotions, blur_threshold, 
#                      enable_stabilization, enable_enhancement):
#     """Prepare data for parallel processing of frames"""
#     return [
#         (frame, timestamp, face_threshold, face_coverage, emotion_detector, selected_emotions, 
#          face_cascade, include_emotions, blur_threshold, enable_stabilization, enable_enhancement)
#         for frame, timestamp in zip(frames, timestamps)
#     ]

# def save_thumbnail_to_storage(frame, video_title, timestamp, emotion, save_dir="thumbnails", format="jpg"):
#     """Save thumbnail to Django's storage system"""
#     # Format timestamp for filename
#     timestamp_str = format_time(timestamp).replace(":", "_")
    
#     # Clean video title for filename
#     clean_title = "".join([c for c in video_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
#     clean_title = clean_title.replace(" ", "_")
    
#     # Create filename
#     filename = f"{clean_title}_{emotion}_{timestamp_str}.{format}"
#     filepath = os.path.join(save_dir, filename)
    
#     # Convert RGB to BGR for saving with OpenCV
#     frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
#     # Save to bytes
#     success, buffer = cv2.imencode(f".{format}", frame_bgr)
#     if not success:
#         return None
    
#     # Save to storage
#     thumbnail_file = ContentFile(buffer.tobytes(), name=filename)
#     saved_path = default_storage.save(filepath, thumbnail_file)
    
#     return {
#         "filename": filename,
#         "path": saved_path,
#         "url": default_storage.url(saved_path)
#     }

# def generate_thumbnails(youtube_url, params):
#     """
#     Main function to generate thumbnails from YouTube video
    
#     Parameters:
#     - youtube_url: URL of the YouTube video
#     - params: Dictionary of parameters for thumbnail generation
    
#     Returns:
#     - Dictionary with results
#     """
#     # Download video
#     download_result = download_youtube_video(youtube_url)
    
#     if not download_result["success"]:
#         return {
#             "success": False,
#             "error": download_result["error"]
#         }
    
#     video_path = download_result["video_path"]
#     video_title = download_result["title"]
#     video_thumbnail = download_result["thumbnail"]
    
#     # Extract frames
#     extraction_result = extract_frames(video_path, interval_secs=params.get("frame_interval", 2))
    
#     if not extraction_result["success"]:
#         return {
#             "success": False,
#             "error": extraction_result["error"]
#         }
    
#     frames = extraction_result["frames"]
#     timestamps = extraction_result["timestamps"]
    
#     # Initialize emotion detector
#     emotion_detector = FER(mtcnn=True)
    
#     # Load face detector
#     face_cascade = load_face_detector()
    
#     # Prepare data for parallel processing
#     frame_data = prepare_frame_data(
#         frames, 
#         timestamps, 
#         params.get("face_threshold", 0.5),
#         params.get("face_coverage", 20),
#         emotion_detector,
#         params.get("selected_emotions", []),
#         face_cascade,
#         params.get("include_emotions", True),
#         params.get("blur_threshold", 100),
#         params.get("enable_stabilization", True),
#         params.get("enable_enhancement", True)
#     )
    
#     # Process frames in parallel
#     thumbnails = []
#     processed_count = 0
#     total_frames = len(frames)
    
#     blur_count = 0
#     face_count = 0
#     emotion_count = 0
    
#     # Use ThreadPoolExecutor for parallel processing
#     with concurrent.futures.ThreadPoolExecutor(max_workers=params.get("max_workers", 4)) as executor:
#         future_to_frame = {executor.submit(process_frame, fd): idx for idx, fd in enumerate(frame_data)}
        
#         for future in concurrent.futures.as_completed(future_to_frame):
#             processed_count += 1
#             result = future.result()
            
#             # Update statistics
#             if result.get("is_blurry", False):
#                 blur_count += 1
#             if result.get("has_face", False):
#                 face_count += 1
#             if result.get("has_emotion", False) and result.get("emotion_match", False):
#                 emotion_count += 1
                
#             # Check if this is a valid thumbnail candidate
#             valid_candidate = (
#                 result.get("success", False) and 
#                 result.get("has_face", False) and 
#                 result.get("meets_coverage", False) and 
#                 not result.get("is_blurry", False)
#             )
#             if params.get("include_emotions", True):
#                 valid_candidate = valid_candidate and result.get("emotion_match", False)

#             if valid_candidate:
#                 thumbnails.append(result)
#                 # Sort thumbnails by a combination of face coverage and blur score
#                 thumbnails.sort(key=lambda x: (x["face_coverage"], x["blur_score"]), reverse=True)
                
#                 # Limit to requested number
#                 thumbnails = thumbnails[:params.get("num_thumbnails", 5)]
    
#     # Process thumbnails - save to storage and enhance if needed
#     processed_thumbnails = []
#     for thumbnail in thumbnails:
#         frame = thumbnail["frame"]
        
#         # Save original thumbnail
#         save_result = save_thumbnail_to_storage(
#             frame,
#             video_title,
#             thumbnail["timestamp"],
#             thumbnail["dominant_emotion"],
#             params.get("save_location", "thumbnails"),
#             params.get("save_format", "jpg")
#         )
        
#         if not save_result:
#             continue
        
#         thumbnail_data = {
#             "original": save_result,
#             "timestamp": thumbnail["timestamp"],
#             "dominant_emotion": thumbnail["dominant_emotion"],
#             "face_coverage": thumbnail["face_coverage"],
#             "blur_score": thumbnail["blur_score"]
#         }
        
#         # If enhancement is enabled, save enhanced version
#         if params.get("enable_enhancement", True):
#             enhanced_frame = enhance_image(frame)
#             enhanced_save_result = save_thumbnail_to_storage(
#                 enhanced_frame,
#                 video_title,
#                 thumbnail["timestamp"],
#                 f"{thumbnail['dominant_emotion']}_enhanced",
#                 params.get("save_location", "thumbnails"),
#                 params.get("save_format", "jpg")
#             )
            
#             if enhanced_save_result:
#                 thumbnail_data["enhanced"] = enhanced_save_result
        
#         processed_thumbnails.append(thumbnail_data)
    
#     # Clean up - remove temporary video file
#     try:
#         os.remove(video_path)
#     except:
#         pass
    
#     return {
#         "success": True,
#         "video_title": video_title,
#         "original_thumbnail": video_thumbnail,
#         "thumbnails": processed_thumbnails,
#         "stats": {
#             "total_frames": total_frames,
#             "blurry_frames": blur_count,
#             "frames_with_faces": face_count,
#             "frames_with_matching_emotions": emotion_count
#         }
#     }

import cv2
import numpy as np
import tempfile
import os
import concurrent.futures
import yt_dlp
from deepface import DeepFace
from scipy.ndimage import gaussian_filter
import uuid
from pathlib import Path
import urllib.request
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from urllib.parse import urlparse, unquote
import re
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageOps
from io import BytesIO
from googletrans import Translator

def download_youtube_video(url, output_path=None):
    """
    Download a YouTube video or handle local file using yt-dlp
    
    Parameters:
    - url: YouTube URL or local file path
    - output_path: Directory to save the video (uses temp dir if None)
    
    Returns:
    - Dictionary with download status and info
    """
    try:
        is_local_file = False
        final_path = None

        # Check if URL is a local file path
        if re.match(r'^[a-zA-Z]:[\\/]', url) or os.path.exists(url):
            final_path = os.path.abspath(url.replace('file://', ''))
            if os.path.isfile(final_path):
                is_local_file = True
        elif url.startswith('file://'):
            parsed = urlparse(url)
            file_path = unquote(parsed.path)
            if os.name == 'nt':
                file_path = file_path.lstrip('/').replace('/', '\\')
            else:
                file_path = file_path
            final_path = os.path.abspath(file_path)
            if os.path.isfile(final_path):
                is_local_file = True

        if is_local_file:
            return {
                "success": True,
                "video_path": final_path,
                "title": os.path.splitext(os.path.basename(final_path))[0],
                "thumbnail": None,
                "is_local": True
            }

        if not url.lower().startswith(('http://', 'https://')):
            return {"success": False, "error": "Unsupported URL scheme"}

        if not url:
            return {
                "success": False,
                "error": "No URL provided"
            }
            
        # Create output directory if needed
        if output_path is None:
            output_path = tempfile.mkdtemp()
        elif not os.path.exists(output_path):
            os.makedirs(output_path)
            
        # Create a random filename to avoid conflicts
        random_filename = f"video_{uuid.uuid4().hex}.mp4"
        output_file = os.path.join(output_path, random_filename)
        
        # yt-dlp options
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': output_file,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
        }
        
        # Download info first to get metadata
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown Title')
            thumbnail_url = info.get('thumbnail', '')
            
            # Now download the video
            ydl.download([url])
        
        # Make sure file exists
        if not os.path.exists(output_file):
            return {
                "success": False,
                "error": "Download completed but file not found"
            }
            
        return {
            "success": True,
            "video_path": output_file,
            "title": video_title,
            "thumbnail": thumbnail_url,
            "is_local": False
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing video source: {str(e)}"
        }

# def download_youtube_video(url, output_path=None):
#     """
#     Download a YouTube video or handle local file using yt-dlp
    
#     Parameters:
#     - url: YouTube URL, file:// URL, or local file path
#     - output_path: Directory to save the video (uses temp dir if None)
    
#     Returns:
#     - Dictionary with download status and info
#     """
#     try:
#         print(f"Processing input: {url}")
#         is_local_file = False
#         final_path = None
#         safe_dir = r"C:\Users\santoshj\Desktop\vi"  # Restrict local files to this directory

#         # Normalize input by replacing backslashes with forward slashes for consistency
#         normalized_url = url.replace('\\', '/')

#         # Check if input is a local file path
#         if re.match(r'^[a-zA-Z]:[/\\]', normalized_url) or os.path.exists(normalized_url):
#             final_path = os.path.abspath(os.path.normpath(normalized_url.replace('file://', '')))
#             print(f"Checking raw path: {final_path}")
#             if os.path.isfile(final_path):
#                 is_local_file = True
#         elif normalized_url.startswith('file://'):
#             parsed = urlparse(normalized_url)
#             file_path = unquote(parsed.path)
#             print(f"Parsed file:// path: {file_path}")
#             if os.name == 'nt':
#                 # Remove leading slashes for Windows
#                 file_path = file_path.lstrip('/')
#                 # Ensure path starts with drive letter
#                 if not re.match(r'^[a-zA-Z]:', file_path):
#                     return {"success": False, "error": "Invalid file:// path format"}
#             else:
#                 file_path = file_path.lstrip('/')
#             final_path = os.path.abspath(os.path.normpath(file_path))
#             print(f"Checking file:// path: {final_path}")
#             if os.path.isfile(final_path):
#                 is_local_file = True
#             else:
#                 print(f"File does not exist or is not a file: {final_path}")

#         if is_local_file:
#             # Security: Restrict to safe directory
#             if not final_path.startswith(os.path.abspath(safe_dir)):
#                 print(f"Path outside safe directory: {final_path}")
#                 return {"success": False, "error": "File path outside allowed directory"}
#             print(f"Local file confirmed: {final_path}")
#             return {
#                 "success": True,
#                 "video_path": final_path,
#                 "title": os.path.splitext(os.path.basename(final_path))[0],
#                 "thumbnail": None,
#                 "is_local": True
#             }

#         # Validate URL for YouTube download
#         if not normalized_url.lower().startswith(('http://', 'https://')):
#             print(f"Invalid URL scheme: {normalized_url}")
#             return {"success": False, "error": "Unsupported URL scheme"}

#         if not normalized_url:
#             return {"success": False, "error": "No URL provided"}
            
#         # Create output directory if needed
#         if output_path is None:
#             output_path = tempfile.mkdtemp()
#         elif not os.path.exists(output_path):
#             os.makedirs(output_path)
            
#         # Create a random filename to avoid conflicts
#         random_filename = f"video_{uuid.uuid4().hex}.mp4"
#         output_file = os.path.join(output_path, random_filename)
        
#         # yt-dlp options
#         ydl_opts = {
#             'format': 'best[ext=mp4]',
#             'outtmpl': output_file,
#             'noplaylist': True,
#             'quiet': True,
#             'no_warnings': True,
#             'noprogress': True,
#         }
        
#         # Download info first to get metadata
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(normalized_url, download=False)
#             video_title = info.get('title', 'Unknown Title')
#             thumbnail_url = info.get('thumbnail', '')
            
#             # Now download the video
#             ydl.download([normalized_url])
        
#         # Make sure file exists
#         if not os.path.exists(output_file):
#             return {"success": False, "error": "Download completed but file not found"}
            
#         print(f"YouTube video downloaded: {output_file}")
#         return {
#             "success": True,
#             "video_path": output_file,
#             "title": video_title,
#             "thumbnail": thumbnail_url,
#             "is_local": False
#         }
        
#     except Exception as e:
#         print(f"Error in download_youtube_video: {str(e)}")
#         return {"success": False, "error": f"Error processing video source: {str(e)}"}
    
def extract_frames(video_path, interval_secs=2):
    frames = []
    timestamps = []
    
    try:
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        # Calculate frame indices to extract based on interval
        frame_interval = int(fps * interval_secs)
        frame_indices = list(range(0, total_frames, frame_interval))
        
        for i in frame_indices:
            video.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = video.read()
            
            if ret:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                timestamp = i / fps  # Calculate timestamp in seconds
                
                frames.append(rgb_frame)
                timestamps.append(timestamp)
        
        video.release()
        
        return {
            "success": True,
            "frames": frames,
            "timestamps": timestamps,
            "total_duration": duration,
            "total_frames": total_frames
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def detect_blur(image, threshold=100):
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    # Calculate the Laplacian variance
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Return blur score and whether image is blurry
    return {
        "blur_score": lap_var,
        "is_blurry": lap_var < threshold
    }

def stabilize_image(image):
    # Apply light Gaussian blur to reduce noise
    stabilized = gaussian_filter(image, sigma=0.5)
    return stabilized

def enhance_image(image, stability=25, scale=2.0, hdr=True, beautify=True):
    img = Image.fromarray(image).convert("RGB")
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1 + stability / 50)

    if scale > 1:
        img = img.resize((int(img.width * scale), int(img.height * scale)))

    if hdr:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)

    if beautify:
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.5)

    return np.array(img)

def adjust_manual(img, brightness=50, contrast=50, saturation=50, hue=0):
    img = np.array(img).astype(np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)

    h, s, v = cv2.split(img)
    h = (h + hue) % 180
    s = np.clip(s * (saturation / 50), 0, 255)
    v = np.clip(v * (brightness / 50), 0, 255)

    img = cv2.merge([h, s, v]).astype(np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
    img = Image.fromarray(img)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast / 50)
    return np.array(img)

def pad_to_aspect_ratio(image, target_ratio):
    img = Image.fromarray(image).convert("RGB")
    img_w, img_h = img.size
    img_ratio = img_w / img_h

    if img_ratio > target_ratio:
        new_h = int(img_w / target_ratio)
        new_w = img_w
    else:
        new_w = int(img_h * target_ratio)
        new_h = img_h

    pad_left = (new_w - img_w) // 2
    pad_top = (new_h - img_h) // 2
    padding = (pad_left, pad_top, new_w - img_w - pad_left, new_h - img_h - pad_top)
    img = ImageOps.expand(img, padding, fill="black")
    return np.array(img)

def translate_text(text, target_lang):
    translator = Translator()
    lang_code = {"English": "en", "Hindi": "hi", "Kannada": "kn"}
    if target_lang == "English":
        return text
    try:
        translated = translator.translate(text, dest=lang_code[target_lang])
        return translated.text
    except Exception:
        return text

def add_text_overlay(img, text, position, size, font_path):
    img = Image.fromarray(img).convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, size)
    except Exception:
        font = ImageFont.load_default()
    
    w, h = img.size
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    if position == "Top-Left":
        xy = (10, 10)
    elif position == "Top-Right":
        xy = (w - text_w - 10, 10)
    elif position == "Bottom-Left":
        xy = (10, h - text_h - 10)
    elif position == "Bottom-Right":
        xy = (w - text_w - 10, h - text_h - 10)
    else:
        xy = ((w - text_w) // 2, (h - text_h) // 2)
    
    draw.text(xy, text, fill="white", font=font)
    return np.array(img)

def add_logo(img, logo_file, position="Top-Left", max_size=150):
    img = Image.fromarray(img).convert("RGB")
    logo = Image.open(logo_file).convert("RGBA")
    
    width, height = logo.size
    ratio = min(max_size/width, max_size/height)
    new_size = (int(width * ratio), int(height * ratio))
    logo = logo.resize(new_size, Image.Resampling.LANCZOS)
    
    bx, by = img.size
    lx, ly = logo.size
    positions = {
        "Top-Left": (10, 10),
        "Top-Right": (bx - lx - 10, 10),
        "Bottom-Left": (10, by - ly - 10),
        "Bottom-Right": (bx - lx - 10, by - ly - 10),
        "Center": ((bx - lx) // 2, (by - ly) // 2)
    }
    pos = positions.get(position, (10, 10))
    img.paste(logo, pos, logo)
    return np.array(img)

def remove_logo_annotation(img, x1, y1, x2, y2):
    img = Image.fromarray(np.array(img)).convert("RGB")
    h, w = img.size[1], img.size[0]
    
    x1 = max(0, min(int(x1), w-1))
    y1 = max(0, min(int(y1), h-1))
    x2 = max(x1+1, min(int(x2), w))
    y2 = max(y1+1, min(int(y2), h))
    
    img_np = np.array(img)
    blur_region = img_np[y1:y2, x1:x2]
    if blur_region.size > 0:
        blur_region = cv2.GaussianBlur(blur_region, (23, 23), 30)
        img_np[y1:y2, x1:x2] = blur_region
    return Image.fromarray(img_np)

def compress_image(img, quality=70):
    img = Image.fromarray(np.array(img)).convert("RGB")
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=quality)
    img_byte_arr.seek(0)
    return img_byte_arr

def load_face_detector():
    # Load pre-trained face detection model (Haar Cascade)
    model_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(model_path)
    return face_cascade

def detect_faces(image, face_cascade, min_confidence=0.5):
    # Convert to grayscale for Haar cascade
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # Calculate face locations and areas
    face_locations = []
    face_areas = []
    
    for (x, y, w, h) in faces:
        face_locations.append((y, x+w, y+h, x))  # Convert to (top, right, bottom, left) format
        face_areas.append(w * h)
    
    return face_locations, face_areas

def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def process_frame(frame_data):
    frame, timestamp, face_threshold, face_coverage, selected_emotions, face_cascade, include_emotions, blur_threshold, enable_stabilization, enable_enhancement = frame_data

    # Stabilize image if enabled
    if enable_stabilization:
        frame = stabilize_image(frame)
    
    # Check for blur
    blur_result = detect_blur(frame, threshold=blur_threshold)
    if blur_result["is_blurry"]:
        return {
            "success": False,
            "is_blurry": True,
            "blur_score": blur_result["blur_score"],
            "timestamp": timestamp
        }
    
    # Detect faces using OpenCV
    face_locations, face_areas = detect_faces(frame, face_cascade, min_confidence=face_threshold)
    
    if not face_locations:
        return {
            "success": False,
            "has_face": False,
            "is_blurry": False,
            "timestamp": timestamp,
            "blur_score": blur_result["blur_score"]
        }
    
    # Calculate face coverage
    frame_area = frame.shape[0] * frame.shape[1]
    max_face_index = np.argmax(face_areas) if face_areas else -1
    
    if max_face_index >= 0:
        max_face_area = face_areas[max_face_index]
        max_face_location = face_locations[max_face_index]
        face_coverage_percent = (max_face_area / frame_area) * 100
    else:
        return {
            "success": False,
            "has_face": False,
            "is_blurry": False,
            "timestamp": timestamp,
            "blur_score": blur_result["blur_score"]
        }
    
    # Check if face meets coverage criteria
    if face_coverage_percent < face_coverage:
        return {
            "success": True,
            "has_face": True,
            "meets_coverage": False,
            "is_blurry": False,
            "face_coverage": face_coverage_percent,
            "timestamp": timestamp,
            "blur_score": blur_result["blur_score"]
        }

    emotion_match = True  # Default to True to include frame unless emotion filtering is active
    dominant_emotion = "none"  # Default when no emotion detection is performed
    emotion_confidence = 0.0

    if include_emotions:
        try:
            top, right, bottom, left = max_face_location
            if bottom <= top or right <= left:
                raise ValueError("Invalid face coordinates")
            face_img = frame[top:bottom, left:right]
            if face_img.size == 0:
                raise ValueError("Empty face image")
            face_img_bgr = cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR)
            emotion_result = DeepFace.analyze(
                face_img_bgr, 
                actions=['emotion'],
                detector_backend='opencv',
                enforce_detection=False,
                silent=True
            )
            if emotion_result:
                emotion_scores = emotion_result[0]['emotion']
                valid_emotions = {emo: score for emo, score in emotion_scores.items() if score > 0}
                if valid_emotions:
                    dominant_emotion = max(valid_emotions, key=valid_emotions.get)
                    emotion_confidence = valid_emotions[dominant_emotion]
                    selected_lower = [e.lower() for e in selected_emotions]
                    emotion_match = dominant_emotion.lower() in selected_lower
                else:
                    emotion_match = False
            else:
                emotion_match = False
        except Exception as e:
            print(f"Emotion detection error: {str(e)}")
            emotion_match = False

    return {
        "success": True,
        "has_face": True,
        "meets_coverage": True,
        "has_emotion": bool(dominant_emotion != "none" and include_emotions),
        "emotion_match": emotion_match,
        "is_blurry": False,
        "face_coverage": face_coverage_percent,
        "dominant_emotion": dominant_emotion,
        "emotion_confidence": emotion_confidence,
        "frame": frame,
        "timestamp": timestamp,
        "blur_score": blur_result["blur_score"],
        "face_location": max_face_location
    }

def prepare_frame_data(frames, timestamps, face_threshold, face_coverage, selected_emotions, 
                     face_cascade, include_emotions, blur_threshold, 
                     enable_stabilization, enable_enhancement):
    """Prepare data for parallel processing of frames"""
    return [
        (frame, timestamp, face_threshold, face_coverage, selected_emotions, 
         face_cascade, include_emotions, blur_threshold, enable_stabilization, enable_enhancement)
        for frame, timestamp in zip(frames, timestamps)
    ]

def save_thumbnail_to_storage(frame, video_title, timestamp, emotion, save_dir="thumbnails", format="jpg", enhanced=False):
    """Save thumbnail to Django's storage system"""
    # Format timestamp for filename
    timestamp_str = format_time(timestamp).replace(":", "_")
    
    # Clean video title for filename
    clean_title = "".join([c for c in video_title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    clean_title = clean_title.replace(" ", "_")
    
    # Create filename
    filename = f"{clean_title}_{emotion}_{timestamp_str}.{format}"
    if enhanced:
        filename = f"{clean_title}_{emotion}_{timestamp_str}_enhanced.{format}"
    filepath = os.path.join(save_dir, filename)
    
    # Convert RGB to BGR for saving with OpenCV
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # Save to bytes
    success, buffer = cv2.imencode(f".{format}", frame_bgr)
    if not success:
        return None
    
    # Save to storage
    thumbnail_file = ContentFile(buffer.tobytes(), name=filename)
    saved_path = default_storage.save(filepath, thumbnail_file)
    
    return {
        "filename": filename,
        "path": saved_path,
        "url": default_storage.url(saved_path)
    }

def save_enhanced_thumbnails(thumbnails, save_dir, format="jpg", compress=False, quality=70):
    """Save enhanced thumbnails to Django's storage system"""
    saved_files = []
    
    for thumbnail in thumbnails:
        enhanced = thumbnail["enhanced"]
        timestamp = thumbnail["timestamp"]
        timestamp_str = format_time(timestamp).replace(":", "_")
        filename = f"enhanced_thumbnail_{timestamp_str}.{format}"
        filepath = os.path.join(save_dir, filename)
        
        if compress:
            img_data = compress_image(enhanced, quality)
            thumbnail_file = ContentFile(img_data.read(), name=filename)
            saved_path = default_storage.save(filepath, thumbnail_file)
        else:
            enhanced_pil = Image.fromarray(enhanced).convert("RGB")
            img_byte_arr = BytesIO()
            enhanced_pil.save(img_byte_arr, format=format.upper())
            img_byte_arr.seek(0)
            thumbnail_file = ContentFile(img_byte_arr.read(), name=filename)
            saved_path = default_storage.save(filepath, thumbnail_file)
        
        saved_files.append({
            "filename": filename,
            "path": saved_path,
            "url": default_storage.url(saved_path)
        })
    
    return {
        "count": len(saved_files),
        "directory": save_dir,
        "files": saved_files
    }

def generate_thumbnails(youtube_url, params):
    """
    Main function to generate thumbnails from YouTube video
    
    Parameters:
    - youtube_url: URL of the YouTube video or local file path
    - params: Dictionary of parameters for thumbnail generation
    
    Returns:
    - Dictionary with results
    """
    # Download video
    download_result = download_youtube_video(youtube_url)
    
    if not download_result["success"]:
        return {
            "success": False,
            "error": download_result["error"]
        }
    
    video_path = download_result["video_path"]
    video_title = download_result["title"]
    video_thumbnail = download_result["thumbnail"]
    is_local = download_result["is_local"]
    
    # Extract frames
    extraction_result = extract_frames(video_path, interval_secs=params.get("frame_interval", 2))
    
    if not extraction_result["success"]:
        return {
            "success": False,
            "error": extraction_result["error"]
        }
    
    frames = extraction_result["frames"]
    timestamps = extraction_result["timestamps"]
    
    # Load face detector
    face_cascade = load_face_detector()
    
    # Prepare data for parallel processing
    frame_data = prepare_frame_data(
        frames, 
        timestamps, 
        params.get("face_threshold", 0.5),
        params.get("face_coverage", 20),
        params.get("selected_emotions", []),
        face_cascade,
        params.get("include_emotions", True),
        params.get("blur_threshold", 100),
        params.get("enable_stabilization", True),
        params.get("enable_enhancement", True)
    )
    
    # Process frames in parallel
    thumbnails = []
    processed_count = 0
    total_frames = len(frames)
    
    blur_count = 0
    face_count = 0
    emotion_count = 0
    
    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=params.get("max_workers", 4)) as executor:
        future_to_frame = {executor.submit(process_frame, fd): idx for idx, fd in enumerate(frame_data)}
        
        for future in concurrent.futures.as_completed(future_to_frame):
            processed_count += 1
            result = future.result()
            
            # Update statistics
            if result.get("is_blurry", False):
                blur_count += 1
            if result.get("has_face", False):
                face_count += 1
            if result.get("has_emotion", False) and result.get("emotion_match", False):
                emotion_count += 1
                
            # Check if this is a valid thumbnail candidate
            valid_candidate = (
                result.get("success", False) and 
                result.get("has_face", False) and 
                result.get("meets_coverage", False) and 
                not result.get("is_blurry", False)
            )
            if params.get("include_emotions", True):
                valid_candidate = valid_candidate and result.get("emotion_match", False)

            if valid_candidate:
                thumbnails.append(result)
                # Sort thumbnails by a combination of face coverage and blur score
                thumbnails.sort(key=lambda x: (x["face_coverage"], x["blur_score"]), reverse=True)
                
                # Limit to requested number
                thumbnails = thumbnails[:params.get("num_thumbnails", 5)]
    
    # Process thumbnails - save to storage and enhance if needed
    processed_thumbnails = []
    for thumbnail in thumbnails:
        frame = thumbnail["frame"]
        
        # Save original thumbnail
        save_result = save_thumbnail_to_storage(
            frame,
            video_title,
            thumbnail["timestamp"],
            thumbnail["dominant_emotion"],
            params.get("save_location", "thumbnails"),
            params.get("save_format", "jpg"),
            enhanced=False
        )
        
        if not save_result:
            continue
        
        thumbnail_data = {
            "original": save_result,
            "timestamp": thumbnail["timestamp"],
            "dominant_emotion": thumbnail["dominant_emotion"],
            "face_coverage": thumbnail["face_coverage"],
            "blur_score": thumbnail["blur_score"],
            "face_location": thumbnail["face_location"]
        }
        
        # If enhancement is enabled, save enhanced version
        if params.get("enable_enhancement", True):
            enhanced_frame = enhance_image(
                frame,
                stability=params.get("stability", 25),
                scale=params.get("scale", 2.0),
                hdr=params.get("hdr", True),
                beautify=params.get("beautify", True)
            )
            enhanced_save_result = save_thumbnail_to_storage(
                enhanced_frame,
                video_title,
                thumbnail["timestamp"],
                f"{thumbnail['dominant_emotion']}_enhanced",
                params.get("save_location", "thumbnails"),
                params.get("save_format", "jpg"),
                enhanced=True
            )
            
            if enhanced_save_result:
                thumbnail_data["enhanced"] = enhanced_save_result
        
        processed_thumbnails.append(thumbnail_data)
    
    # Clean up - remove temporary video file if not local
    if not is_local and os.path.exists(video_path):
        try:
            os.remove(video_path)
        except:
            pass
    
    return {
        "success": True,
        "video_title": video_title,
        "original_thumbnail": video_thumbnail,
        "thumbnails": processed_thumbnails,
        "stats": {
            "total_frames": total_frames,
            "blurry_frames": blur_count,
            "frames_with_faces": face_count,
            "frames_with_matching_emotions": emotion_count
        }
    }

