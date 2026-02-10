/**
 * Custom React Hooks for RAG System
 */
import { useState, useEffect, useCallback } from 'react';
import apiService from '../services/api';

/**
 * Hook to fetch and manage subjects
 */
export function useSubjects() {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSubjects = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.getSubjects();
      setSubjects(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSubjects();
  }, [fetchSubjects]);

  return { subjects, loading, error, refetch: fetchSubjects };
}

/**
 * Hook to manage document uploads
 */
export function useDocumentUpload() {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const uploadDocument = async (subject, file) => {
    try {
      setUploading(true);
      setProgress(0);
      setError(null);

      const result = await apiService.uploadDocument(
        subject,
        file,
        (percent) => setProgress(percent)
      );

      setUploading(false);
      return result;
    } catch (err) {
      setError(err.message);
      setUploading(false);
      throw err;
    }
  };

  return { uploadDocument, uploading, progress, error };
}

/**
 * Hook to ask questions and get answers
 */
export function useQuery() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const askQuestion = async (subject, query, options = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await apiService.askQuestion(subject, query, options);
      setResult(data);
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
  };

  return { askQuestion, loading, error, result, reset };
}

/**
 * Hook to manage query history
 */
export function useQueryHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = useCallback(async (page = 1) => {
    try {
      setLoading(true);
      const data = await apiService.getQueryHistory(page);
      setHistory(data.results || data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return { history, loading, error, refetch: fetchHistory };
}

/**
 * Hook to fetch documents
 */
export function useDocuments(subject = null) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.getDocuments(subject);
      setDocuments(data.results || data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [subject]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const deleteDocument = async (id) => {
    try {
      await apiService.deleteDocument(id);
      await fetchDocuments(); // Refresh list
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  return { documents, loading, error, refetch: fetchDocuments, deleteDocument };
}

/**
 * Hook to submit feedback
 */
export function useFeedback() {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const submitFeedback = async (queryId, rating, comment = '') => {
    try {
      setSubmitting(true);
      setError(null);
      
      const result = await apiService.submitFeedback(queryId, rating, comment);
      
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setSubmitting(false);
    }
  };

  return { submitFeedback, submitting, error };
}

/**
 * Hook to fetch system statistics
 */
export function useSystemStats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiService.getSystemStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, loading, error, refetch: fetchStats };
}
