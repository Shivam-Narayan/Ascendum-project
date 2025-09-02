# from rest_framework import serializers

# class ThumbnailRequestSerializer(serializers.Serializer):
#     youtube_url = serializers.URLField(required=True)
#     face_threshold = serializers.FloatField(default=0.5, min_value=0.0, max_value=1.0)
#     face_coverage = serializers.IntegerField(default=20, min_value=0, max_value=100)
#     num_thumbnails = serializers.IntegerField(default=5, min_value=1, max_value=200)
#     include_emotions = serializers.BooleanField(default=True)
#     selected_emotions = serializers.ListField(
#         child=serializers.CharField(),
#         required=False,
#         default=["happy", "surprise", "angry"]
#     )
#     frame_interval = serializers.IntegerField(default=2, min_value=1, max_value=10)
#     max_workers = serializers.IntegerField(default=4, min_value=1, max_value=8)
#     blur_threshold = serializers.IntegerField(default=100, min_value=10, max_value=200)
#     enable_stabilization = serializers.BooleanField(default=True)
#     enable_enhancement = serializers.BooleanField(default=True)
#     enable_autosave = serializers.BooleanField(default=False)
#     save_location = serializers.CharField(default="thumbnails", required=False)
#     save_format = serializers.ChoiceField(choices=["jpg", "png"], default="jpg")

# from rest_framework import serializers

# class ThumbnailRequestSerializer(serializers.Serializer):
#     youtube_url = serializers.CharField(required=True)
#     face_threshold = serializers.FloatField(default=0.5, min_value=0.0, max_value=1.0)
#     face_coverage = serializers.IntegerField(default=20, min_value=0, max_value=100)
#     num_thumbnails = serializers.IntegerField(default=5, min_value=1, max_value=200)
#     include_emotions = serializers.BooleanField(default=True)
#     selected_emotions = serializers.ListField(
#         child=serializers.CharField(),
#         required=False,
#         default=["happy", "surprise", "angry"]
#     )
#     frame_interval = serializers.IntegerField(default=2, min_value=1, max_value=10)
#     max_workers = serializers.IntegerField(default=4, min_value=1, max_value=8)
#     blur_threshold = serializers.IntegerField(default=100, min_value=10, max_value=200)
#     enable_stabilization = serializers.BooleanField(default=True)
#     enable_enhancement = serializers.BooleanField(default=True)
#     enable_autosave = serializers.BooleanField(default=False)
#     save_location = serializers.CharField(default="thumbnails", required=False)
#     save_format = serializers.ChoiceField(choices=["jpg", "png"], default="jpg")


from rest_framework import serializers

class ThumbnailRequestSerializer(serializers.Serializer):
    youtube_url = serializers.CharField(required=False, allow_blank=True)
    video_file = serializers.FileField(required=False, allow_empty_file=False)
    face_threshold = serializers.FloatField(default=0.5, min_value=0.0, max_value=1.0)
    face_coverage = serializers.IntegerField(default=20, min_value=0, max_value=100)
    num_thumbnails = serializers.IntegerField(default=5, min_value=1, max_value=200)
    include_emotions = serializers.BooleanField(default=True)
    selected_emotions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=["happy", "surprise", "angry"]
    )
    frame_interval = serializers.IntegerField(default=2, min_value=1, max_value=10)
    max_workers = serializers.IntegerField(default=4, min_value=1, max_value=8)
    blur_threshold = serializers.IntegerField(default=100, min_value=10, max_value=200)
    enable_stabilization = serializers.BooleanField(default=True)
    enable_enhancement = serializers.BooleanField(default=True)
    enable_autosave = serializers.BooleanField(default=False)
    save_location = serializers.CharField(default="thumbnails", required=False)
    save_format = serializers.ChoiceField(choices=["jpg", "png"], default="jpg")

    def validate(self, data):
        youtube_url = data.get('youtube_url', '')
        video_file = data.get('video_file')
        if not youtube_url and not video_file:
            raise serializers.ValidationError("Either 'youtube_url' or 'video_file' must be provided.")
        if youtube_url and video_file:
            raise serializers.ValidationError("Provide only one of 'youtube_url' or 'video_file'.")
        return data