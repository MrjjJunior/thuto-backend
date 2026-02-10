/**
 * DocumentUpload Component
 * Upload and manage documents for RAG system
 */
import React, { useState } from 'react';
import { useSubjects, useDocumentUpload, useDocuments } from '../hooks/useRAG';
import './DocumentUpload.css';

function DocumentUpload() {
  const { subjects, loading: subjectsLoading } = useSubjects();
  const { uploadDocument, uploading, progress, error: uploadError } = useDocumentUpload();
  const { documents, loading: docsLoading, refetch, deleteDocument } = useDocuments();

  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [filterSubject, setFilterSubject] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['application/pdf', 'text/plain', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      
      if (!allowedTypes.includes(file.type)) {
        alert('Please select a PDF, TXT, or DOCX file');
        e.target.value = '';
        return;
      }

      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        e.target.value = '';
        return;
      }

      setSelectedFile(file);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!selectedSubject || !selectedFile) {
      alert('Please select a subject and file');
      return;
    }

    try {
      await uploadDocument(selectedSubject, selectedFile);
      alert('Document uploaded and processed successfully!');
      
      // Reset form
      setSelectedFile(null);
      setSelectedSubject('');
      document.getElementById('file-input').value = '';
      
      // Refresh document list
      refetch();
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed: ' + error.message);
    }
  };

  const handleDelete = async (docId, docName) => {
    if (window.confirm(`Are you sure you want to delete "${docName}"?`)) {
      try {
        await deleteDocument(docId);
        alert('Document deleted successfully');
      } catch (error) {
        alert('Failed to delete document: ' + error.message);
      }
    }
  };

  const filteredDocuments = filterSubject
    ? documents.filter(doc => doc.subject_name === filterSubject)
    : documents;

  return (
    <div className="document-upload">
      <div className="upload-section">
        <h2>Upload Document</h2>
        
        <form onSubmit={handleUpload} className="upload-form">
          <div className="form-group">
            <label htmlFor="upload-subject">Subject:</label>
            <select
              id="upload-subject"
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              disabled={subjectsLoading || uploading}
              required
            >
              <option value="">Select a subject</option>
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.name}>
                  {subject.display_name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="file-input">File (PDF, TXT, or DOCX):</label>
            <input
              id="file-input"
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.txt,.docx"
              disabled={uploading}
              required
            />
            {selectedFile && (
              <div className="file-info">
                Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
              </div>
            )}
          </div>

          {uploading && (
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progress}%` }}
              />
              <span className="progress-text">{Math.round(progress)}%</span>
            </div>
          )}

          {uploadError && (
            <div className="error-message">
              {uploadError}
            </div>
          )}

          <button 
            type="submit" 
            className="upload-btn"
            disabled={uploading || !selectedSubject || !selectedFile}
          >
            {uploading ? 'Uploading...' : 'Upload & Process'}
          </button>
        </form>
      </div>

      <div className="documents-section">
        <div className="documents-header">
          <h2>Uploaded Documents</h2>
          
          <div className="filter-group">
            <label htmlFor="filter-subject">Filter by subject:</label>
            <select
              id="filter-subject"
              value={filterSubject}
              onChange={(e) => setFilterSubject(e.target.value)}
            >
              <option value="">All subjects</option>
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.name}>
                  {subject.display_name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {docsLoading ? (
          <div className="loading">Loading documents...</div>
        ) : filteredDocuments.length === 0 ? (
          <div className="empty-state">
            No documents uploaded yet
          </div>
        ) : (
          <div className="documents-list">
            <table>
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Subject</th>
                  <th>Type</th>
                  <th>Chunks</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocuments.map((doc) => (
                  <tr key={doc.id}>
                    <td>{doc.filename}</td>
                    <td>{doc.subject_display}</td>
                    <td>{doc.file_type.toUpperCase()}</td>
                    <td>{doc.chunk_count}</td>
                    <td>
                      <span className={`status ${doc.processed ? 'processed' : 'pending'}`}>
                        {doc.processed ? 'Processed' : 'Pending'}
                      </span>
                    </td>
                    <td>{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        className="delete-btn"
                        onClick={() => handleDelete(doc.id, doc.filename)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default DocumentUpload;
