import mongoengine as me
from datetime import datetime

class DocumentChunk(me.Document):
    document_name = me.StringField(required=True, max_length=255)
    chunk_index = me.IntField(required=True)
    page_number = me.IntField()
    section = me.StringField(max_length=100)
    content = me.StringField(required=True)
    created_at = me.DateTimeField(default=datetime.utcnow)
    updated_at = me.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'document_chunks',
        'ordering': ['document_name', 'chunk_index'],
        'indexes': [
            {'fields': ('document_name', 'chunk_index'), 'unique': True},
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(DocumentChunk, self).save(*args, **kwargs)
