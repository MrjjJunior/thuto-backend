"""
Django REST Framework Serializers
"""
from rest_framework import serializers
from .models import Subject, Document, Query, Feedback


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model"""
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'display_name', 'description', 'document_count', 'created_at']
    
    def get_document_count(self, obj):
        return obj.documents.filter(processed=True).count()


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_display = serializers.CharField(source='subject.display_name', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'subject', 'subject_name', 'subject_display',
            'file', 'filename', 'file_type', 'uploaded_at',
            'processed', 'processed_at', 'chunk_count'
        ]
        read_only_fields = ['processed', 'processed_at', 'chunk_count', 'file_type']


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload"""
    subject = serializers.CharField()
    file = serializers.FileField()
    
    def validate_subject(self, value):
        """Validate that subject exists"""
        try:
            Subject.objects.get(name=value)
        except Subject.DoesNotExist:
            raise serializers.ValidationError(f"Subject '{value}' does not exist")
        return value
    
    def validate_file(self, value):
        """Validate file type"""
        allowed_extensions = ['.pdf', '.txt', '.docx']
        file_ext = '.' + value.name.split('.')[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Check file size (e.g., max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 10MB")
        
        return value


class QuerySerializer(serializers.ModelSerializer):
    """Serializer for Query model"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = Query
        fields = [
            'id', 'subject', 'subject_name', 'query_text',
            'answer_text', 'context_chunks', 'tokens_used', 'created_at'
        ]
        read_only_fields = ['answer_text', 'context_chunks', 'tokens_used']


class QueryRequestSerializer(serializers.Serializer):
    """Serializer for query request"""
    subject = serializers.CharField()
    query = serializers.CharField()
    k = serializers.IntegerField(default=5, min_value=1, max_value=10)
    temperature = serializers.FloatField(default=0.7, min_value=0.0, max_value=1.0)
    
    def validate_subject(self, value):
        """Validate that subject exists"""
        try:
            Subject.objects.get(name=value)
        except Subject.DoesNotExist:
            raise serializers.ValidationError(f"Subject '{value}' does not exist")
        return value


class QueryResponseSerializer(serializers.Serializer):
    """Serializer for query response"""
    query_id = serializers.IntegerField()
    answer = serializers.CharField()
    sources = serializers.ListField()
    subject = serializers.CharField()
    tokens_used = serializers.IntegerField()
    follow_up_questions = serializers.ListField(required=False)


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for Feedback model"""
    
    class Meta:
        model = Feedback
        fields = ['id', 'query', 'rating', 'comment', 'created_at']


class VectorStoreStatsSerializer(serializers.Serializer):
    """Serializer for vector store statistics"""
    subject = serializers.CharField()
    total_vectors = serializers.IntegerField()
    embedding_dim = serializers.IntegerField()
    total_metadata = serializers.IntegerField()
