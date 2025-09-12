from rest_framework import serializers
from .models import DocumentChunk

class DocumentChunkSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    document_name = serializers.CharField(max_length=255)
    chunk_index = serializers.IntegerField()
    page_number = serializers.IntegerField(required=False, allow_null=True)
    section = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    content = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return DocumentChunk(**validated_data).save()

    def update(self, instance, validated_data):
        instance.document_name = validated_data.get('document_name', instance.document_name)
        instance.chunk_index = validated_data.get('chunk_index', instance.chunk_index)
        instance.page_number = validated_data.get('page_number', instance.page_number)
        instance.section = validated_data.get('section', instance.section)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
