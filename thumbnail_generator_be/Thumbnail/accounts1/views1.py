import cv2
import numpy as np
import tempfile
import os
import concurrent.futures
import urllib.request
import uuid
import yt_dlp
from pathlib import Path
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from scipy.ndimage import gaussian_filter
from deepface import DeepFace
from urllib.parse import urlparse, unquote
import re
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageOps, ImageFilter
from io import BytesIO
from googletrans import Translator
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
import base64
from django.conf import settings

# Helper functions (same as in your Streamlit app)
def download_youtube_video(url, output_path=None):
    try:
        is_local_file = False
        final_path = None

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

        if output_path is None:
            output_path = tempfile.mkdtemp()
        elif not os.path.exists(output_path):
            os.makedirs(output_path)

        random_filename = f"video_{uuid.uuid4().hex}.mp4"
        output_file = os.path.join(output_path, random_filename)

        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': output_file,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown Title')
            thumbnail_url = info.get('thumbnail', '')
            ydl.download([url])

        if not os.path.exists(output_file):
            return {"success": False, "error": "Download failed"}

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
pass

def extract_frames(video_path, interval_secs=2):
    frames = []
    timestamps = []
    
    try:
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        frame_interval = int(fps * interval_secs)
        frame_indices = list(range(0, total_frames, frame_interval))
        
        for i in frame_indices:
            video.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = video.read()
            
            if ret:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                timestamp = i / fps
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
pass

def detect_blur(image, threshold=100):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return {
        "blur_score": lap_var,
        "is_blurry": lap_var < threshold
    }
pass

def stabilize_image(image):
    return gaussian_filter(image, sigma=0.5)
pass

def enhance_image(image, stability, scale, hdr, beautify):
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
pass

def adjust_manual(img, brightness, contrast, saturation, hue):
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
pass

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
pass

def translate_text(text, target_lang):
    translator = Translator()
    lang_code = {"English": "en", "Hindi": "hi", "Kannada": "kn"}
    if target_lang == "English":
        return text
    try:
        translated = translator.translate(text, dest=lang_code[target_lang])
        return translated.text
    except Exception as e:
        # st.error(f"Translation error: {str(e)}")
        return text
pass

def add_text_overlay(img, text, position, size, font_path):
    img = Image.fromarray(img).convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, size)
    except Exception:
        # st.warning(f"Font not found: {font_path}. Using default font.")
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
pass

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
pass

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
pass

def compress_image(img, quality=70):
    img = Image.fromarray(np.array(img)).convert("RGB")
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=quality)
    img_byte_arr.seek(0)
    return img_byte_arr
pass

def resize_image_fixed_width(img, fixed_width=600):
    """Resize image to a fixed width while maintaining aspect ratio."""
    img = Image.fromarray(np.array(img)).convert("RGB")
    aspect = img.width / img.height
    display_height = int(fixed_width / aspect)
    return img.resize((fixed_width, display_height))

def load_face_detector():
    model_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(model_path)
    return face_cascade

def detect_faces(image, face_cascade, min_confidence=0.5):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1, 
        minNeighbors=5, 
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    face_locations = []
    face_areas = []
    
    for (x, y, w, h) in faces:
        face_locations.append((y, x+w, y+h, x))
        face_areas.append(w * h)
    
    return face_locations, face_areas
pass

def process_frame(frame_data):
    frame, timestamp, face_threshold, face_coverage, selected_emotions, face_cascade, include_emotions, blur_threshold, enable_stabilization, enable_enhancement = frame_data

    if enable_stabilization:
        frame = stabilize_image(frame)

    blur_result = detect_blur(frame, threshold=blur_threshold)
    if blur_result["is_blurry"]:
        return {
            "success": False,
            "is_blurry": True,
            "blur_score": blur_result["blur_score"],
            "timestamp": timestamp
        }

    face_locations, face_areas = detect_faces(frame, face_cascade, min_confidence=face_threshold)
    
    if not face_locations:
        return {
            "success": False,
            "has_face": False,
            "is_blurry": False,
            "timestamp": timestamp,
            "blur_score": blur_result["blur_score"]
        }

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
pass

def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"
pass

def image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    return base64.b64encode(buffer).decode('utf-8')

# @api_view(['POST'])
# @parser_classes([MultiPartParser, FormParser])
# def generate_thumbnails2(request):
#     try:
#         # Get parameters from request
#         youtube_url = request.data.get('youtube_url', '')
#         face_threshold = float(request.data.get('face_threshold', 0.5))
#         face_coverage = int(request.data.get('face_coverage', 3))
#         num_thumbnails = int(request.data.get('num_thumbnails', 30))
#         include_emotions = request.data.get('include_emotions', 'false').lower() == 'true'
        
