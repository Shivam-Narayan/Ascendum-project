from django.shortcuts import render
import json
import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json, os, uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from functools import wraps
import shutil
from django.contrib.auth import logout
import shutil
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import ThumbnailRequestSerializer
from .utils import download_youtube_video, extract_frames, load_face_detector, prepare_frame_data, process_frame, enhance_image, format_time
import os
import cv2
import concurrent.futures
from django.conf import settings
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import os
import torch
import numpy as np
import cv2
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.http import HttpResponse
from PIL import Image, UnidentifiedImageError
import io
import zipfile
from logging_config import setup_logging
import logging
from rest_framework.decorators import parser_classes
import logging
from django.conf import settings



# Initialize logger
logger = setup_logging()

from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet


# In-memory token store (or use a simple file like tokens.json)
VALID_TOKENS = {}


def load_users():
    json_file_path = os.path.join(settings.BASE_DIR, 'users.json')
    with open(json_file_path, 'r') as f:
        return json.load(f)


def token_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({"error": "Missing or invalid Authorization header"}, status=401)

        token = auth_header.split(" ")[1]

        # Match token to user
        for email, valid_token in VALID_TOKENS.items():
            if token == valid_token:
                request.user_email = email  # 🔹 Set user_email on request
                return view_func(request, *args, **kwargs)

        return JsonResponse({"error": "Unauthorized"}, status=401)

    return wrapper


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            email = body.get('email')
            password = body.get('password')

            users = load_users()

            for user in users:
                if user['email'] == email and user['password'] == password:
                    token = str(uuid.uuid4())
                    VALID_TOKENS[email] = token
                    logger.info(f"User {email} logged in successfully")
                    return JsonResponse({"message": "Login successful", "token": token, "email": email}, status=200)

            logger.error(f"Failed login attempt for email: {email} - Invalid credentials")
            return JsonResponse({"message": "Invalid Credentials"}, status=401)

        except Exception as e:
            logger.error(f"Login error for email {email}: {str(e)}")
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"message": "Only POST method is allowed"}, status=405)


# @csrf_exempt
# @token_required
# def protected_api(request):
#     return JsonResponse({"message": "You have accessed a protected endpoint!"}, status=200)


# @token_required
# @api_view(['POST'])
# def generate_thumbnails_api(request):
#     """
#     API endpoint to generate thumbnails from a YouTube video or local file
    
#     Example POST data:
#     {
#         "youtube_url": "C:\\Users\\santoshj\\Desktop\\vi\\videoplayback.mp4",
#         "face_threshold": 0.5,
#         "face_coverage": 20,
#         "num_thumbnails": 5,
#         "include_emotions": true,
#         "selected_emotions": ["happy", "surprise"],
#         "frame_interval": 2,
#         "max_workers": 4,
#         "blur_threshold": 100,
#         "enable_stabilization": true,
#         "enable_enhancement": true,
#         "enable_autosave": false,
#         "save_location": "thumbnails",
#         "save_format": "jpg"
#     }
#     """
#     serializer = ThumbnailRequestSerializer(data=request.data)
#     if not serializer.is_valid():
#         logger.error(f"Invalid request data for {request.user_email}: {serializer.errors}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     try:
#         params = serializer.validated_data
#         youtube_url = params['youtube_url']
#         logger.info(f"Generating thumbnails for {request.user_email}, video: {youtube_url}")
        
#         # Download video or get local file path
#         download_result = download_youtube_video(youtube_url)
#         if not download_result["success"]:
#             logger.error(f"Video download failed for {request.user_email}, video: {youtube_url}, error: {download_result['error']}")
#             return Response(
#                 {"error": download_result["error"]},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         video_path = download_result["video_path"]
#         video_title = download_result["title"]
#         is_local = download_result.get("is_local", False)
        
#         # Extract frames
#         extraction_result = extract_frames(video_path, interval_secs=params['frame_interval'])
#         if not extraction_result["success"]:
#             logger.error(f"Frame extraction failed for {request.user_email}, video: {youtube_url}, error: {extraction_result['error']}")
#             return Response(
#                 {"error": extraction_result["error"]},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
        
#         frames = extraction_result["frames"]
#         timestamps = extraction_result["timestamps"]
        
#         # Initialize detectors
#         face_cascade = load_face_detector()
        
#         # Prepare data for parallel processing
#         frame_data = prepare_frame_data(
#             frames, timestamps, 
#             params['face_threshold'], params['face_coverage'], 
#             params['selected_emotions'], 
#             face_cascade, params['include_emotions'], 
#             params['blur_threshold'], params['enable_stabilization'], 
#             params['enable_enhancement']
#         )
        
