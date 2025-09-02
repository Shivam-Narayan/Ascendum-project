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

def stabilize_image(image):
    return gaussian_filter(image, sigma=0.5)

def enhance_image(image, stability=25, scale=2, hdr=True, beautify=True):
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
    img = np.array(img).astype(np.uint8)  # Ensure input is NumPy array
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)

    h, s, v = cv2.split(img)
    h = (h + hue) % 180
    s = np.clip(s * (saturation / 50), 0, 255)
    v = np.clip(v * (brightness / 50), 0, 255)

    img = cv2.merge([h, s, v]).astype(np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
    img = Image.fromarray(img)  # Convert to PIL Image for contrast enhancement
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast / 50)
    return np.array(img)  # Convert back to NumPy array

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
    except Exception as e:
        return text

def add_text_overlay(img, text, position="Center", size=30, font_path=None):
    img = Image.fromarray(img).convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
    except Exception as e:
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
    else:  # Center
        xy = ((w - text_w) // 2, (h - text_h) // 2)
    
    draw.text(xy, text, fill="white", font=font)
    return np.array(img)

def add_logo(img, logo_file, position="Top-Left"):
    img = Image.fromarray(img).convert("RGB")
    logo = Image.open(logo_file).convert("RGBA")
    logo.thumbnail((100, 100))
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

def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"

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

    if not include_emotions:
        return {
            "success": True,
            "has_face": True,
            "meets_coverage": True,
            "has_emotion": False,
            "emotion_match": True,
            "is_blurry": False,
            "face_coverage": face_coverage_percent,
            "frame": frame,
            "timestamp": timestamp,
            "blur_score": blur_result["blur_score"],
            "face_location": max_face_index,
            "dominant_emotion": "No emotion detection"
        }

    emotion_match = False
    dominant_emotion = "neutral"
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
            selected_lower = [e.lower() for e in selected_emotions]
            emotion_match = any(
                emotion_scores[emo] > 0 
                for emo in emotion_scores 
                if emo.lower() in selected_lower
            )
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
    except Exception as e:
        print(f"Emotion detection error: {str(e)}")

    return {
        "success": True,
        "has_face": True,
        "meets_coverage": True,
        "has_emotion": bool(dominant_emotion),
        "emotion_match": emotion_match,
        "is_blurry": False,
        "face_coverage": face_coverage_percent,
        "dominant_emotion": dominant_emotion or "Unknown",
        "frame": frame,
        "timestamp": timestamp,
        "blur_score": blur_result["blur_score"],
        "face_location": max_face_location
    }

def generate_thumbnails_from_video(youtube_url, params):
    face_threshold = params.get('face_threshold', 0.5)
    face_coverage = params.get('face_coverage', 3)
    num_thumbnails = params.get('num_thumbnails', 5)
    include_emotions = params.get('include_emotions', True)
    selected_emotions = params.get('selected_emotions', ["happy", "surprise"])
    frame_interval = params.get('frame_interval', 2)
    max_workers = params.get('max_workers', 4)
    blur_threshold = params.get('blur_threshold', 30)
    enable_stabilization = params.get('enable_stabilization', True)
    enable_enhancement = params.get('enable_enhancement', True)
    
    download_result = download_youtube_video(youtube_url)
    
    if not download_result["success"]:
        return {
            "success": False,
            "error": download_result["error"]
        }
    
    video_path = download_result["video_path"]
    video_title = download_result["title"]
    is_local = download_result["is_local"]
    
    extraction_result = extract_frames(video_path, interval_secs=frame_interval)
    
    if not extraction_result["success"]:
        return {
            "success": False,
            "error": extraction_result["error"]
        }
    
    frames = extraction_result["frames"]
    timestamps = extraction_result["timestamps"]
    
    face_cascade = load_face_detector()
    
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
    
    if not is_local and os.path.exists(video_path):
        try:
            os.remove(video_path)
        except:
            pass
    
    return {
        "success": True,
        "thumbnails": thumbnails,
        "video_title": video_title
    }

def enhance_thumbnail(thumbnail, enhancement_params):
    frame = thumbnail["frame"]
    
    # AI Enhancements
    stability = enhancement_params.get('stability', 25)
    scale = enhancement_params.get('scale', 2.0)
    hdr = enhancement_params.get('hdr', True)
    beautify = enhancement_params.get('beautify', True)
    
    enhanced = enhance_image(frame, stability, scale, hdr, beautify)
    
    # Manual Enhancements
    brightness = enhancement_params.get('brightness', 50)
    contrast = enhancement_params.get('contrast', 50)
    saturation = enhancement_params.get('saturation', 50)
    hue = enhancement_params.get('hue', 0)
    
    enhanced = adjust_manual(enhanced, brightness, contrast, saturation, hue)
    
    # Aspect Ratio
    aspect_ratio = enhancement_params.get('aspect_ratio', "Original")
    if aspect_ratio != "Original":
        if aspect_ratio == "1:1":
            target_ratio = 1
        elif aspect_ratio == "4:3":
            target_ratio = 4 / 3
        elif aspect_ratio == "16:9":
            target_ratio = 16 / 9
        enhanced = pad_to_aspect_ratio(enhanced, target_ratio)
    
    # Logo
    logo_file = enhancement_params.get('logo_file', None)
    if logo_file:
        logo_position = enhancement_params.get('logo_position', "Top-Left")
        enhanced = add_logo(enhanced, logo_file, logo_position)
    
    # Text
    text = enhancement_params.get('text', None)
    if text:
        language = enhancement_params.get('language', "English")
        font_position = enhancement_params.get('font_position', "Center")
        font_size = enhancement_params.get('font_size', 30)
        font_path = enhancement_params.get('font_path', None)
        
        translated_text = translate_text(text, language)
        enhanced = add_text_overlay(enhanced, translated_text, font_position, font_size, font_path)
    
    # Blur regions
    blur_regions = enhancement_params.get('blur_regions', [])
    if blur_regions:
        enhanced_pil = Image.fromarray(enhanced).convert("RGB")
        for region in blur_regions:
            enhanced_pil = remove_logo_annotation(
                enhanced_pil, region["x1"], region["y1"], region["x2"], region["y2"]
            )
        enhanced = np.array(enhanced_pil)
    
    return {
        "original": frame,
        "enhanced": enhanced,
        "timestamp": thumbnail["timestamp"],
        "face_location": thumbnail.get("face_location", None)
    }