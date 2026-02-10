/**
 * API Service for RAG Tutoring System
 * Connects React frontend to Django backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class RAGApiService {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Generic fetch wrapper with error handling
   */
  async fetch(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || error.detail || 'API request failed');
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // ========== Subject Endpoints ==========
  
  /**
   * Get all subjects
   */
  async getSubjects() {
    return this.fetch('/subjects/');
  }

  /**
   * Get subject by ID
   */
  async getSubject(id) {
    return this.fetch(`/subjects/${id}/`);
  }

  /**
   * Get subject statistics
   */
  async getSubjectStats(id) {
    return this.fetch(`/subjects/${id}/stats/`);
  }

  // ========== Document Endpoints ==========
  
  /**
   * Get all documents (optionally filtered by subject)
   */
  async getDocuments(subject = null) {
    const params = subject ? `?subject=${subject}` : '';
    return this.fetch(`/documents/${params}`);
  }

  /**
   * Upload a document
   */
  async uploadDocument(subject, file, onProgress = null) {
    const formData = new FormData();
    formData.append('subject', subject);
    formData.append('file', file);

    const xhr = new XMLHttpRequest();
    
    return new Promise((resolve, reject) => {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const percentComplete = (e.loaded / e.total) * 100;
          onProgress(percentComplete);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          reject(new Error(xhr.responseText));
        }
      });

      xhr.addEventListener('error', () => reject(new Error('Upload failed')));
      xhr.addEventListener('abort', () => reject(new Error('Upload aborted')));

      xhr.open('POST', `${this.baseURL}/documents/upload/`);
      xhr.send(formData);
    });
  }

  /**
   * Delete a document
   */
  async deleteDocument(id) {
    return this.fetch(`/documents/${id}/`, {
      method: 'DELETE',
    });
  }

  /**
   * Reprocess a document
   */
  async reprocessDocument(id) {
    return this.fetch(`/documents/${id}/reprocess/`, {
      method: 'POST',
    });
  }

  // ========== Query Endpoints ==========
  
  /**
   * Ask a question
   */
  async askQuestion(subject, query, options = {}) {
    const { k = 5, temperature = 0.7 } = options;
    
    return this.fetch('/queries/ask/', {
      method: 'POST',
      body: JSON.stringify({
        subject,
        query,
        k,
        temperature,
      }),
    });
  }

  /**
   * Get query history
   */
  async getQueryHistory(page = 1) {
    return this.fetch(`/queries/?page=${page}`);
  }

  /**
   * Get specific query
   */
  async getQuery(id) {
    return this.fetch(`/queries/${id}/`);
  }

  // ========== Feedback Endpoints ==========
  
  /**
   * Submit feedback for a query
   */
  async submitFeedback(queryId, rating, comment = '') {
    return this.fetch('/feedback/', {
      method: 'POST',
      body: JSON.stringify({
        query: queryId,
        rating,
        comment,
      }),
    });
  }

  // ========== System Endpoints ==========
  
  /**
   * Get system statistics
   */
  async getSystemStats() {
    return this.fetch('/stats/');
  }
}

// Export singleton instance
const apiService = new RAGApiService();
export default apiService;
