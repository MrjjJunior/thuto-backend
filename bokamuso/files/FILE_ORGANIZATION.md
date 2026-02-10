# File Organization Guide

## 📂 How to Organize Your Downloaded Files

All the files you've downloaded need to be organized in a specific directory structure for the RAG system to work properly.

## Project Structure

Create this exact folder structure:

```
rag-tutoring-system/
├── backend/
│   ├── config/
│   ├── rag_app/
│   │   └── management/
│   │       └── commands/
│   ├── services/
│   ├── data/
│   │   ├── math/
│   │   │   ├── raw/
│   │   │   ├── processed/
│   │   │   └── index/
│   │   └── physics/
│   │       ├── raw/
│   │       ├── processed/
│   │       └── index/
│   ├── logs/
│   └── media/
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── hooks/
    │   └── services/
    └── public/
```

## File Placement Instructions

### 📄 Documentation (Root Level - Read These First!)
Place in your project root folder:
- **SUMMARY.md** - Complete system overview (START HERE!)
- **README.md** - Full documentation
- **QUICKSTART.md** - 5-minute setup guide
- **ARCHITECTURE.md** - System architecture details
- **FILE_ORGANIZATION.md** - This file

### 🔧 Backend Root Files
Place in `backend/` folder:
- **requirements.txt** - Python dependencies
- **.env.example** - Environment variable template (rename to .env)
- **init_db.py** - Database initialization script

### ⚙️ Backend Services (Place in `backend/services/`)
- **loader.py** - Document loader
- **chunker.py** - Text chunking
- **embeddings.py** - Vector embeddings
- **vectorstore.py** - FAISS vector store management
- **retriever.py** - Context retrieval
- **generate.py** - Claude API integration

### 🗄️ Django App (Place in `backend/rag_app/`)
- **models.py** - Database models
- **serializers.py** - REST API serializers
- **views.py** - API views and endpoints
- **urls.py** - URL routing (rag_app)

Create empty `__init__.py` files in:
- `backend/rag_app/__init__.py`
- `backend/rag_app/management/__init__.py`
- `backend/rag_app/management/commands/__init__.py`

### 📋 Management Command (Place in `backend/rag_app/management/commands/`)
- **process_documents.py** - Document processing command

### ⚙️ Django Config (Place in `backend/config/`)
- **settings.py** - Django settings
- **urls.py** - Main URL configuration (config)

Create empty `__init__.py` in:
- `backend/config/__init__.py`

Also create `backend/config/wsgi.py`:
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
```

### 💻 Frontend Root (Place in `frontend/`)
- **package.json** - Node dependencies

### 🎨 Frontend Components (Place in `frontend/src/components/`)
- **QueryInterface.jsx**
- **QueryInterface.css**
- **DocumentUpload.jsx**
- **DocumentUpload.css**

### 🪝 Frontend Hooks (Place in `frontend/src/hooks/`)
- **useRAG.js**

### 🌐 Frontend Services (Place in `frontend/src/services/`)
- **api.js**

### 📱 Frontend App (Place in `frontend/src/`)
- **App.jsx**
- **App.css**

Also create `frontend/src/index.js`:
```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

And `frontend/public/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>RAG Tutoring System</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
```

## Quick Setup Commands

After organizing files, run these commands:

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure .env
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run migrations
python manage.py migrate

# Initialize database
python init_db.py

# Create data directories (if not already created)
mkdir -p data/{math,physics}/{raw,processed,index} logs media

# Start server
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create .env
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env

# Start development server
npm start
```

## Additional Files to Create

### backend/manage.py
```python
#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
```

Make it executable:
```bash
chmod +x backend/manage.py
```

### backend/services/__init__.py
Create empty file.

### frontend/.gitignore
```
node_modules/
build/
.env
.env.local
npm-debug.log*
```

### backend/.gitignore
```
*.pyc
__pycache__/
db.sqlite3
media/
logs/
.env
venv/
data/*/index/*.faiss
data/*/index/*.pkl
```

## Verification Checklist

After organizing files, verify:

- [ ] All Python files are in correct directories
- [ ] All `__init__.py` files created
- [ ] `manage.py` created and executable
- [ ] `wsgi.py` created in config/
- [ ] All React components in frontend/src/components/
- [ ] `index.js` and `index.html` created
- [ ] `.env.example` copied to `.env` and configured
- [ ] Data directories created (math, physics)

## Testing Your Setup

1. **Backend Test:**
   ```bash
   cd backend
   python manage.py check
   # Should show: System check identified no issues
   ```

2. **Frontend Test:**
   ```bash
   cd frontend
   npm run build
   # Should compile without errors
   ```

3. **Full System Test:**
   - Start backend: `python manage.py runserver`
   - Start frontend: `npm start`
   - Visit http://localhost:3000
   - Should see the RAG Tutoring interface

## Need Help?

If you encounter issues:
1. Check this file organization matches exactly
2. Verify all `__init__.py` files exist
3. Check `.env` file has ANTHROPIC_API_KEY
4. Review QUICKSTART.md for step-by-step setup
5. Consult README.md troubleshooting section

## Next Steps

Once files are organized:
1. Read **SUMMARY.md** for system overview
2. Follow **QUICKSTART.md** for setup
3. Add your documents to `data/math/raw/` and `data/physics/raw/`
4. Process documents: `python manage.py process_documents`
5. Start using the system!

---

**Important:** Keep this file for reference when setting up the system!
