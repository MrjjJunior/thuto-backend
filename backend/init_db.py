import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thuto.settings")
django.setup()

from core.models import Subject

subjects = [
        ("Maths", "Mathematics"),
        ("Physics", "Pythsical Science & Chemistry"),
        ("Life Sciences", "Biology"),
        ("English HL", "ENG Home Language"),
        ("Englsih FAL", "ENG First Additional Language"),
        ("Afrikaans HL", "AFR Home Language"),
        ("Afrikaans FAL", "AFR First Additonal Language"),
        ("Accounting","Accounting")
        ]

for name, desc in subjects:
    Subject.objects.get_or_create(name=name, description=desc)

print("Subjects created")
