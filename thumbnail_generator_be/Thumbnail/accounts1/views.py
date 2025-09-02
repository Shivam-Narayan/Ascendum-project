import os
import tempfile
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import numpy as np
from PIL import Image
from io import BytesIO
from .utils import (
    generate_thumbnails_from_video,
    enhance_thumbnail,
    compress_image,
    format_time,
    enhance_image
)
from django.conf import settings
import cv2
import requests
from accounts.views import token_required


@token_required
@csrf_exempt
@api_view(['POST'])
def generate_thumbnails(request):
    if request.method == 'POST':
        youtube_url = request.data.get('youtube_url')
        if not youtube_url:
            return Response(
                {"error": "YouTube URL is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        params = {
            'face_threshold': request.data.get('face_threshold', 0.5),
            'face_coverage': request.data.get('face_coverage', 3),
            'num_thumbnails': request.data.get('num_thumbnails', 5),
            'include_emotions': request.data.get('include_emotions', True),
            'selected_emotions': request.data.get('selected_emotions', ["happy", "surprise"]),
            'frame_interval': request.data.get('frame_interval', 2),
            'max_workers': request.data.get('max_workers', 4),
            'blur_threshold': request.data.get('blur_threshold', 30),
            'enable_stabilization': request.data.get('enable_stabilization', True),
            'enable_enhancement': request.data.get('enable_enhancement', True),
            'enable_autosave': request.data.get('enable_autosave', False),
            'save_location': request.data.get('save_location', 'thumbnails'),
            'save_format': request.data.get('save_format', 'jpg')
        }
        
        result = generate_thumbnails_from_video(youtube_url, params)
        
        if not result["success"]:
            return Response(
                {"error": result["error"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare response data structure
        response_data = {
            "success": True,
            "video_title": result["video_title"],
            "original_thumbnail": result.get("thumbnail", ""),
            "thumbnails": [],
            "stats": {
                "total_frames": len(result.get("frames", [])),
                "blurry_frames": 0,
                "frames_with_faces": 0,
                "frames_with_matching_emotions": 0
            }
        }

        # Save thumbnails to media storage
        save_dir = os.path.join(settings.MEDIA_ROOT, params['save_location'])
        os.makedirs(save_dir, exist_ok=True)

        # Process thumbnails
        for thumb in result["thumbnails"]:
            # Update stats
            if thumb.get("is_blurry", False):
                response_data["stats"]["blurry_frames"] += 1
            if thumb.get("has_face", False):
                response_data["stats"]["frames_with_faces"] += 1
            if thumb.get("emotion_match", False):
                response_data["stats"]["frames_with_matching_emotions"] += 1

            # Generate clean filename
            timestamp_str = format_time(thumb['timestamp']).replace(":", "_")
            clean_title = "".join([c for c in result["video_title"] if c.isalnum() or c in (' ', '_')]).strip().replace(" ", "_")
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
            
            # Add to response
            response_data["thumbnails"].append({
                "timestamp": thumb['timestamp'],
                "formatted_time": format_time(thumb['timestamp']),
                "dominant_emotion": thumb['dominant_emotion'],
                "face_coverage": thumb['face_coverage'],
                "blur_score": thumb['blur_score'],
                "original": {
                    "filename": original_filename,
                    "path": original_path,
                    "url": f"{settings.MEDIA_URL}{params['save_location']}/{original_filename}"
                },
                "enhanced": {
                    "filename": enhanced_filename,
                    "path": enhanced_path,
                    "url": f"{settings.MEDIA_URL}{params['save_location']}/{enhanced_filename}" if enhanced_filename else None
                } if params['enable_enhancement'] else None
            })
        
        return Response(response_data, status=status.HTTP_200_OK)



@token_required
@csrf_exempt
@api_view(['POST'])
def enhance_thumbnails(request):
    if request.method == 'POST':
        thumbnails = request.data.get('thumbnails')
        if not thumbnails:
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
                except Exception as e:
                    print(f"Error loading image from URL {url}: {str(e)}")
                    continue
            
            # Case 2: Base64 image_data provided
            elif 'image_data' in thumbnail_data:
                try:
                    img_byte_arr = BytesIO(thumbnail_data['image_data'].encode('latin1'))
                    img = Image.open(img_byte_arr)
                    thumbnail["frame"] = np.array(img)
                except Exception as e:
                    print(f"Error decoding base64 image data: {str(e)}")
                    continue
            
            # Case 3: Original file path provided
            elif thumbnail["original_path"]:
                try:
                    img = Image.open(thumbnail["original_path"])
                    thumbnail["frame"] = np.array(img)
                except Exception as e:
                    print(f"Error loading image from path {thumbnail['original_path']}: {str(e)}")
                    continue
            
            else:
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
    # Map file extension to PIL format
                            format_map = {'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG'}
                            pil_format = format_map.get(file_ext, 'JPEG')
                            enhanced_img.save(thumbnail["original_path"], format=pil_format, quality=enhancement_params['quality'])
                            print(f"Saved enhanced image to: {thumbnail['original_path']}")
                        except Exception as e:
                            print(f"Error enhancing thumbnail: {str(e)}")
                            continue
                        print(f"Saved enhanced image to: {thumbnail['original_path']}")
                    
                    enhanced_thumbnails.append({
                        "timestamp": enhanced["timestamp"],
                        "formatted_time": format_time(enhanced["timestamp"]),
                        "url": thumbnail["original_url"],  # Return original URL
                        "width": enhanced_img.width,
                        "height": enhanced_img.height,
                        "format": file_ext if thumbnail["original_path"] else ('jpg' if enhancement_params['compress'] else 'png'),
                        "dominant_emotion": enhanced.get("dominant_emotion", "unknown"),
                        "file_path": thumbnail["original_path"]  # For debugging
                    })
                    
                except Exception as e:
                    print(f"Error enhancing thumbnail: {str(e)}")
                    continue
        
        return Response({
            "success": True,
            "enhanced_thumbnails": enhanced_thumbnails,
            "count": len(enhanced_thumbnails)
        })


@token_required
@csrf_exempt
@api_view(['POST'])
def download_thumbnail(request):
    if request.method == 'POST':
        image_data = request.data.get('image_data')
        if not image_data:
            return Response(
                {"error": "Image data is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        img_byte_arr = BytesIO(image_data.encode('latin1'))
        img = Image.open(img_byte_arr)
        
        format = request.data.get('format', 'JPEG')
        quality = request.data.get('quality', 70)
        
        output = BytesIO()
        if format == 'JPEG':
            img.save(output, format='JPEG', quality=quality)
            content_type = 'image/jpeg'
            file_ext = 'jpg'
        else:
            img.save(output, format='PNG')
            content_type = 'image/png'
            file_ext = 'png'
        
        output.seek(0)
        
        response = FileResponse(output, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="thumbnail.{file_ext}"'
        return response