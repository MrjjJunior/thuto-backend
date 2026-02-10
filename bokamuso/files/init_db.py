"""
Initialize database with subjects
Run with: python init_db.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rag_app.models import Subject

def init_subjects():
    """Create initial subjects"""
    subjects = [
        {
            'name': 'math',
            'display_name': 'Mathematics',
            'description': 'Mathematics course materials including algebra, calculus, geometry, and statistics'
        },
        {
            'name': 'physics',
            'display_name': 'Physics',
            'description': 'Physics course materials including mechanics, thermodynamics, electromagnetism, and quantum physics'
        }
    ]
    
    for subject_data in subjects:
        subject, created = Subject.objects.get_or_create(
            name=subject_data['name'],
            defaults={
                'display_name': subject_data['display_name'],
                'description': subject_data['description']
            }
        )
        
        if created:
            print(f'✓ Created subject: {subject.display_name}')
        else:
            print(f'- Subject already exists: {subject.display_name}')

if __name__ == '__main__':
    print('Initializing database with subjects...\n')
    init_subjects()
    print('\n✓ Database initialization complete!')
