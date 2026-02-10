# RAG System Architecture

## 📐 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Query      │  │  Document    │  │   Custom     │          │
│  │  Interface   │  │   Upload     │  │   Hooks      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                          │                                        │
│                    API Service Layer                             │
└──────────────────────────┼──────────────────────────────────────┘
                           │ HTTP/REST
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Django Backend                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    REST API Layer                         │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │  │
│  │  │Subject │ │Document│ │ Query  │ │Feedback│           │  │
│  │  │ViewSet │ │ViewSet │ │ViewSet │ │ViewSet │           │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    RAG Services Layer                     │  │
│  │                                                           │  │
│  │  ┌─────────────┐    ┌──────────────┐    ┌────────────┐ │  │
│  │  │   Loader    │───▶│   Chunker    │───▶│ Embeddings │ │  │
│  │  │ PDF/DOCX/TXT│    │ Smart Split  │    │sentence-   │ │  │
│  │  └─────────────┘    └──────────────┘    │transformers│ │  │
│  │                                          └────────────┘ │  │
│  │                           │                              │  │
│  │                           ▼                              │  │
│  │                  ┌────────────────┐                     │  │
│  │                  │ Vector Store   │                     │  │
│  │                  │   Manager      │                     │  │
│  │                  └────────────────┘                     │  │
│  │                    │            │                        │  │
│  │        ┌───────────┴─────┬──────┴─────────┐            │  │
│  │        ▼                  ▼                ▼            │  │
│  │   ┌─────────┐      ┌─────────┐      ┌─────────┐       │  │
│  │   │  Math   │      │ Physics │      │  More   │       │  │
│  │   │  FAISS  │      │  FAISS  │      │ Subjects│       │  │
│  │   │  Index  │      │  Index  │      │  ...    │       │  │
│  │   └─────────┘      └─────────┘      └─────────┘       │  │
│  │        │                  │                │            │  │
│  │        └──────────┬───────┴────────────────┘            │  │
│  │                   ▼                                      │  │
│  │            ┌──────────────┐                             │  │
│  │            │   Retriever  │                             │  │
│  │            │ Context Ret. │                             │  │
│  │            └──────────────┘                             │  │
│  │                   │                                      │  │
│  │                   ▼                                      │  │
│  │            ┌──────────────┐                             │  │
│  │            │   Generator  │                             │  │
│  │            │ Claude API   │◀────────────────────┐       │  │
│  │            └──────────────┘                     │       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                      │          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Database Layer                         │  │
│  │  ┌────────┐ ┌─────────┐ ┌───────┐ ┌──────────┐         │  │
│  │  │Subject │ │Document │ │ Query │ │ Feedback │         │  │
│  │  │ Model  │ │  Model  │ │ Model │ │  Model   │         │  │
│  │  └────────┘ └─────────┘ └───────┘ └──────────┘         │  │
│  │                SQLite / PostgreSQL                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌──────────────────────────┐
              │   Anthropic Claude API   │
              │   GPT-4 class LLM        │
              └──────────────────────────┘
```

## 🔄 Data Flow

### Document Processing Flow

```
1. User uploads document (PDF/DOCX/TXT)
   ↓
2. Document saved to media storage
   ↓
3. DocumentLoader extracts text
   ↓
4. DocumentChunker splits into semantic chunks
   ↓
5. EmbeddingService generates vector embeddings
   ↓
6. VectorStoreManager adds to subject-specific FAISS index
   ↓
7. Metadata saved alongside vectors
   ↓
8. Document marked as processed
```

### Query Processing Flow

```
1. User submits question + selects subject
   ↓
2. Frontend sends to /api/queries/ask/
   ↓
3. Query text embedded using same model
   ↓
4. Retriever searches subject-specific FAISS index
   ↓
5. Top-k relevant chunks retrieved
   ↓
6. Context formatted with source information
   ↓
7. Generator calls Claude API with context
   ↓
8. Claude generates answer based on context
   ↓
9. Follow-up questions generated
   ↓
10. Response sent to frontend with sources
   ↓
