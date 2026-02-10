"""
Document Chunker Service
Splits documents into semantic chunks for embedding
"""
import re
from typing import List, Dict
import tiktoken
import logging

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Intelligent document chunking with overlap"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        """
        Initialize chunker
        
        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def chunk_document(self, document: Dict) -> List[Dict]:
        """
        Split document into chunks with metadata
        
        Args:
            document: Document dict from loader
            
        Returns:
            List of chunk dictionaries
        """
        content = document['content']
        metadata = document['metadata']
        
        # First, try to split by natural boundaries (paragraphs)
        paragraphs = self._split_into_paragraphs(content)
        
        # Create chunks respecting paragraph boundaries when possible
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for para in paragraphs:
            para_tokens = self.count_tokens(para)
            
            # If paragraph alone exceeds chunk size, split it
            if para_tokens > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                    current_tokens = 0
                
                # Split large paragraph
                sub_chunks = self._split_large_text(para)
                chunks.extend(sub_chunks)
            
            # If adding paragraph exceeds chunk size, save current chunk
            elif current_tokens + para_tokens > self.chunk_size:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + "\n\n" + para
                current_tokens = self.count_tokens(current_chunk)
            
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
                current_tokens += para_tokens
        
        # Add remaining chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Create chunk objects with metadata
        chunk_objects = []
        for i, chunk_text in enumerate(chunks):
            chunk_obj = {
                'content': chunk_text,
                'metadata': {
                    **metadata,
                    'chunk_id': i,
                    'total_chunks': len(chunks),
                    'tokens': self.count_tokens(chunk_text)
                }
            }
            chunk_objects.append(chunk_obj)
        
        logger.info(f"Split {metadata.get('source', 'document')} into {len(chunks)} chunks")
        return chunk_objects
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split by double newlines or multiple newlines
        paragraphs = re.split(r'\n\s*\n', text)
        # Filter out empty paragraphs
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_large_text(self, text: str) -> List[str]:
        """Split large text that exceeds chunk size"""
        # Try to split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            if current_tokens + sentence_tokens > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    overlap = self._get_overlap_text(current_chunk)
                    current_chunk = overlap + " " + sentence
                    current_tokens = self.count_tokens(current_chunk)
                else:
                    # Single sentence too long, force split by words
                    word_chunks = self._split_by_words(sentence)
                    chunks.extend(word_chunks)
            else:
                current_chunk += " " + sentence if current_chunk else sentence
                current_tokens += sentence_tokens
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_by_words(self, text: str) -> List[str]:
        """Force split by words when sentence is too long"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for word in words:
            word_tokens = self.count_tokens(word)
            
            if current_tokens + word_tokens > self.chunk_size:
                chunks.append(' '.join(current_chunk))
                # Keep some overlap
                overlap_words = current_chunk[-20:] if len(current_chunk) > 20 else current_chunk
                current_chunk = overlap_words + [word]
                current_tokens = self.count_tokens(' '.join(current_chunk))
            else:
                current_chunk.append(word)
                current_tokens += word_tokens
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from end of chunk"""
        tokens = self.encoding.encode(text)
        if len(tokens) <= self.chunk_overlap:
            return text
        
        overlap_tokens = tokens[-self.chunk_overlap:]
        return self.encoding.decode(overlap_tokens)
    
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk multiple documents
        
        Args:
            documents: List of document dicts
            
        Returns:
            List of all chunks from all documents
        """
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        
        return all_chunks
