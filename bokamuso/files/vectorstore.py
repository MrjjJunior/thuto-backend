"""
Vector Store Service
Manages FAISS indices with subject isolation
"""
import os
import pickle
from typing import List, Dict, Tuple, Optional
import numpy as np
import faiss
import logging

logger = logging.getLogger(__name__)


class SubjectVectorStore:
    """FAISS vector store for a specific subject"""
    
    def __init__(self, subject: str, embedding_dim: int, index_path: str):
        """
        Initialize vector store for a subject
        
        Args:
            subject: Subject name (e.g., 'math', 'physics')
            embedding_dim: Dimension of embedding vectors
            index_path: Path to save/load index
        """
        self.subject = subject
        self.embedding_dim = embedding_dim
        self.index_path = index_path
        self.metadata_path = index_path.replace('.faiss', '_metadata.pkl')
        
        # Initialize FAISS index (using L2 distance, can also use Inner Product)
        self.index = faiss.IndexFlatL2(embedding_dim)
        
        # Store metadata for each vector
        self.metadata = []
        
        # Load existing index if available
        if os.path.exists(index_path):
            self.load()
    
    def add_chunks(self, chunks: List[Dict]) -> int:
        """
        Add chunks to the index
        
        Args:
            chunks: List of chunk dicts with 'embedding' and 'metadata'
            
        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0
        
        # Extract embeddings
        embeddings = np.array([chunk['embedding'] for chunk in chunks]).astype('float32')
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store metadata
        for chunk in chunks:
            metadata = chunk['metadata'].copy()
            metadata['content'] = chunk['content']
            self.metadata.append(metadata)
        
        logger.info(f"Added {len(chunks)} chunks to {self.subject} index. Total: {self.index.ntotal}")
        return len(chunks)
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Search for similar chunks
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of results with metadata and scores
        """
        if self.index.ntotal == 0:
            logger.warning(f"No vectors in {self.subject} index")
            return []
        
        # Ensure query is 2D array
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Search
        k = min(k, self.index.ntotal)  # Don't request more than available
        distances, indices = self.index.search(query_embedding, k)
        
        # Prepare results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):  # Safety check
                result = {
                    'content': self.metadata[idx]['content'],
                    'metadata': {k: v for k, v in self.metadata[idx].items() if k != 'content'},
                    'score': float(distance),  # L2 distance (lower is better)
                    'rank': i + 1
                }
                results.append(result)
        
        return results
    
    def save(self):
        """Save index and metadata to disk"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, self.index_path)
        
        # Save metadata
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        logger.info(f"Saved {self.subject} index to {self.index_path}")
    
    def load(self):
        """Load index and metadata from disk"""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            logger.info(f"Loaded {self.subject} index from {self.index_path}")
        
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            logger.info(f"Loaded {len(self.metadata)} metadata entries")
    
    def clear(self):
        """Clear the index and metadata"""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata = []
        logger.info(f"Cleared {self.subject} index")
    
    def get_stats(self) -> Dict:
        """Get statistics about the index"""
        return {
            'subject': self.subject,
            'total_vectors': self.index.ntotal,
            'embedding_dim': self.embedding_dim,
            'total_metadata': len(self.metadata)
        }


class VectorStoreManager:
    """Manages multiple subject-specific vector stores"""
    
    def __init__(self, base_path: str, embedding_dim: int):
        """
        Initialize vector store manager
        
        Args:
            base_path: Base directory for storing indices
            embedding_dim: Dimension of embedding vectors
        """
        self.base_path = base_path
        self.embedding_dim = embedding_dim
        self.stores: Dict[str, SubjectVectorStore] = {}
        
        os.makedirs(base_path, exist_ok=True)
    
    def get_or_create_store(self, subject: str) -> SubjectVectorStore:
        """
        Get or create a vector store for a subject
        
        Args:
            subject: Subject name (e.g., 'math', 'physics')
            
        Returns:
            SubjectVectorStore instance
        """
        if subject not in self.stores:
            index_path = os.path.join(self.base_path, subject, 'index', f'{subject}.faiss')
            self.stores[subject] = SubjectVectorStore(subject, self.embedding_dim, index_path)
        
        return self.stores[subject]
    
    def add_chunks_to_subject(self, subject: str, chunks: List[Dict]) -> int:
        """
        Add chunks to a specific subject's vector store
        
        Args:
            subject: Subject name
            chunks: List of chunks with embeddings
            
        Returns:
            Number of chunks added
        """
        # Filter chunks for this subject
        subject_chunks = [
            chunk for chunk in chunks 
            if chunk.get('metadata', {}).get('subject') == subject
        ]
        
        if not subject_chunks:
            logger.warning(f"No chunks found for subject: {subject}")
            return 0
        
        store = self.get_or_create_store(subject)
        count = store.add_chunks(subject_chunks)
        
        # Auto-save after adding
        store.save()
        
        return count
    
    def search(self, subject: str, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Search within a specific subject
        
        Args:
            subject: Subject to search in
            query_embedding: Query vector
            k: Number of results
            
        Returns:
            List of search results
        """
        if subject not in self.stores:
            logger.error(f"No vector store found for subject: {subject}")
            return []
        
        return self.stores[subject].search(query_embedding, k)
    
    def search_all_subjects(self, query_embedding: np.ndarray, k: int = 5) -> Dict[str, List[Dict]]:
        """
        Search across all subjects (for comparison/debugging)
        
        Args:
            query_embedding: Query vector
            k: Number of results per subject
            
        Returns:
            Dict mapping subject to results
        """
        results = {}
        for subject, store in self.stores.items():
            results[subject] = store.search(query_embedding, k)
        
        return results
    
    def save_all(self):
        """Save all subject stores"""
        for subject, store in self.stores.items():
            store.save()
        logger.info(f"Saved all {len(self.stores)} subject stores")
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics for all subjects"""
        return {
            subject: store.get_stats() 
            for subject, store in self.stores.items()
        }
    
    def clear_subject(self, subject: str):
        """Clear a specific subject's index"""
        if subject in self.stores:
            self.stores[subject].clear()
            self.stores[subject].save()