#         selected_emotions = request.data.get('selected_emotions', '').split(',')
#         selected_emotions = [e.strip() for e in selected_emotions if e.strip()]
        
#         frame_interval = int(request.data.get('frame_interval', 4))
#         max_workers = int(request.data.get('max_workers', 2))
#         blur_threshold = int(request.data.get('blur_threshold', 30))
#         enable_stabilization = request.data.get('enable_stabilization', 'true').lower() == 'true'
#         enable_enhancement = request.data.get('enable_enhancement', 'true').lower() == 'true'

#         # Download video
#         download_result = download_youtube_video(youtube_url)
#         if not download_result["success"]:
#             return Response({"error": download_result["error"]}, status=400)
        
#         video_path = download_result["video_path"]
#         video_title = download_result["title"]
#         video_thumbnail = download_result["thumbnail"]
#         is_local = download_result["is_local"]

#         # Extract frames
#         extraction_result = extract_frames(video_path, interval_secs=frame_interval)
#         if not extraction_result["success"]:
#             return Response({"error": extraction_result["error"]}, status=400)
        
#         frames = extraction_result["frames"]
#         timestamps = extraction_result["timestamps"]
        
#         face_cascade = load_face_detector()
        
#         # Process frames
#         frame_data = [
#             (frame, timestamp, face_threshold, face_coverage, selected_emotions, face_cascade, 
#              include_emotions, blur_threshold, enable_stabilization, enable_enhancement)
#             for frame, timestamp in zip(frames, timestamps)
#         ]
        
#         thumbnails = []
        
#         with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
#             future_to_frame = {executor.submit(process_frame, fd): idx for idx, fd in enumerate(frame_data)}
            
#             for future in concurrent.futures.as_completed(future_to_frame):
#                 result = future.result()
                
#                 valid_candidate = (
#                     result.get("success", False) and 
#                     result.get("has_face", False) and 
#                     result.get("meets_coverage", False) and 
#                     not result.get("is_blurry", False)
#                 )
                
#                 if include_emotions:
#                     valid_candidate = valid_candidate and result.get("emotion_match", False)
                
#                 if valid_candidate:
#                     thumbnails.append(result)
#                     thumbnails.sort(key=lambda x: (x["face_coverage"], x["blur_score"]), reverse=True)
#                     thumbnails = thumbnails[:num_thumbnails]
        
#         # Clean up video file
#         if not is_local and os.path.exists(video_path):
#             try:
#                 os.remove(video_path)
#             except:
#                 pass

#         response_data = {
#             "success": True,
#             "video_title": video_title,
#             "thumbnail_count": len(thumbnails),
#             "thumbnails": [],
#             "stats": {
#                 "total_frames": len(frames),
#                 "blurry_frames": sum(1 for t in thumbnails if t.get("is_blurry", False)),
#                 "frames_with_faces": sum(1 for t in thumbnails if t.get("has_face", False)),
#                 "frames_with_matching_emotions": sum(1 for t in thumbnails if t.get("emotion_match", False))
#             }
#         }

#         # Save thumbnails to media storage
#         save_dir = os.path.join(settings.MEDIA_ROOT, 'temp_thumbnails')
#         os.makedirs(save_dir, exist_ok=True)

#         for thumbnail in thumbnails:
#             # Generate filename with dominant emotion
#             timestamp_str = format_time(thumbnail['timestamp']).replace(":", "_")
#             clean_title = "".join([c for c in video_title if c.isalnum() or c in (' ', '_')]).strip().replace(" ", "_")
#             base_filename = f"{clean_title}_{thumbnail['dominant_emotion'].replace(' ', '_')}_{timestamp_str}_{uuid.uuid4().hex[:4]}"
#             filename = f"{base_filename}.jpg"
#             filepath = os.path.join(save_dir, filename)
            
#             # Save image
#             cv2.imwrite(filepath, cv2.cvtColor(thumbnail["frame"], cv2.COLOR_RGB2BGR))
            
#             # Add to response
#             response_data["thumbnails"].append({
#                 "timestamp": thumbnail["timestamp"],
#                 "formatted_time": format_time(thumbnail["timestamp"]),
#                 "face_coverage": thumbnail["face_coverage"],
#                 "blur_score": thumbnail["blur_score"],
#                 "dominant_emotion": thumbnail["dominant_emotion"],
#                 "emotion_confidence": thumbnail["emotion_confidence"],
#                 "image_url": f"{settings.MEDIA_URL}temp_thumbnails/{filename}"
                
