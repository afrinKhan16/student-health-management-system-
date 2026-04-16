import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studenthealth.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
doctors = User.objects.filter(role='doctor')
res = []
for d in doctors:
    d.set_password(d.username)
    d.save()
    spec = d.doctor_profile.specialization if hasattr(d, 'doctor_profile') else ''
    res.append(f"{d.username} (Specialist: {spec})")

print("DOCTOR LIST:", ", ".join(res))
