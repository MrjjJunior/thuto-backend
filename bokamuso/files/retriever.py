"""
Retriever Service
Retrieves relevant context from vector stores for RAG
"""
from typing import List, Dict, Optional
import numpy as np
import logging
from .embeddings import get_embedding_service
from .vectorstore import VectorStoreManager

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Retrieves relevant context for queries"""
    
    def __init__(self, vector_store_manager: VectorStoreManager, embedding_service=None):
        """
        Initialize retriever
        
        Args:
            vector_store_manager: VectorStoreManager instance
            embedding_service: EmbeddingService instance (optional)
        """
        self.vector_store_manager = vector_store_manager
        self.embedding_service = embedding_service or get_embedding_service()
    
    def retrieve(
        self, 
        query: str, 
        subject: str, 
        k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Retrieve relevant chunks for a query
        
        Args:
            query: User query
            subject: Subject to search in (e.g., 'math', 'physics')
            k: Number of chunks to retrieve
            score_threshold: Minimum score threshold (L2 distance, lower is better)
            
        Returns:
            List of relevant chunks with metadata
        """
        # Embed the query
        query_embedding = self.embedding_service.embed_text(query)
        
        # Search in the subject's vector store
        results = self.vector_store_manager.search(subject, query_embedding, k)
        
        # Filter by score threshold if provided
        if score_threshold is not None:
            results = [r for r in results if r['score'] <= score_threshold]
        
        logger.info(f"Retrieved {len(results)} chunks for query in {subject}")
        
        return results
    
    def retrieve_with_context(
        self,
        query: str,
        subject: str,
        k: int = 5,
        score_threshold: Optional[float] = None,
        include_sources: bool = True
    ) -> Dict:
        """
        Retrieve chunks and format as context for LLM
        
        Args:
            query: User query
            subject: Subject to search in
            k: Number of chunks to retrieve
            score_threshold: Score threshold
            include_sources: Whether to include source information
            
        Returns:
            Dict with 'context', 'sources', and 'chunks'
        """
        # Retrieve relevant chunks
        chunks = self.retrieve(query, subject, k, score_threshold)
        
        if not chunks:
            return {
                'context': '',
                'sources': [],
                'chunks': []
            }
        
        # Format context
        context_parts = []
        sources = []
        
        for i, chunk in enumerate(chunks, 1):
            # Add chunk content
            context_parts.append(f"[Document {i}]")
            context_parts.append(chunk['content'])
            context_parts.append("")  # Empty line for separation
            
            # Collect source information
            if include_sources:
                source_info = {
                    'rank': chunk['rank'],
                    'score': chunk['score'],
                    'source': chunk['metadata'].get('source', 'Unknown'),
                    'subject': chunk['metadata'].get('subject', subject),
                    'chunk_id': chunk['metadata'].get('chunk_id', 'N/A')
                }
                sources.append(source_info)
        
        context = '\n'.join(context_parts)
        
        return {
            'context': context,
            'sources': sources,
            'chunks': chunks
        }
    
    def retrieve_multi_subject(
        self,
        query: str,
        subjects: List[str],
        k_per_subject: int = 3
    ) -> Dict[str, List[Dict]]:
        """
        Retrieve from multiple subjects (use cautiously to avoid cross-contamination)
        
        Args:
            query: User query
            subjects: List of subjects to search
            k_per_subject: Results per subject
            
        Returns:
            Dict mapping subject to results
        """
        query_embedding = self.embedding_service.embed_text(query)
        
        results = {}
        for subject in subjects:
            subject_results = self.vector_store_manager.search(
                subject, 
                query_embedding, 
                k_per_subject
            )
            results[subject] = subject_results
        
        return results
    
    def get_similar_chunks(
        self,
        chunk_content: str,
        subject: str,
        k: int = 3,
        exclude_same_source: bool = True
    ) -> List[Dict]:
        """
        Find similar chunks to a given chunk
        
        Args:
            chunk_content: Content to find similar chunks for
            subject: Subject to search in
            k: Number of similar chunks
            exclude_same_source: Exclude chunks from the same source
            
        Returns:
            List of similar chunks
        """
        # Embed the chunk
        chunk_embedding = self.embedding_service.embed_text(chunk_content)
        
        # Search for similar chunks (retrieve more than k for filtering)
        results = self.vector_store_manager.search(subject, chunk_embedding, k * 2)
        
        if exclude_same_source:
            # Filter out exact matches and same source
            filtered = []
            for r in results:
                if r['content'] != chunk_content:
                    filtered.append(r)
                if len(filtered) >= k:
                    break
            results = filtered[:k]
        
        return results