#             })

#         # Clean up
#         if not is_local and os.path.exists(video_path):
#             os.remove(video_path)

#         return Response(response_data)

#     except Exception as e:
#         return Response({
#             "error": str(e),
#             "stats": {
#                 "total_frames": len(frames) if 'frames' in locals() else 0,
#                 "blurry_frames": 0,
#                 "frames_with_faces": 0,
#                 "frames_with_matching_emotions": 0
#             }
#         }, status=500)        


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def generate_thumbnails2(request):
    try:
        # Extract token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Token "):
            return Response({"error": "Missing or invalid token"}, status=401)

        token = auth_header.split(" ")[1]
        email = None

        # Identify user by token
        for user_email, user_token in VALID_TOKENS.items():
            if user_token == token:
                email = user_email
                break

        if not email:
            return Response({"error": "Invalid or expired token"}, status=401)

        # Get parameters from request
        youtube_url = request.data.get('youtube_url', '')
        face_threshold = float(request.data.get('face_threshold', 0.5))
        face_coverage = int(request.data.get('face_coverage', 3))
        num_thumbnails = int(request.data.get('num_thumbnails', 30))
        include_emotions = request.data.get('include_emotions', 'false').lower() == 'true'
        
        selected_emotions = request.data.get('selected_emotions', '').split(',')
        selected_emotions = [e.strip() for e in selected_emotions if e.strip()]
        
        frame_interval = int(request.data.get('frame_interval', 4))
        max_workers = int(request.data.get('max_workers', 2))
        blur_threshold = int(request.data.get('blur_threshold', 30))
        enable_stabilization = request.data.get('enable_stabilization', 'true').lower() == 'true'
        enable_enhancement = request.data.get('enable_enhancement', 'true').lower() == 'true'

        # Download video
        download_result = download_youtube_video(youtube_url)
        if not download_result["success"]:
            return Response({"error": download_result["error"]}, status=400)
        
        video_path = download_result["video_path"]
        video_title = download_result["title"]
        video_thumbnail = download_result["thumbnail"]
        is_local = download_result["is_local"]

        # Extract frames
        extraction_result = extract_frames(video_path, interval_secs=frame_interval)
        if not extraction_result["success"]:
            return Response({"error": extraction_result["error"]}, status=400)
        
        frames = extraction_result["frames"]
        timestamps = extraction_result["timestamps"]
        
        face_cascade = load_face_detector()
        
        # Process frames
        frame_data = [
            (frame, timestamp, face_threshold, face_coverage, selected_emotions, face_cascade, 
             include_emotions, blur_threshold, enable_stabilization, enable_enhancement)
            for frame, timestamp in zip(frames, timestamps)
        ]
        
        thumbnails = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_frame = {executor.submit(process_frame, fd): idx for idx, fd in enumerate(frame_data)}
            
            for future in concurrent.futures.as_completed(future_to_frame):
                result = future.result()
                
                valid_candidate = (
                    result.get("success", False) and 
                    result.get("has_face", False) and 
                    result.get("meets_coverage", False) and 
                    not result.get("is_blurry", False)
                )
                
                if include_emotions:
                    valid_candidate = valid_candidate and result.get("emotion_match", False)
                
                if valid_candidate:
                    thumbnails.append(result)
                    thumbnails.sort(key=lambda x: (x["face_coverage"], x["blur_score"]), reverse=True)
                    thumbnails = thumbnails[:num_thumbnails]

        response_data = {
            "success": True,
            "video_title": video_title,
            "thumbnail_count": len(thumbnails),
            "thumbnails": [],
            "stats": {
                "total_frames": len(frames),
                "blurry_frames": sum(1 for t in thumbnails if t.get("is_blurry", False)),
                "frames_with_faces": sum(1 for t in thumbnails if t.get("has_face", False)),
                "frames_with_matching_emotions": sum(1 for t in thumbnails if t.get("emotion_match", False))
            }
        }

        # Save to user-specific directory
        user_folder = os.path.join(settings.MEDIA_ROOT, 'temp_thumbnails', email)
        os.makedirs(user_folder, exist_ok=True)

        for thumbnail in thumbnails:
            timestamp_str = format_time(thumbnail['timestamp']).replace(":", "_")
            clean_title = "".join([c for c in video_title if c.isalnum() or c in (' ', '_')]).strip().replace(" ", "_")
            base_filename = f"{clean_title}_{thumbnail['dominant_emotion'].replace(' ', '_')}_{timestamp_str}_{uuid.uuid4().hex[:4]}"
            filename = f"{base_filename}.jpg"
            filepath = os.path.join(user_folder, filename)
            
            cv2.imwrite(filepath, cv2.cvtColor(thumbnail["frame"], cv2.COLOR_RGB2BGR))
            
            response_data["thumbnails"].append({
                "timestamp": thumbnail["timestamp"],
                "formatted_time": format_time(thumbnail["timestamp"]),
                "face_coverage": thumbnail["face_coverage"],
                "blur_score": thumbnail["blur_score"],
                "dominant_emotion": thumbnail["dominant_emotion"],
                "emotion_confidence": thumbnail["emotion_confidence"],
                "image_url": f"{settings.MEDIA_URL}temp_thumbnails/{email}/{filename}"
            })

        if not is_local and os.path.exists(video_path):
            os.remove(video_path)

        return Response(response_data)

    except Exception as e:
        return Response({
            "error": str(e),
            "stats": {
                "total_frames": len(frames) if 'frames' in locals() else 0,
                "blurry_frames": 0,
                "frames_with_faces": 0,
                "frames_with_matching_emotions": 0
            }
        }, status=500)