#         # Process frames in parallel
#         thumbnails = []
#         with concurrent.futures.ThreadPoolExecutor(max_workers=params['max_workers']) as executor:
#             future_to_frame = {executor.submit(process_frame, fd): idx for idx, fd in enumerate(frame_data)}
            
#             for future in concurrent.futures.as_completed(future_to_frame):
#                 result = future.result()
                
#                 valid_candidate = (
#                     result.get("success", False) and 
#                     result.get("has_face", False) and 
#                     result.get("meets_coverage", False) and 
#                     not result.get("is_blurry", False)
#                 )
                
#                 if params['include_emotions']:
#                     valid_candidate = valid_candidate and result.get("emotion_match", False)
                
#                 if valid_candidate:
#                     thumbnails.append(result)
#                     thumbnails.sort(key=lambda x: (x["face_coverage"], x["blur_score"]), reverse=True)
#                     thumbnails = thumbnails[:params['num_thumbnails']]
        
#         # Prepare response data
#         response_data = {
#             "success": True,
#             "video_title": video_title,
#             "original_thumbnail": download_result.get("thumbnail", ""),
#             "thumbnails": [],
#             "stats": {
#                 "total_frames": len(frames),
#                 "blurry_frames": sum(1 for t in thumbnails if t.get("is_blurry", False)),
#                 "frames_with_faces": sum(1 for t in thumbnails if t.get("has_face", False)),
#                 "frames_with_matching_emotions": sum(1 for t in thumbnails if t.get("emotion_match", False))
#             }
#         }
        
#         # Save thumbnails to media storage
#         user_dir = request.user_email.replace("@", "_at_").replace(".", "_")  # sanitize
#         save_dir = os.path.join(settings.MEDIA_ROOT, params['save_location'], user_dir)
#         os.makedirs(save_dir, exist_ok=True)
        
#         for i, thumb in enumerate(thumbnails):
#             # Generate clean filename
#             timestamp_str = format_time(thumb['timestamp']).replace(":", "_")
#             clean_title = "".join([c for c in video_title if c.isalnum() or c in (' ', '_')]).strip().replace(" ", "_")
#             base_filename = f"{clean_title}_{thumb['dominant_emotion'].replace(' ', '_')}_{timestamp_str}"
            
#             # Save original thumbnail
#             original_filename = f"{base_filename}.{params['save_format']}"
#             original_path = os.path.join(save_dir, original_filename)
#             cv2.imwrite(original_path, cv2.cvtColor(thumb["frame"], cv2.COLOR_RGB2BGR))
            
#             # Save enhanced thumbnail if enabled
#             enhanced_filename = None
#             enhanced_path = None
#             if params['enable_enhancement']:
#                 enhanced_frame = enhance_image(thumb["frame"])
#                 enhanced_filename = f"{base_filename}_enhanced.{params['save_format']}"
#                 enhanced_path = os.path.join(save_dir, enhanced_filename)
#                 cv2.imwrite(enhanced_path, cv2.cvtColor(enhanced_frame, cv2.COLOR_RGB2BGR))
            
#             response_data["thumbnails"].append({
#                 "timestamp": thumb['timestamp'],
#                 "formatted_time": format_time(thumb['timestamp']),
#                 "dominant_emotion": thumb['dominant_emotion'],
#                 "face_coverage": thumb['face_coverage'],
#                 "blur_score": thumb['blur_score'],
#                 "original": {
#                     "filename": original_filename,
#                     "path": original_path,
#                     "url": f"{settings.MEDIA_URL}{params['save_location']}/{user_dir}/{original_filename}"
#                 },
#                 "enhanced": {
#                     "filename": enhanced_filename,
#                     "path": enhanced_path,
#                     "url": f"{settings.MEDIA_URL}{params['save_location']}/{user_dir}/{enhanced_filename}" if enhanced_filename else None
#                 } if params['enable_enhancement'] else None
#             })

#         logger.info(f"Generated {len(thumbnails)} thumbnails for {request.user_email}, video: {youtube_url}, saved to: {save_dir}")    
        
#         # Clean up video file only if it's not a local file
#         if not is_local and os.path.exists(video_path):
#             try:
#                 os.remove(video_path)
#                 logger.info(f"Deleted temporary video file: {video_path}")
#             except Exception as e:
#                 logger.error(f"Failed to delete temporary video file {video_path}: {str(e)}")
#                 print(f"Failed to delete temporary video file {video_path}: {str(e)}")
        
#         return Response(response_data, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         logger.error(f"Thumbnail generation error for {request.user_email}, video: {youtube_url}: {str(e)}")
#         return Response(
#             {"error": f"An error occurred: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


