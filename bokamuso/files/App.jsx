/**
 * Main App Component
 * RAG Tutoring System Frontend
 */
import React, { useState } from 'react';
import QueryInterface from './components/QueryInterface';
import DocumentUpload from './components/DocumentUpload';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('query');

  return (
    <div className="App">
      <header className="app-header">
        <h1>📚 RAG Tutoring System</h1>
        <p>AI-Powered Learning Assistant</p>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-btn ${activeTab === 'query' ? 'active' : ''}`}
          onClick={() => setActiveTab('query')}
        >
          Ask Questions
        </button>
        <button
          className={`nav-btn ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          Manage Documents
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'query' && <QueryInterface />}
        {activeTab === 'documents' && <DocumentUpload />}
      </main>

      <footer className="app-footer">
        <p>
          Powered by Anthropic Claude • FAISS Vector Store • Django Backend
        </p>
      </footer>
    </div>
  );
}

export default App;
