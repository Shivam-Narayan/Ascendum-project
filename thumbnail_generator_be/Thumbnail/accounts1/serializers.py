from rest_framework import serializers
from .models import ThumbnailRequest, GeneratedThumbnail

class ThumbnailRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThumbnailRequest
        fields = '__all__'
        read_only_fields = ('created_at',)

class GeneratedThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedThumbnail
        fields = '__all__'


# from django.db import models

class ThumbnailRequest(models.Model):
    youtube_url = models.URLField(max_length=500)
    face_threshold = models.FloatField(default=0.5)
    face_coverage = models.IntegerField(default=3)
    num_thumbnails = models.IntegerField(default=5)
    include_emotions = models.BooleanField(default=True)
    selected_emotions = models.JSONField(default=list)
    frame_interval = models.IntegerField(default=2)
    max_workers = models.IntegerField(default=4)
    blur_threshold = models.IntegerField(default=30)
    enable_stabilization = models.BooleanField(default=True)
    enable_enhancement = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Request for {self.youtube_url}"

class GeneratedThumbnail(models.Model):
    request = models.ForeignKey(ThumbnailRequest, on_delete=models.CASCADE, related_name='thumbnails')
    image = models.ImageField(upload_to='thumbnails/')
    timestamp = models.FloatField()
    emotion = models.CharField(max_length=20)
    face_coverage = models.FloatField()
    blur_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Thumbnail at {self.timestamp}s"