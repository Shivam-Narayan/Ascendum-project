from celery import shared_task
from .models import ThumbnailGenerationTask, Thumbnail
from .services import YouTubeThumbnailGenerator
import json
from django.core.files.storage import default_storage

@shared_task(bind=True)
def process_thumbnail_generation_task(self, task_id):
    try:
        task = ThumbnailGenerationTask.objects.get(id=task_id)
        task.status = 'PROCESSING'
        task.save()
        
        generator = YouTubeThumbnailGenerator()
        params = task.parameters
        
        try:
            result = generator.generate_thumbnails(params)
            
            if not result.get('success', False):
                task.status = 'FAILED'
                task.error = result.get('error', 'Unknown error')
                task.save()
                return
            
            # Save thumbnails to database
            for thumb_data in result['thumbnails']:
                thumbnail = Thumbnail(
                    task=task,
                    timestamp=thumb_data['timestamp'],
                    formatted_time=thumb_data['formatted_time'],
                    dominant_emotion=thumb_data['dominant_emotion'],
                    face_coverage=thumb_data['face_coverage'],
                    blur_score=thumb_data['blur_score'],
                    emotion_scores=thumb_data['emotion_scores']
                )
                
                if thumb_data['original_image']:
                    with default_storage.open(thumb_data['original_image'], 'rb') as f:
                        thumbnail.original_image.save(thumb_data['original_image'], f, save=False)
                
                if thumb_data['enhanced_image']:
                    with default_storage.open(thumb_data['enhanced_image'], 'rb') as f:
                        thumbnail.enhanced_image.save(thumb_data['enhanced_image'], f, save=False)
                
                thumbnail.save()
            
            task.status = 'COMPLETED'
            task.result = {
                'video_title': result['video_title'],
                'video_thumbnail': result['video_thumbnail'],
                'total_duration': result['total_duration'],
                'total_frames': result['total_frames'],
                'stats': result['stats'],
                'thumbnail_count': len(result['thumbnails'])
            }
            task.save()
            
        except Exception as e:
            task.status = 'FAILED'
            task.error = str(e)
            task.save()
            raise
    
    except ThumbnailGenerationTask.DoesNotExist:
        # Task doesn't exist - nothing to do
        pass
    except Exception as e:
        # Handle any other unexpected errors
        if task:
            task.status = 'FAILED'
            task.error = str(e)
            task.save()
        raise