@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def enhance_thumbnail2(request):
    try:
        # Get parameters from request
        image_base64 = request.data.get('image')
        stability = int(request.data.get('stability', 25))
        scale = float(request.data.get('scale', 2.0))
        hdr = request.data.get('hdr', 'true').lower() == 'true'
        beautify = request.data.get('beautify', 'true').lower() == 'true'
        brightness = int(request.data.get('brightness', 50))
        contrast = int(request.data.get('contrast', 50))
        saturation = int(request.data.get('saturation', 50))
        hue = int(request.data.get('hue', 0))
        aspect_ratio = request.data.get('aspect_ratio', 'Original')
        compress = request.data.get('compress', 'false').lower() == 'true'
        quality = int(request.data.get('quality', 70))
        
        # Decode image
        image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
        image_np = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Apply enhancements
        enhanced = enhance_image(image, stability, scale, hdr, beautify)
        enhanced = adjust_manual(enhanced, brightness, contrast, saturation, hue)
        
        # Apply aspect ratio
        if aspect_ratio != "Original":
            target_ratio = 1 if aspect_ratio == "1:1" else 4/3 if aspect_ratio == "4:3" else 16/9
            enhanced = pad_to_aspect_ratio(enhanced, target_ratio)
        
        # Handle logo upload
        logo_file = request.FILES.get('logo_file')
        if logo_file:
            logo_position = request.data.get('logo_position', 'Top-Left')
            logo_size = int(request.data.get('logo_size', 150))
            
            # Save logo to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_logo:
                for chunk in logo_file.chunks():
                    temp_logo.write(chunk)
                temp_logo_path = temp_logo.name
            
            enhanced = add_logo(enhanced, temp_logo_path, logo_position, logo_size)
            os.unlink(temp_logo_path)
        
        # Add text
        text = request.data.get('text', '')
        if text:
            language = request.data.get('language', 'English')
            font_position = request.data.get('font_position', 'Center')
            font_size = int(request.data.get('font_size', 30))
            
            font_paths = {
                "English": "NotoSans-Regular.ttf",
                "Hindi": "NotoSansDevanagari-Regular.ttf",
                "Kannada": "NotoSerifKannada-Regular.ttf"
            }
            
            translated_text = translate_text(text, language)
            enhanced = add_text_overlay(
                enhanced,
                translated_text,
                font_position,
                font_size,
                font_paths.get(language, "NotoSans-Regular.ttf")
            )
        
        # Handle blur regions
        blur_regions = request.data.get('blur_regions', '[]')
        try:
            blur_regions = json.loads(blur_regions)
            for region in blur_regions:
                enhanced = remove_logo_annotation(
                    enhanced,
                    region["x1"], region["y1"],
                    region["x2"], region["y2"]
                )
        except:
            pass
        
        # Prepare response
        if compress:
            img_data = compress_image(enhanced, quality)
            response = HttpResponse(img_data.getvalue(), content_type='image/jpeg')
            response['Content-Disposition'] = 'attachment; filename="enhanced_thumbnail.jpg"'
            return response
        else:
            enhanced_base64 = image_to_base64(enhanced)
            return Response({
                "success": True,
                "enhanced_image": enhanced_base64
            })
    
    except Exception as e:
        return Response({"error": str(e)}, status=500)