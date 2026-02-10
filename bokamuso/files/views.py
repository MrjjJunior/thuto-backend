"""
Django REST Framework Views for RAG System
"""
import os
import logging
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone

from .models import Subject, Document, Query, Feedback
from .serializers import (
    SubjectSerializer, DocumentSerializer, DocumentUploadSerializer,
    QuerySerializer, QueryRequestSerializer, QueryResponseSerializer,
    FeedbackSerializer, VectorStoreStatsSerializer
)

# Import RAG services
import sys
sys.path.append(os.path.join(settings.BASE_DIR, 'services'))

from loader import DocumentLoader
from chunker import DocumentChunker
from embeddings import get_embedding_service
from vectorstore import VectorStoreManager
from retriever import RAGRetriever
from generate import get_claude_generator

logger = logging.getLogger(__name__)

# Initialize RAG components (singleton pattern)
embedding_service = None
vector_store_manager = None
retriever = None
generator = None


def initialize_rag_system():
    """Initialize RAG system components"""
    global embedding_service, vector_store_manager, retriever, generator
    
    if embedding_service is None:
        logger.info("Initializing RAG system...")
        
        # Initialize embedding service
        embedding_service = get_embedding_service()
        
        # Initialize vector store manager
        data_path = os.path.join(settings.BASE_DIR, 'data')
        vector_store_manager = VectorStoreManager(
            base_path=data_path,
            embedding_dim=embedding_service.get_embedding_dimension()
        )
        
        # Initialize retriever
        retriever = RAGRetriever(vector_store_manager, embedding_service)
        
        # Initialize generator
        generator = get_claude_generator()
        
        logger.info("RAG system initialized successfully")


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for subjects"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a subject"""
        subject = self.get_object()
        initialize_rag_system()
        
        # Get vector store stats
        store_stats = vector_store_manager.get_or_create_store(subject.name).get_stats()
        
        # Get document stats
        doc_stats = {
            'total_documents': subject.documents.count(),
            'processed_documents': subject.documents.filter(processed=True).count(),
            'total_chunks': subject.documents.filter(processed=True).aggregate(
                total=models.Sum('chunk_count')
            )['total'] or 0
        }
        
        return Response({
            'subject': subject.name,
            'vector_store': store_stats,
            'documents': doc_stats
        })


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for documents"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [AllowAny]  # Change to IsAuthenticated for production
    
    def get_queryset(self):
        """Filter by subject if provided"""
        queryset = Document.objects.all()
        subject = self.request.query_params.get('subject', None)
        if subject:
            queryset = queryset.filter(subject__name=subject)
        return queryset
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload and process a document"""
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        subject_name = serializer.validated_data['subject']
        uploaded_file = serializer.validated_data['file']
        
        # Get subject
        subject = Subject.objects.get(name=subject_name)
        
        # Save file
        file_ext = '.' + uploaded_file.name.split('.')[-1].lower()
        filename = uploaded_file.name
        
        # Create document record
        document = Document.objects.create(
            subject=subject,
            file=uploaded_file,
            filename=filename,
            file_type=file_ext[1:],
            uploaded_by=request.user if request.user.is_authenticated else None
        )
        
        # Process document asynchronously (or synchronously for now)
        try:
            self._process_document(document)
            return Response({
                'message': 'Document uploaded and processed successfully',
                'document': DocumentSerializer(document).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return Response({
                'error': f'Failed to process document: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _process_document(self, document):
        """Process uploaded document"""
        initialize_rag_system()
        
        # Get file path
        file_path = document.file.path
        
        # Load document
        loader = DocumentLoader()
        doc_data = loader.load_document(file_path, subject=document.subject.name)
        
        # Chunk document
        chunker = DocumentChunker()
        chunks = chunker.chunk_document(doc_data)
        
        # Embed chunks
        chunks_with_embeddings = embedding_service.embed_chunks(chunks)
        
        # Add to vector store
        count = vector_store_manager.add_chunks_to_subject(
            document.subject.name,
            chunks_with_embeddings
        )
        
        # Update document record
        document.processed = True
        document.processed_at = timezone.now()
        document.chunk_count = count
        document.save()
        
        logger.info(f"Processed document {document.filename}: {count} chunks")
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess a document"""
        document = self.get_object()
        
        try:
            # Clear existing chunks (would need to implement in vector store)
            self._process_document(document)
            return Response({
                'message': 'Document reprocessed successfully',
                'document': DocumentSerializer(document).data
            })
        except Exception as e:
            return Response({
                'error': f'Failed to reprocess document: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QueryViewSet(viewsets.ModelViewSet):
    """ViewSet for queries"""
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = [AllowAny]  # Change to IsAuthenticated for production
    
    def get_queryset(self):
        """Filter by user if authenticated"""
        queryset = Query.objects.all()
        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        return queryset
    
    @action(detail=False, methods=['post'])
    def ask(self, request):
        """Ask a question and get RAG-based answer"""
        serializer = QueryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        subject_name = serializer.validated_data['subject']
        query_text = serializer.validated_data['query']
        k = serializer.validated_data['k']
        temperature = serializer.validated_data['temperature']
        
        initialize_rag_system()
        
        try:
            # Get subject
            subject = Subject.objects.get(name=subject_name)
            
            # Retrieve context
            context_data = retriever.retrieve_with_context(
                query=query_text,
                subject=subject_name,
                k=k
            )
            
            # Generate answer
            answer_data = generator.generate_answer(
                query=query_text,
                context=context_data['context'],
                subject=subject_name,
                temperature=temperature
            )
            
            # Generate follow-up questions
            follow_up = generator.generate_follow_up_questions(
                query=query_text,
                answer=answer_data['answer'],
                subject=subject_name
            )
            
            # Save query
            query_obj = Query.objects.create(
                user=request.user if request.user.is_authenticated else None,
                subject=subject,
                query_text=query_text,
                answer_text=answer_data['answer'],
                context_chunks=len(context_data['chunks']),
                tokens_used=answer_data['usage']['total_tokens']
            )
            
            # Prepare response
            response_data = {
                'query_id': query_obj.id,
                'answer': answer_data['answer'],
                'sources': context_data['sources'],
                'subject': subject_name,
                'tokens_used': answer_data['usage']['total_tokens'],
                'follow_up_questions': follow_up
            }
            
            return Response(response_data)
        
        except Subject.DoesNotExist:
            return Response({
                'error': f"Subject '{subject_name}' not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return Response({
                'error': f'Failed to process query: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def stream(self, request):
        """Stream answer (for future WebSocket implementation)"""
        # Placeholder for streaming implementation
        return Response({
            'message': 'Streaming not yet implemented. Use /ask endpoint.'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class FeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for feedback"""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]


@api_view(['GET'])
@permission_classes([AllowAny])
def system_stats(request):
    """Get overall system statistics"""
    initialize_rag_system()
    
    # Get vector store stats for all subjects
    all_stats = vector_store_manager.get_all_stats()
    
    # Get overall stats
    stats = {
        'subjects': SubjectSerializer(Subject.objects.all(), many=True).data,
        'total_documents': Document.objects.count(),
        'processed_documents': Document.objects.filter(processed=True).count(),
        'total_queries': Query.objects.count(),
        'vector_stores': all_stats
    }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([AllowAny])
def batch_upload(request):
    """Upload multiple documents at once"""
    # Implementation for batch upload
    return Response({
        'message': 'Batch upload endpoint - implementation needed'
    }, status=status.HTTP_501_NOT_IMPLEMENTED)
