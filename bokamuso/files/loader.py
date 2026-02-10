"""
Document Loader Service
Handles loading of PDF, DOCX, and TXT files for the RAG system
"""
import os
from typing import List, Dict
import PyPDF2
import pdfplumber
from docx import Document
import logging

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Unified document loader for multiple file formats"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.docx']
    
    def load_document(self, file_path: str, subject: str = None) -> Dict:
        """
        Load a document and return its content with metadata
        
        Args:
            file_path: Path to the document
            subject: Subject category (math/physics)
            
        Returns:
            Dict with 'content', 'metadata', and 'file_type'
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Load content based on file type
        if file_ext == '.pdf':
            content = self._load_pdf(file_path)
        elif file_ext == '.txt':
            content = self._load_txt(file_path)
        elif file_ext == '.docx':
            content = self._load_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Create metadata
        metadata = {
            'source': os.path.basename(file_path),
            'file_path': file_path,
            'subject': subject,
            'file_type': file_ext[1:]  # Remove the dot
        }
        
        return {
            'content': content,
            'metadata': metadata,
            'file_type': file_ext[1:]
        }
    
    def _load_pdf(self, file_path: str) -> str:
        """Load PDF using pdfplumber for better text extraction"""
        try:
            text_content = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            return '\n\n'.join(text_content)
        except Exception as e:
            logger.warning(f"pdfplumber failed for {file_path}, trying PyPDF2: {e}")
            # Fallback to PyPDF2
            return self._load_pdf_pypdf2(file_path)
    
    def _load_pdf_pypdf2(self, file_path: str) -> str:
        """Fallback PDF loader using PyPDF2"""
        text_content = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        return '\n\n'.join(text_content)
    
    def _load_txt(self, file_path: str) -> str:
        """Load plain text file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _load_docx(self, file_path: str) -> str:
        """Load DOCX file"""
        doc = Document(file_path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return '\n\n'.join(paragraphs)
    
    def load_directory(self, directory_path: str, subject: str = None) -> List[Dict]:
        """
        Load all supported documents from a directory
        
        Args:
            directory_path: Path to directory containing documents
            subject: Subject category (math/physics)
            
        Returns:
            List of document dictionaries
        """
        documents = []
        
        if not os.path.exists(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            return documents
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Check if file format is supported
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in self.supported_formats:
                try:
                    doc = self.load_document(file_path, subject)
                    documents.append(doc)
                    logger.info(f"Loaded: {filename}")
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {e}")
        
        return documents
