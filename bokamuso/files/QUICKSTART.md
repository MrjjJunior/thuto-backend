# Quick Start Guide

## 🚀 Get Up and Running in 5 Minutes

### Step 1: Backend Setup (2 minutes)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Initialize database
python manage.py migrate
python init_db.py

# Create directories
mkdir -p data/{math,physics}/{raw,processed,index}
mkdir logs
```

### Step 2: Add Documents (1 minute)

```bash
# Copy your course materials
# PDFs, DOCX, or TXT files to:
cp your_math_textbook.pdf data/math/raw/
cp your_physics_notes.pdf data/physics/raw/

# Process documents
python manage.py process_documents
```

### Step 3: Start Backend (30 seconds)

```bash
python manage.py runserver
# Running at http://localhost:8000
```

### Step 4: Frontend Setup (1.5 minutes)

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env

# Start React app
npm start
# Opens at http://localhost:3000
```

### Step 5: Start Learning! ✨

1. Open http://localhost:3000
2. Select a subject (Math or Physics)
3. Ask a question!
4. Get AI-powered answers with sources

## 📝 Example Questions

**Math:**
- "What is the Pythagorean theorem?"
- "Explain derivatives step by step"
- "How do I solve quadratic equations?"

**Physics:**
- "What is Newton's second law?"
- "Explain how electric circuits work"
- "What is the difference between velocity and acceleration?"

## 🔧 Verify Installation

Test the API:
```bash
curl http://localhost:8000/api/subjects/
curl http://localhost:8000/api/stats/
```

Expected response: JSON with subjects and statistics

## 🐛 Common Issues

**"No module named 'rest_framework'"**
```bash
pip install djangorestframework
```

**"No documents found"**
- Place files in `data/math/raw/` or `data/physics/raw/`
- Run `python manage.py process_documents`

**CORS errors**
- Verify CORS_ALLOWED_ORIGINS in settings.py includes your frontend URL

**"ANTHROPIC_API_KEY not found"**
- Check .env file has ANTHROPIC_API_KEY=your-key-here

## 📖 Next Steps

- Read full README.md for detailed documentation
- Customize system prompt in `services/generate.py`
- Add more subjects by creating new Subject instances
- Configure authentication for production use

## 💡 Pro Tips

1. **Better Embeddings**: Use `all-mpnet-base-v2` for better quality
   ```python
   # In services/embeddings.py
   embedding_service = EmbeddingService("all-mpnet-base-v2")
   ```

2. **More Context**: Increase retrieved chunks
   ```javascript
   // In frontend
   askQuestion(subject, query, { k: 7 })
   ```

3. **Rebuild Index**: If documents change
   ```bash
   python manage.py process_documents --rebuild
   ```

4. **Monitor Usage**: Check token usage in responses
   ```json
   {
     "tokens_used": 1234,
     "answer": "..."
   }
   ```

Happy learning! 🎓