11. User can rate and provide feedback
```

## 🗂️ File Structure

```
rag-tutoring-system/
├── config/                      # Django project config
│   ├── settings.py             # Main settings
│   ├── urls.py                 # URL routing
│   └── wsgi.py                 # WSGI config
│
├── rag_app/                    # Main Django app
│   ├── models.py               # Database models
│   ├── views.py                # API views
│   ├── serializers.py          # DRF serializers
│   ├── urls.py                 # App URLs
│   └── management/
│       └── commands/
│           └── process_documents.py
│
├── services/                   # RAG service layer
│   ├── loader.py               # Document loading
│   ├── chunker.py              # Text chunking
│   ├── embeddings.py           # Vector embeddings
│   ├── vectorstore.py          # FAISS management
│   ├── retriever.py            # Context retrieval
│   └── generate.py             # Claude integration
│
├── data/                       # Document storage
│   ├── math/
│   │   ├── raw/                # Original documents
│   │   ├── processed/          # Processed documents
│   │   └── index/              # FAISS indices
│   └── physics/
│       ├── raw/
│       ├── processed/
│       └── index/
│
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── QueryInterface.jsx
│   │   │   ├── DocumentUpload.jsx
│   │   │   └── *.css
│   │   ├── hooks/
│   │   │   └── useRAG.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
│
├── requirements.txt            # Python dependencies
├── init_db.py                  # DB initialization
├── README.md                   # Full documentation
└── QUICKSTART.md              # Quick start guide
```

## 🔐 Security Features

### Subject Isolation

Each subject has its own isolated FAISS index:

```python
# Completely separate indices
math_store = SubjectVectorStore('math', embedding_dim, 'data/math/index/math.faiss')
physics_store = SubjectVectorStore('physics', embedding_dim, 'data/physics/index/physics.faiss')

# Query only searches in specified subject
math_results = retriever.retrieve(query, subject='math', k=5)
# This NEVER returns physics results
```

### Benefits:
- ✅ No cross-contamination
- ✅ More accurate results
- ✅ Faster searches (smaller index)
- ✅ Easy to scale to more subjects

## ⚙️ Key Components

### 1. Document Loader
- Supports PDF, DOCX, TXT
- Extracts clean text
- Preserves structure when possible

### 2. Chunker
- Smart semantic splitting
- Configurable chunk size (default 800 tokens)
- Overlap for context continuity (default 100 tokens)
- Respects paragraph boundaries

### 3. Embeddings
- sentence-transformers models
- Default: all-MiniLM-L6-v2 (384 dim)
- Alternative: all-mpnet-base-v2 (768 dim)
- Batched processing for efficiency

### 4. Vector Store
- FAISS for fast similarity search
- L2 distance metric
- Persistent storage
- Metadata tracking

### 5. Retriever
- Context retrieval with k-NN search
- Source attribution
- Score threshold filtering
- Formatted context for LLM

### 6. Generator
- Anthropic Claude integration
- Streaming support
- Token usage tracking
- Follow-up question generation

## 📊 Scalability

### Adding New Subjects

```python
# 1. Create subject in database
Subject.objects.create(
    name='chemistry',
    display_name='Chemistry',
    description='Chemistry course materials'
)

# 2. Create directory structure
mkdir -p data/chemistry/{raw,processed,index}

# 3. Add documents to data/chemistry/raw/

# 4. Process documents
python manage.py process_documents --subject chemistry
```

The system automatically:
- Creates new FAISS index
- Maintains isolation from other subjects
- Enables queries for new subject

### Performance Optimization

1. **GPU Acceleration**: Use `faiss-gpu` for large datasets
2. **Batch Processing**: Process documents in batches
3. **Caching**: Cache embeddings for repeated queries
4. **Index Optimization**: Use IVF indices for millions of vectors

## 🔄 API Integration

### Example Frontend Integration

```javascript
// Ask a question
const response = await apiService.askQuestion('math', 'What is calculus?', {
  k: 5,              // Retrieve 5 chunks
  temperature: 0.7   // LLM temperature
});

// Upload a document
await apiService.uploadDocument('physics', file, (progress) => {
  console.log(`Upload: ${progress}%`);
});

// Get statistics
const stats = await apiService.getSystemStats();
```

## 🎯 Best Practices

1. **Document Quality**: Use high-quality, well-formatted documents
2. **Chunk Size**: Adjust based on document structure
3. **Retrieval Count**: Start with k=5, adjust based on results
4. **Temperature**: Lower (0.3-0.5) for factual, higher (0.7-0.9) for creative
5. **Feedback Loop**: Collect user feedback to improve system

## 📈 Monitoring

Track these metrics:
- Document processing success rate
- Query response time
- Token usage per query
- User satisfaction ratings
- Vector store size per subject
- Cache hit rates

This architecture provides a robust, scalable, and maintainable RAG system for educational applications!
