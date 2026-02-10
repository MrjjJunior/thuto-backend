# RAG Tutoring System

A production-ready Retrieval-Augmented Generation (RAG) system for tutoring, built with Django backend and React frontend. Features subject-isolated vector stores to prevent cross-contamination of information.

## 🌟 Features

- **Subject Isolation**: Separate FAISS indices for Math and Physics to prevent cross-contamination
- **Multi-Format Support**: Process PDF, DOCX, and TXT files
- **Intelligent Chunking**: Smart document splitting with semantic overlap
- **Vector Search**: Fast similarity search using FAISS
- **Claude Integration**: Powered by Anthropic's Claude for high-quality answers
- **Source Attribution**: Transparent source tracking for all answers
- **Follow-up Questions**: AI-generated follow-up questions for deeper learning
- **Feedback System**: User feedback collection for continuous improvement
- **Modern UI**: Clean React interface with real-time updates

## 🏗️ Architecture

```
Backend (Django + Python)
├── RAG Services
│   ├── Document Loader (PDF, DOCX, TXT)
│   ├── Chunker (Intelligent splitting)
│   ├── Embeddings (sentence-transformers)
│   ├── Vector Store (FAISS with subject isolation)
│   ├── Retriever (Context retrieval)
│   └── Generator (Claude API)
├── REST API (Django REST Framework)
└── Database (SQLite/PostgreSQL)

Frontend (React)
├── API Service Layer
├── Custom Hooks
├── Query Interface
└── Document Management
```

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Anthropic API key

## 🚀 Installation

### Backend Setup

1. **Clone the repository and navigate to project root**

```bash
cd rag-tutoring-system
```

2. **Create and activate virtual environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your-api-key-here
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
```

5. **Run database migrations**

```bash
python manage.py migrate
```

6. **Create initial subjects**

```bash
python manage.py shell
```

```python
from rag_app.models import Subject

Subject.objects.create(
    name='math',
    display_name='Mathematics',
    description='Mathematics course materials'
)

Subject.objects.create(
    name='physics',
    display_name='Physics',
    description='Physics course materials'
)

exit()
```

7. **Create directory structure for documents**

```bash
mkdir -p data/math/{raw,processed,index}
mkdir -p data/physics/{raw,processed,index}
mkdir -p logs
```

8. **Add your course documents**

Place your PDF, DOCX, or TXT files in:
- `data/math/raw/` for math documents
- `data/physics/raw/` for physics documents

9. **Process documents and build vector indices**

```bash
python manage.py process_documents
```

Or process a specific subject:

```bash
python manage.py process_documents --subject math
```

To rebuild indices from scratch:

```bash
python manage.py process_documents --rebuild
```

10. **Start the Django development server**

```bash
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**

```bash
cd frontend
```

2. **Install dependencies**

```bash
npm install
```

3. **Configure API endpoint**

Create `.env` file in frontend directory:

```
REACT_APP_API_URL=http://localhost:8000/api
```

4. **Start development server**

```bash
npm start
```

Frontend will be available at `http://localhost:3000`

## 📖 Usage

### Asking Questions

1. Navigate to "Ask Questions" tab
2. Select a subject (Math or Physics)
3. Type your question
4. Receive AI-powered answer with source attribution
5. View follow-up questions for deeper learning
6. Rate the answer quality

### Managing Documents

1. Navigate to "Manage Documents" tab
2. Select subject and upload file (PDF, DOCX, or TXT)
3. Document will be automatically processed and indexed
4. View all uploaded documents with processing status
5. Delete documents as needed

### API Endpoints

**Subjects**
- `GET /api/subjects/` - List all subjects
- `GET /api/subjects/{id}/` - Get subject details
- `GET /api/subjects/{id}/stats/` - Get subject statistics

**Documents**
- `GET /api/documents/` - List documents (filter by `?subject=math`)
- `POST /api/documents/upload/` - Upload new document
- `DELETE /api/documents/{id}/` - Delete document
- `POST /api/documents/{id}/reprocess/` - Reprocess document

**Queries**
- `POST /api/queries/ask/` - Ask a question
  ```json
  {
    "subject": "math",
    "query": "What is the Pythagorean theorem?",
    "k": 5,
    "temperature": 0.7
  }
  ```
- `GET /api/queries/` - Get query history

**Feedback**
- `POST /api/feedback/` - Submit feedback
  ```json
  {
    "query": 1,
    "rating": 5,
    "comment": "Very helpful!"
  }
  ```

**System**
- `GET /api/stats/` - Get system statistics

## 🔧 Configuration

### Embedding Model

Change the embedding model in `services/embeddings.py`:

```python
embedding_service = EmbeddingService(model_name="all-mpnet-base-v2")
```

Options:
- `all-MiniLM-L6-v2` - Fast, 384 dimensions (default)
- `all-mpnet-base-v2` - Better quality, 768 dimensions
- `paraphrase-multilingual-MiniLM-L12-v2` - Multilingual support

### Chunk Size

Adjust chunking parameters in `services/chunker.py`:

```python
chunker = DocumentChunker(
    chunk_size=800,      # tokens per chunk
    chunk_overlap=100    # overlap between chunks
)
```

### Claude Model

Change the Claude model in `services/generate.py`:

```python
generator = ClaudeGenerator(model="claude-sonnet-4-20250514")
```

### Number of Retrieved Chunks

Modify the default `k` value when asking questions:

```python
# In frontend
await askQuestion(subject, query, { k: 7 })
```

## 📊 Subject Isolation

The system maintains **completely separate vector stores** for each subject:

```
data/
├── math/
│   └── index/
│       ├── math.faiss           # FAISS index for math
│       └── math_metadata.pkl    # Metadata for math chunks
└── physics/
    └── index/
        ├── physics.faiss        # FAISS index for physics
        └── physics_metadata.pkl # Metadata for physics chunks
```

This ensures:
- ✅ No cross-contamination between subjects
- ✅ More accurate retrieval within each domain
- ✅ Better performance due to smaller search space
- ✅ Easy to scale to additional subjects

## 🔒 Security Considerations

For production deployment:

1. **Change authentication**:
   ```python
   # In settings.py
   REST_FRAMEWORK = {
       'DEFAULT_PERMISSION_CLASSES': [
           'rest_framework.permissions.IsAuthenticated',
       ],
   }
   ```

2. **Use environment variables** for all secrets

3. **Enable HTTPS** in production

4. **Use PostgreSQL** instead of SQLite:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'rag_db',
           'USER': 'postgres',
           'PASSWORD': 'password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

5. **Set proper CORS** settings for your domain

## 🚀 Production Deployment

### Using Gunicorn + Nginx

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Run with Gunicorn:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

3. Build React for production:
```bash
cd frontend
npm run build
```

4. Serve with Nginx (example config):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /path/to/frontend/build;
        try_files $uri /index.html;
    }
}
```

## 🐛 Troubleshooting

**Issue**: Documents not processing
- Check logs in `logs/rag_system.log`
- Verify file format is supported (PDF, DOCX, TXT)
- Ensure file size is under 10MB

**Issue**: Empty answers or no context found
- Verify documents are processed: Check `processed=True` in admin
- Run `python manage.py process_documents` again
- Check vector store stats: `GET /api/stats/`

**Issue**: CORS errors
- Verify frontend URL in `settings.py` CORS_ALLOWED_ORIGINS
- Check that Django server is running

**Issue**: API connection errors
- Verify `REACT_APP_API_URL` in frontend `.env`
- Check Django server is running on correct port

## 📝 License

MIT License - feel free to use for your projects!

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue on GitHub.
