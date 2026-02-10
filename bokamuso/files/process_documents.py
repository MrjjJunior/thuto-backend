"""
Management command to process documents in bulk
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from rag_app.models import Subject, Document
import sys

sys.path.append(os.path.join(settings.BASE_DIR, 'services'))

from loader import DocumentLoader
from chunker import DocumentChunker
from embeddings import get_embedding_service
from vectorstore import VectorStoreManager


class Command(BaseCommand):
    help = 'Process documents from data/raw folders and add to vector store'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--subject',
            type=str,
            help='Process only specific subject (math or physics)',
        )
        parser.add_argument(
            '--rebuild',
            action='store_true',
            help='Rebuild vector store from scratch',
        )
    
    def handle(self, *args, **options):
        subject_filter = options.get('subject')
        rebuild = options.get('rebuild')
        
        # Initialize services
        self.stdout.write('Initializing RAG services...')
        embedding_service = get_embedding_service()
        
        data_path = os.path.join(settings.BASE_DIR, 'data')
        vector_store_manager = VectorStoreManager(
            base_path=data_path,
            embedding_dim=embedding_service.get_embedding_dimension()
        )
        
        # Get subjects to process
        subjects = Subject.objects.all()
        if subject_filter:
            subjects = subjects.filter(name=subject_filter)
        
        for subject in subjects:
            self.stdout.write(f'\n=== Processing {subject.display_name} ===')
            
            # Clear if rebuild
            if rebuild:
                self.stdout.write('Rebuilding vector store...')
                vector_store_manager.clear_subject(subject.name)
            
            # Get raw documents path
            raw_path = os.path.join(data_path, subject.name, 'raw')
            
            if not os.path.exists(raw_path):
                self.stdout.write(self.style.WARNING(f'Raw folder not found: {raw_path}'))
                continue
            
            # Load documents
            loader = DocumentLoader()
            documents = loader.load_directory(raw_path, subject=subject.name)
            
            if not documents:
                self.stdout.write(self.style.WARNING(f'No documents found in {raw_path}'))
                continue
            
            self.stdout.write(f'Loaded {len(documents)} documents')
            
            # Chunk documents
            chunker = DocumentChunker()
            all_chunks = []
            
            for doc in documents:
                chunks = chunker.chunk_document(doc)
                all_chunks.extend(chunks)
                self.stdout.write(f'  {doc["metadata"]["source"]}: {len(chunks)} chunks')
            
            # Embed chunks
            self.stdout.write(f'Embedding {len(all_chunks)} chunks...')
            chunks_with_embeddings = embedding_service.embed_chunks(all_chunks)
            
            # Add to vector store
            self.stdout.write('Adding to vector store...')
            count = vector_store_manager.add_chunks_to_subject(
                subject.name,
                chunks_with_embeddings
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Added {count} chunks to {subject.name}'))
        
        # Save all stores
        vector_store_manager.save_all()
        
        # Print stats
        self.stdout.write('\n=== Statistics ===')
        stats = vector_store_manager.get_all_stats()
        for subject_name, subject_stats in stats.items():
            self.stdout.write(f'{subject_name}: {subject_stats["total_vectors"]} vectors')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Processing complete!'))