@token_required
@api_view(['POST'])
def enhance_thumbnails(request):
    if request.method == 'POST':
        thumbnails = request.data.get('thumbnails')
        if not thumbnails:
            logger.error(f"No thumbnails data provided for {request.user_email}")
            return Response(
                {"error": "Thumbnails data is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enhancement_params = {
            'stability': request.data.get('stability', 25),
            'scale': request.data.get('scale', 2.0),
            'hdr': request.data.get('hdr', True),
            'beautify': request.data.get('beautify', True),
            'brightness': request.data.get('brightness', 50),
            'contrast': request.data.get('contrast', 50),
            'saturation': request.data.get('saturation', 50),
            'hue': request.data.get('hue', 0),
            'aspect_ratio': request.data.get('aspect_ratio', "Original"),
            'text': request.data.get('text', None),
            'language': request.data.get('language', "English"),
            'font_position': request.data.get('font_position', "Center"),
            'font_size': request.data.get('font_size', 30),
            'font_path': request.data.get('font_path', None),
            'logo_file': request.FILES.get('logo_file', None),
            'logo_position': request.data.get('logo_position', "Top-Left"),
            'blur_regions': request.data.get('blur_regions', []),
            'compress': request.data.get('compress', False),
            'quality': request.data.get('quality', 70)
        }
        
        logger.info(f"Enhancing thumbnails for {request.user_email}, params: {enhancement_params}")
        enhanced_thumbnails = []
        
        for thumbnail_data in thumbnails:
            # Initialize thumbnail object
            thumbnail = {
                "frame": None,
                "timestamp": thumbnail_data.get("timestamp"),
                "dominant_emotion": thumbnail_data.get("dominant_emotion", "neutral"),
                "face_location": thumbnail_data.get("face_location", None),
                "original_path": None,
                "original_url": None
            }
            
            # Get original file info if available
            if 'original' in thumbnail_data:
                thumbnail["original_path"] = thumbnail_data['original'].get('path')
                thumbnail["original_url"] = thumbnail_data['original'].get('url')
            
            # Case 1: URL provided (from generate API response)
            if 'url' in thumbnail_data:
                try:
                    # Build absolute URL if needed
                    url = thumbnail_data['url']
                    if not url.startswith(('http://', 'https://')):
                        url = request.build_absolute_uri(url)
                    
                    # Download image from URL
                    response = requests.get(url)
                    response.raise_for_status()
                    img = Image.open(BytesIO(response.content))
                    thumbnail["frame"] = np.array(img)
                    logger.info(f"Loaded thumbnail for {request.user_email}: {url}")
                except Exception as e:
                    logger.error(f"Error loading thumbnail {url} for {request.user_email}: {str(e)}")
                    print(f"Error loading image from URL {url}: {str(e)}")
                    continue
            
            # Case 2: Base64 image_data provided
            elif 'image_data' in thumbnail_data:
                try:
                    img_byte_arr = BytesIO(thumbnail_data['image_data'].encode('latin1'))
                    img = Image.open(img_byte_arr)
                    thumbnail["frame"] = np.array(img)
                    logger.info(f"Loaded base64 thumbnail for {request.user_email}")
                except Exception as e:
                    logger.error(f"Error decoding base64 thumbnail for {request.user_email}: {str(e)}")
                    print(f"Error decoding base64 image data: {str(e)}")
                    continue
            
            # Case 3: Original file path provided
            elif thumbnail["original_path"]:
                try:
                    img = Image.open(thumbnail["original_path"])
                    thumbnail["frame"] = np.array(img)
                    logger.info(f"Loaded thumbnail from path for {request.user_email}: {thumbnail['original_path']}")
                except Exception as e:
                    logger.error(f"Error loading thumbnail from path {thumbnail['original_path']} for {request.user_email}: {str(e)}")
                    print(f"Error loading image from path {thumbnail['original_path']}: {str(e)}")
                    continue
            
            else:
                logger.warning(f"No valid image source for thumbnail for {request.user_email}")
                print("No valid image source found in thumbnail data")
                continue
            
            # Enhance the image if we successfully loaded it
            if thumbnail["frame"] is not None:
                try:
                    enhanced = enhance_thumbnail(thumbnail, enhancement_params)
                    enhanced_img = Image.fromarray(enhanced["enhanced"])
                    
                    # Save to original location if path exists
                    if thumbnail["original_path"]:
                        # Determine format from original filename
                        file_ext = os.path.splitext(thumbnail["original_path"])[1].lower().replace('.', '')
                        if file_ext not in ['jpg', 'jpeg', 'png']:
                            file_ext = 'jpg' if enhancement_params['compress'] else 'png'
                        
                        # Save the enhanced image (overwrite original)
                        try:
                            format_map = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG'}
                            pil_format = format_map.get(file_ext, 'JPEG')
                            enhanced_img.save(thumbnail["original_path"], format=pil_format, quality=enhancement_params['quality'])
                            logger.info(f"Saved enhanced thumbnail for {request.user_email}: {thumbnail['original_path']}")
                            print(f"Saved enhanced image to: {thumbnail['original_path']}")
                        except Exception as e:
                            print(f"Error enhancing thumbnail: {str(e)}")
                            continue
                        
                        enhanced_thumbnails.append({
                            "timestamp": enhanced["timestamp"],
                            "formatted_time": format_time(enhanced["timestamp"]),
                            "url": thumbnail["original_url"],
                            "width": enhanced_img.width,
                            "height": enhanced_img.height,
                            "format": file_ext if thumbnail["original_path"] else ('jpg' if enhancement_params['compress'] else 'png'),
                            "dominant_emotion": enhanced.get("dominant_emotion", "unknown"),
                            "file_path": thumbnail["original_path"]
                        })
                    
                except Exception as e:
                    logger.error(f"Error enhancing thumbnail for {request.user_email}: {str(e)}")
                    print(f"Error enhancing thumbnail: {str(e)}")
                    continue
        
        logger.info(f"Enhanced {len(enhanced_thumbnails)} thumbnails for {request.user_email}")
        return Response({
            "success": True,
            "enhanced_thumbnails": enhanced_thumbnails,
            "count": len(enhanced_thumbnails)
        })
    
    logger.error(f"Invalid method for enhance_thumbnails for {request.user_email}")
    return Response({"error": "Only POST method is allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@token_required
def logout_view(request):
    """
    API endpoint to log out a user, invalidate their token, and delete their thumbnail folder.
    
    Requires Authorization header with Bearer token.
    
    Example request:
    - Headers: Authorization: Bearer <token>
    - Body: {}
    
    Returns:
    - Success: {"message": "Logout successful, thumbnails deleted"}
    - Error: {"error": "Failed to delete thumbnail folder"} or {"error": "Unauthorized"}
    """
    try:
        # Get user email from token_required decorator
        user_email = request.user_email
        
        # Invalidate token
        if user_email in VALID_TOKENS:
            del VALID_TOKENS[user_email]
            logger.info(f"User {user_email} logged out, token invalidated")
        else:
            logger.warning(f"Logout attempt for {user_email} - No active session found")
            return Response({"error": "No active session found"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete user's thumbnail folder
        user_dir = user_email.replace("@", "_at_").replace(".", "_")  # Sanitize email
        thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails', user_dir)
        
        if os.path.exists(thumbnail_dir):
            try:
                shutil.rmtree(thumbnail_dir)
                print(f"Deleted thumbnail folder: {thumbnail_dir}")
                logger.info(f"Deleted thumbnail folder for {user_email}: {thumbnail_dir}")
            except Exception as e:
                logger.error(f"Failed to delete thumbnail folder for {user_email}: {str(e)}")
                print(f"Failed to delete thumbnail folder {thumbnail_dir}: {str(e)}")
                return Response(
                    {"error": f"Failed to delete thumbnail folder: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(
            {"message": "Logout successful, thumbnails deleted"},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.error(f"Logout error for {user_email}: {str(e)}")
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )        
    
logger = logging.getLogger('upscale')

# Set environment variables
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# MODEL_PATH = r'C:\Users\santoshj\Desktop\upscaler\RealESRGAN_x4plus.pth'
MODEL_PATH = 'RealESRGAN_x4plus.pth'



def load_model():
    try:
        logger.info("Loading Real-ESRGAN model")
        model = RRDBNet(num_in_ch=3, num_out_ch=3)
        upsampler = RealESRGANer(
            scale=4,
            model_path=MODEL_PATH,
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=False,
            device=torch.device('cpu')
        )
        logger.info("Model loaded successfully")
        return upsampler
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        return None

# upsacle api is working fine for single image
# @token_required
# @api_view(['POST'])
# @parser_classes([MultiPartParser])
# def upscale_image(request):
#     logger.info(f"Received upscale request from user: {request.user}")
#     # parser_classes = [MultiPartParser]

#     image_file = request.FILES.get('image')
#     if not image_file:
#         logger.warning("No image uploaded in request")
#         return Response({'error': 'No image uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         logger.info(f"Processing image: {image_file.name}")
#         # Convert uploaded image to numpy array
#         image = Image.open(image_file).convert('RGB')
#         image_np = np.array(image)

#         # Load and run Real-ESRGAN model
#         upsampler = load_model()
#         if upsampler is None:
#             logger.error("Model loading failed")
#             return Response({'error': 'Failed to load model'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#         logger.info("Enhancing image with Real-ESRGAN")
#         output, _ = upsampler.enhance(image_np)

#         # Convert output to PNG byte stream
#         _, buffer = cv2.imencode('.png', cv2.cvtColor(output, cv2.COLOR_RGB2BGR))
#         logger.info("Image upscaled successfully")
#         # return HttpResponse(buffer.tobytes(), content_type='image/png')
#         response = HttpResponse(buffer.tobytes(), content_type='image/png')
#         response['Content-Disposition'] = 'attachment; filename="upscaled_image.jpg"'
#         return response


#     except Exception as e:
#         logger.error(f"Error upscaling image {image_file.name}: {str(e)}", exc_info=True)
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @token_required
# @api_view(['POST'])
# def upscale_image(request):
#     """API to upscale a server-side thumbnail using Real-ESRGAN."""
#     logger.info(f"Received upscale request from user: {request.user}")
 
#     # Get thumbnail_url from request
#     thumbnail_url = request.POST.get('thumbnail_url')
#     if not thumbnail_url:
#         logger.warning("No thumbnail_url provided in request")
#         return Response({'error': 'No thumbnail_url provided.'}, status=status.HTTP_400_BAD_REQUEST)
 
#     try:
#         # Construct full file path from thumbnail_url
#         # Remove MEDIA_URL prefix (e.g., '/media/') to get relative path
#         relative_path = thumbnail_url.lstrip(settings.MEDIA_URL)
#         image_path = os.path.join(settings.MEDIA_ROOT, relative_path)
 
#         # Validate file existence
#         if not os.path.exists(image_path):
#             logger.warning(f"Thumbnail not found at {image_path}")
#             return Response({'error': 'Thumbnail not found.'}, status=status.HTTP_404_NOT_FOUND)
 
#         logger.info(f"Processing image: {relative_path}")
#         # Load image
#         image = Image.open(image_path).convert('RGB')
#         image_np = np.array(image)
 
#         # Load and run Real-ESRGAN model
#         upsampler = load_model()
#         if upsampler is None:
#             logger.error("Model loading failed")
#             return Response({'error': 'Failed to load model'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
#         logger.info("Enhancing image with Real-ESRGAN")
#         output, _ = upsampler.enhance(image_np)
 
#         # Convert output to PNG byte stream
#         _, buffer = cv2.imencode('.png', cv2.cvtColor(output, cv2.COLOR_RGB2BGR))
#         logger.info("Image upscaled successfully")
#         response = HttpResponse(buffer.tobytes(), content_type='image/png')
#         response['Content-Disposition'] = 'attachment; filename="upscaled_image.jpg"'
#         return response
 
#     except Exception as e:
#         logger.error(f"Error upscaling image {relative_path}: {str(e)}", exc_info=True)
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Added by Arun, this API function will work for both edited images and server-side thumbnails
@token_required
@api_view(['POST'])
def upscale_image(request):
    """API to upscale either a server-side thumbnail or uploaded image using Real-ESRGAN."""
    logger.info(f"Received upscale request from user: {request.user}")
    
    image = None
    source_type = None
    
    # Case 1: Handle direct image upload (for edited images)
    if 'image' in request.FILES:
        try:
            image = Image.open(request.FILES['image']).convert('RGB')
            source_type = 'upload'
            logger.info("Processing uploaded image")
        except Exception as e:
            logger.error(f"Error processing uploaded image: {str(e)}")
            return Response({'error': 'Invalid image upload'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Case 2: Handle thumbnail URL (original behavior)
    elif 'thumbnail_url' in request.POST:
        thumbnail_url = request.POST.get('thumbnail_url')
        if not thumbnail_url:
            logger.warning("No thumbnail_url provided in request")
            return Response({'error': 'No thumbnail_url provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Construct full file path from thumbnail_url
            relative_path = thumbnail_url.lstrip(settings.MEDIA_URL)
            image_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            
            if not os.path.exists(image_path):
                logger.warning(f"Thumbnail not found at {image_path}")
                return Response({'error': 'Thumbnail not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            image = Image.open(image_path).convert('RGB')
            source_type = 'thumbnail_url'
            logger.info(f"Processing thumbnail: {relative_path}")
        except Exception as e:
            logger.error(f"Error processing thumbnail URL: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        return Response({'error': 'Either image file or thumbnail_url must be provided'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    # Common processing for both cases
    try:
        image_np = np.array(image)
        
        # Load and run Real-ESRGAN model
        upsampler = load_model()
        if upsampler is None:
            logger.error("Model loading failed")
            return Response({'error': 'Failed to load model'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"Enhancing {source_type} image with Real-ESRGAN")
        output, _ = upsampler.enhance(image_np)
        
        # Convert output to PNG byte stream
        _, buffer = cv2.imencode('.png', cv2.cvtColor(output, cv2.COLOR_RGB2BGR))
        logger.info("Image upscaled successfully")
        response = HttpResponse(buffer.tobytes(), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="upscaled_{source_type}_image.jpg"'
        return response
    
    except Exception as e:
        logger.error(f"Error upscaling image: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# upsacle api for Multiple  images
@token_required
@api_view(['POST'])
def upscale_images(request):
    logger.info(f"Received multiple upscale request from user: {request.user}")

    if request.method == 'POST':
        images = request.FILES.getlist('images')
        if not images:
            logger.warning("No images provided in request")
            return JsonResponse({'error': 'No images provided'}, status=400)

        logger.info(f"Processing {len(images)} images")
        upsampler = load_model()
        if upsampler is None:
            logger.error("Model loading failed")
            return JsonResponse({'error': 'Failed to load model'}, status=500)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for index, image_file in enumerate(images):
                logger.info(f"Processing image {index + 1}: {image_file.name}")

                try:
                    img = Image.open(image_file).convert("RGB")
                    image_np = np.array(img)

                
                    output, _ = upsampler.enhance(image_np)
                    output_img = Image.fromarray(output)

                    img_byte_arr = io.BytesIO()
                    output_img.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)  # ✅ Seek before writing to ZIP

                    zip_file.writestr(f'upscaled_image_{index + 1}.png', img_byte_arr.read())
                    logger.info(f"Image {image_file.name} upscaled and added to ZIP")
                except Exception as e:
                    logger.error(f"Error upscaling image {image_file.name}: {str(e)}", exc_info=True)
                    return JsonResponse({'error': f'Upscaling failed: {str(e)}'}, status=500)

        zip_buffer.seek(0)
        logger.info("ZIP file created successfully")
        response = HttpResponse(zip_buffer.read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="upscaled_images.zip"'
        return response




# Initialize logger
logger = logging.getLogger('upscale')

def apply_hdr(image_np):
    """Apply HDR effect using histogram equalization."""
    try:
        # Convert to YCrCb color space for luminance-based processing
        ycrcb = cv2.cvtColor(image_np, cv2.COLOR_RGB2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        # Apply histogram equalization to the Y channel (luminance)
        y_eq = cv2.equalizeHist(y)
        # Merge back and convert to RGB
        ycrcb_eq = cv2.merge([y_eq, cr, cb])
        result = cv2.cvtColor(ycrcb_eq, cv2.COLOR_YCrCb2RGB)
        return result
    except Exception as e:
        logger.error(f"HDR processing failed: {str(e)}", exc_info=True)
        raise

def apply_beautify(image_np):
    """Apply Beautify effect with smoothing and color enhancement."""
    try:
        # Apply bilateral filter for smoothing while preserving edges
        smoothed = cv2.bilateralFilter(image_np, d=9, sigmaColor=75, sigmaSpace=75)
        # Convert to HSV for color enhancement
        hsv = cv2.cvtColor(smoothed, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        # Increase saturation for vibrance
        s = np.clip(s * 1.2, 0, 255).astype(np.uint8)
        # Merge and convert back to RGB
        hsv_enhanced = cv2.merge([h, s, v])
        result = cv2.cvtColor(hsv_enhanced, cv2.COLOR_HSV2RGB)
        return result
    except Exception as e:
        logger.error(f"Beautify processing failed: {str(e)}", exc_info=True)
        raise

@token_required
@api_view(['POST'])
def enhance_thumbnailhdr(request):
    """API to apply HDR and Beautify effects to a server-side thumbnail."""
    logger.info(f"Received thumbnail enhancement request from user: {request.user}")

    # Get parameters
    thumbnail_url = request.POST.get('thumbnail_url')
    hdr = request.POST.get('hdr', 'false').lower() == 'true'
    beautify = request.POST.get('beautify', 'false').lower() == 'true'

    if not thumbnail_url:
        logger.warning("No thumbnail_url provided in request")
        return Response({'error': 'No thumbnail_url provided.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Construct full file path from thumbnail_url
        # Remove MEDIA_URL prefix (e.g., '/media/') to get relative path
        relative_path = thumbnail_url.lstrip(settings.MEDIA_URL)
        image_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        # Validate file existence
        if not os.path.exists(image_path):
            logger.warning(f"Thumbnail not found at {image_path}")
            return Response({'error': 'Thumbnail not found.'}, status=status.HTTP_404_NOT_FOUND)

        logger.info(f"Processing thumbnail: {relative_path}, HDR: {hdr}, Beautify: {beautify}")
        # Load image
        image = Image.open(image_path).convert('RGB')
        image_np = np.array(image)

        # Apply HDR if selected
        if hdr:
            logger.info("Applying HDR effect")
            image_np = apply_hdr(image_np)

        # Apply Beautify if selected
        if beautify:
            logger.info("Applying Beautify effect")
            image_np = apply_beautify(image_np)

        # Convert output to PNG byte stream
        _, buffer = cv2.imencode('.png', cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))
        logger.info("Thumbnail enhancement completed successfully")
        return HttpResponse(buffer.tobytes(), content_type='image/png')

    except Exception as e:
        logger.error(f"Error enhancing thumbnail {thumbnail_url}: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#========================================================================


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import ThumbnailRequestSerializer
from .utils import download_youtube_video, extract_frames, load_face_detector, prepare_frame_data, process_frame, enhance_image, format_time
import concurrent.futures
import os
import logging
from django.conf import settings
import cv2
import numpy as np
import tempfile
import uuid

logger = logging.getLogger(__name__)

# # Assuming token_required is defined elsewhere
# def token_required(view_func):
#     return view_func

@token_required
@api_view(['POST'])
def generate_thumbnails_api(request):
    """
    API endpoint to generate thumbnails from a YouTube video, local file path, or uploaded video file
    
    Example POST data:
    {
        "youtube_url": "https://www.youtube.com/watch?v=example" or "C:\\Users\\santoshj\\Desktop\\vi\\videoplayback.mp4",
        "video_file": <uploaded_file>,
        "face_threshold": 0.5,
        "face_coverage": 20,
        "num_thumbnails": 5,
        "include_emotions": true,
        "selected_emotions": ["happy", "surprise"],
        "frame_interval": 2,
        "max_workers": 4,
        "blur_threshold": 100,
        "enable_stabilization": true,
        "enable_enhancement": true,
        "enable_autosave": false,
        "save_location": "thumbnails",
        "save_format": "jpg"
    }
    """
    serializer = ThumbnailRequestSerializer(data=request.data)
    if not serializer.is_valid():
        logger.error(f"Invalid request data for {request.user_email}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        params = serializer.validated_data
        youtube_url = params.get('youtube_url', '')
        video_file = params.get('video_file')
        temp_file_path = None
        is_uploaded = False

        # Handle uploaded video file
        if video_file:
            # Save uploaded file to a temporary location
            temp_dir = tempfile.mkdtemp()
            temp_filename = f"uploaded_{uuid.uuid4().hex}.mp4"
            temp_file_path = os.path.join(temp_dir, temp_filename)
            with open(temp_file_path, 'wb') as f:
                for chunk in video_file.chunks():
                    f.write(chunk)
            youtube_url = temp_file_path  # Treat uploaded file as a local file path
            is_uploaded = True
            logger.info(f"Processing uploaded video file for {request.user_email}")
        
        logger.info(f"Generating thumbnails for {request.user_email}, video: {youtube_url}")
        
        # Download video or get local file path
        download_result = download_youtube_video(youtube_url)
        if not download_result["success"]:
            logger.error(f"Video processing failed for {request.user_email}, video: {youtube_url}, error: {download_result['error']}")
            return Response(
                {"error": download_result["error"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        video_path = download_result["video_path"]
        video_title = download_result["title"]
        is_local = download_result.get("is_local", False) or is_uploaded
        
        # Extract frames
        extraction_result = extract_frames(video_path, interval_secs=params['frame_interval'])
        if not extraction_result["success"]:
            logger.error(f"Frame extraction failed for {request.user_email}, video: {youtube_url}, error: {extraction_result['error']}")
            return Response(
                {"error": extraction_result["error"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        frames = extraction_result["frames"]
        timestamps = extraction_result["timestamps"]
        
        # Initialize detectors
        face_cascade = load_face_detector()
        
        # Prepare data for parallel processing
        frame_data = prepare_frame_data(
            frames, timestamps, 
            params['face_threshold'], params['face_coverage'], 
            params['selected_emotions'], 
            face_cascade, params['include_emotions'], 
            params['blur_threshold'], params['enable_stabilization'], 
            params['enable_enhancement']
        )
        
        # Process frames in parallel
        thumbnails = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=params['max_workers']) as executor:
            future_to_frame = {executor.submit(process_frame, fd): idx for idx, fd in enumerate(frame_data)}
            
            for future in concurrent.futures.as_completed(future_to_frame):
                result = future.result()
                
                valid_candidate = (
                    result.get("success", False) and 
                    result.get("has_face", False) and 
                    result.get("meets_coverage", False) and 
                    not result.get("is_blurry", False)
                )
                
                if params['include_emotions']:
                    valid_candidate = valid_candidate and result.get("emotion_match", False)
                
                if valid_candidate:
                    thumbnails.append(result)
                    thumbnails.sort(key=lambda x: (x["face_coverage"], x["blur_score"]), reverse=True)
                    thumbnails = thumbnails[:params['num_thumbnails']]
        
        # Prepare response data
        response_data = {
            "success": True,
            "video_title": video_title,
            "original_thumbnail": download_result.get("thumbnail", ""),
            "thumbnails": [],
            "stats": {
                "total_frames": len(frames),
                "blurry_frames": sum(1 for t in thumbnails if t.get("is_blurry", False)),
                "frames_with_faces": sum(1 for t in thumbnails if t.get("has_face", False)),
                "frames_with_matching_emotions": sum(1 for t in thumbnails if t.get("emotion_match", False))
            }
        }
        
        # Save thumbnails to media storage
        user_dir = request.user_email.replace("@", "_at_").replace(".", "_")  # sanitize
        save_dir = os.path.join(settings.MEDIA_ROOT, params['save_location'], user_dir)
        os.makedirs(save_dir, exist_ok=True)
        
        for i, thumb in enumerate(thumbnails):
            # Generate clean filename
            timestamp_str = format_time(thumb['timestamp']).replace(":", "_")
            clean_title = "".join([c for c in video_title if c.isalnum() or c in (' ', '_')]).strip().replace(" ", "_")
            base_filename = f"{clean_title}_{thumb['dominant_emotion'].replace(' ', '_')}_{timestamp_str}"
            
            # Save original thumbnail
            original_filename = f"{base_filename}.{params['save_format']}"
            original_path = os.path.join(save_dir, original_filename)
            cv2.imwrite(original_path, cv2.cvtColor(thumb["frame"], cv2.COLOR_RGB2BGR))
            
            # Save enhanced thumbnail if enabled
            enhanced_filename = None
            enhanced_path = None
            if params['enable_enhancement']:
                enhanced_frame = enhance_image(thumb["frame"])
                enhanced_filename = f"{base_filename}_enhanced.{params['save_format']}"
                enhanced_path = os.path.join(save_dir, enhanced_filename)
                cv2.imwrite(enhanced_path, cv2.cvtColor(enhanced_frame, cv2.COLOR_RGB2BGR))
            
            response_data["thumbnails"].append({
                "timestamp": thumb['timestamp'],
                "formatted_time": format_time(thumb['timestamp']),
                "dominant_emotion": thumb['dominant_emotion'],
                "face_coverage": thumb['face_coverage'],
                "blur_score": thumb['blur_score'],
                "original": {
                    "filename": original_filename,
                    "path": original_path,
                    "url": f"{settings.MEDIA_URL}{params['save_location']}/{user_dir}/{original_filename}"
                },
                "enhanced": {
                    "filename": enhanced_filename,
                    "path": enhanced_path,
                    "url": f"{settings.MEDIA_URL}{params['save_location']}/{user_dir}/{enhanced_filename}" if enhanced_filename else None
                } if params['enable_enhancement'] else None
            })

        logger.info(f"Generated {len(thumbnails)} thumbnails for {request.user_email}, video: {youtube_url or 'uploaded file'}, saved to: {save_dir}")    
        
        # Clean up video file only if it's not a local file or uploaded file
        if not is_local and os.path.exists(video_path):
            try:
                os.remove(video_path)
                logger.info(f"Deleted temporary video file: {video_path}")
            except Exception as e:
                logger.error(f"Failed to delete temporary video file {video_path}: {str(e)}")
                print(f"Failed to delete temporary video file {video_path}: {str(e)}")
        
        # Clean up uploaded file if it exists
        if is_uploaded and temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"Deleted temporary uploaded file: {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to delete temporary uploaded file {temp_file_path}: {str(e)}")
                print(f"Failed to delete temporary uploaded file {temp_file_path}: {str(e)}")
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Thumbnail generation error for {request.user_email}, video: {youtube_url or 'uploaded file'}: {str(e)}")
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    