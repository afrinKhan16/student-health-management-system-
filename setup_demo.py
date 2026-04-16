import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studenthealth.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import Doctor

User = get_user_model()

def setup_demo_data():
    print("Setting up demo data...")
    
    # 1. Admin
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        admin.role = 'admin'
        admin.first_name = "System"
        admin.last_name = "Admin"
        admin.save()
        print("Created Superuser: admin (password: admin)")
    
    # 2. Doctor
    if not User.objects.filter(username='doctor').exists():
        doc_user = User.objects.create_user('doctor', 'doctor@example.com', 'doctor')
        doc_user.role = 'doctor'
        doc_user.first_name = "John"
        doc_user.last_name = "Doe"
        doc_user.save()
        Doctor.objects.create(user=doc_user, specialization="Cardiologist")
        print("Created Doctor: doctor (password: doctor)")
    
    # 3. Teacher
    if not User.objects.filter(username='teacher').exists():
        teacher_user = User.objects.create_user('teacher', 'teacher@example.com', 'teacher')
        teacher_user.role = 'teacher'
        teacher_user.first_name = "Afrin"
        teacher_user.last_name = ""
        teacher_user.save()
        print("Created Teacher: teacher (password: teacher)")
        
    print("\nDemo data setup complete! You can now log in with:")
    print("  Admin   -> username: admin,   password: admin")
    print("  Doctor  -> username: doctor,  password: doctor")
    print("  Teacher -> username: teacher, password: teacher")

if __name__ == '__main__':
    setup_demo_data()
