from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import User, Patient, Doctor, Schedule, Appointment, Prescription, Bill, Notification

def login_page(request):
    if request.user.is_authenticated:
        # Role-based redirect after login
        if request.user.role == 'teacher':
            return redirect('teacher_dashboard')
        return redirect('dashboard')
        
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            # Role-based redirect after login
            if user.role == 'teacher':
                return redirect('teacher_dashboard')
            return redirect('dashboard')
        else:
            return render(request, 'index.html', {'error': 'Invalid username or password. Please try again.'})

    return render(request, 'index.html')

@login_required(login_url='login')
def dashboard(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    total_doctors = Doctor.objects.count()
    requested_appointments = Appointment.objects.filter(status='pending').count()
    
    busy_doctors = Appointment.objects.filter(status='pending').values_list('doctor_id', flat=True)
    available_doctors = Doctor.objects.exclude(id__in=busy_doctors).count()
    
    emergency_cases = Appointment.objects.filter(is_emergency=True, status='pending').count()

    context = {
        'notifications': notifications,
        'total_doctors': total_doctors,
        'requested_appointments': requested_appointments,
        'available_doctors': available_doctors,
        'emergency_cases': emergency_cases
    }
    return render(request, 'Admin panel dashboard.html', context)

def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

@login_required(login_url='login')
def register_patient(request):
    if request.user.role != 'teacher':
        messages.error(request, "You do not have permission to register students.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        address = request.POST.get('address', '')
        emergency_contact = request.POST.get('emergency_contact', '')
        emergency_phone = request.POST.get('emergency_phone', '')
        general_info = request.POST.get('general_info', '')
        health_info = request.POST.get('health_info', '')

        if first_name:
            import uuid
            unique_username = "student_" + uuid.uuid4().hex[:8]
            new_user = User.objects.create_user(
                username=unique_username,
                first_name=first_name,
                last_name=last_name,
                role='patient'
            )
            Patient.objects.create(
                user=new_user,
                phone=emergency_phone,
                address=address,
                medical_history=f"General: {general_info}\nHealth: {health_info}\nEmergency Contact: {emergency_contact}"
            )
            messages.success(request, f"Student '{first_name} {last_name}' registered successfully!")
        else:
            messages.error(request, "Please provide at least the student's first name.")
        
        return redirect('register_patient')
        
    return render(request, 'Student profile.html')

def student_signup(request):
    if request.user.is_authenticated:
        if request.user.role == 'teacher':
            return redirect('teacher_dashboard')
        return redirect('dashboard')
        
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists. Please choose a different one.'})

        if first_name and username and password:
            new_user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                role='patient'
            )
            Patient.objects.create(
                user=new_user
            )
            messages.success(request, f"Account created successfully for {first_name}! You can now login.")
            return redirect('login')
        else:
            return render(request, 'signup.html', {'error': 'Please provide all details.'})
        
    return render(request, 'signup.html')

@login_required(login_url='login')
def book_appointment(request, doctor_id=None):
    if request.method == 'POST':
        from django.utils import timezone
        
        doc_id = request.POST.get('doctor_id') or doctor_id
        if doc_id:
            doctor = Doctor.objects.filter(id=doc_id).first()
        else:
            doctor = Doctor.objects.first()
            
        patient_name_input = request.POST.get('patient_name')
        
        if patient_name_input:
            import uuid
            # Create a unique user and patient profile just for this name
            unique_username = "guest_" + uuid.uuid4().hex[:8]
            new_user = User.objects.create(username=unique_username, first_name=patient_name_input, role='patient')
            patient = Patient.objects.create(user=new_user)
        else:
            patient = getattr(request.user, 'patient_profile', Patient.objects.first())
            
        is_emergency = request.POST.get('is_emergency') == 'yes'
        appt_date_str = request.POST.get('date')
        if appt_date_str:
            from datetime import datetime
            try:
                appt_date = datetime.strptime(appt_date_str, '%Y-%m-%d').date()
            except ValueError:
                appt_date = timezone.now().date()
        else:
            appt_date = timezone.now().date()
            
        if doctor and patient:
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=appt_date,
                time=timezone.now().time(),
                status='pending',
                is_emergency=is_emergency
            )
            
        msg = "Emergency Appointment booked successfully!" if is_emergency else "Appointment booked successfully! Status: Pending"
        messages.success(request, msg)
        
        # Notify all teachers about the appointment
        patient_display_name = patient_name_input or request.user.first_name or request.user.username
        doctor_display_name = f"Dr. {doctor.user.first_name} {doctor.user.last_name}" if doctor else "Unknown"
        
        teachers = User.objects.filter(role='teacher')
        for teacher in teachers:
            if is_emergency:
                message = f"EMERGENCY: Student '{patient_display_name}' has requested an emergency appointment with {doctor_display_name}."
            else:
                message = f"Student '{patient_display_name}' has booked an appointment with {doctor_display_name}. Status: Pending."
            
            Notification.objects.create(
                user=teacher,
                message=message
            )
                
        return redirect('requested_appointments')
        
    busy_doctors = Appointment.objects.filter(status='pending').values_list('doctor_id', flat=True)
    doctors = Doctor.objects.exclude(id__in=busy_doctors)
    return render(request, 'doctors pescribtion.html', {'doctors': doctors, 'selected_doc_id': doctor_id})

@login_required(login_url='login')
def my_schedule(request):
    if request.user.role == 'doctor':
        try:
            doctor_profile = request.user.doctor_profile
            schedules = Appointment.objects.filter(doctor=doctor_profile).order_by('-date', '-time')
        except Doctor.DoesNotExist:
            schedules = []
    elif request.user.role == 'admin':
        schedules = Appointment.objects.all().order_by('-date', '-time')
    else:
        schedules = []
        
    return render(request, 'doctors appointment schedule.html', {'schedules': schedules})

@login_required(login_url='login')
def doctors_list(request):
    busy_doctors = Appointment.objects.filter(status='pending').values_list('doctor_id', flat=True)
    doctors = Doctor.objects.exclude(id__in=busy_doctors)
    return render(request, 'doctors_list.html', {'doctors': doctors, 'title': 'All Doctors Info'})

@login_required(login_url='login')
def available_doctors(request):
    busy_doctors = Appointment.objects.filter(status='pending').values_list('doctor_id', flat=True)
    doctors = Doctor.objects.exclude(id__in=busy_doctors)
    return render(request, 'doctors_list.html', {'doctors': doctors, 'title': 'Available Doctors'})

@login_required(login_url='login')
def accept_appointment(request, appt_id):
    if request.user.role == 'doctor':
        try:
            appt = Appointment.objects.get(id=appt_id, doctor=request.user.doctor_profile)
            appt.status = 'accepted'
            appt.save()
            messages.success(request, f"Request from {appt.patient.user.first_name} has been Accepted!")
        except Exception as e:
            pass
    return redirect('requested_appointments')

@login_required(login_url='login')
def requested_appointments(request):
    if request.user.role == 'doctor':
        appointments = Appointment.objects.filter(doctor=request.user.doctor_profile, status='pending').order_by('-date', '-time')
    elif request.user.role == 'admin':
        appointments = Appointment.objects.filter(status='pending').order_by('-date', '-time')
    else:
        try:
            appointments = Appointment.objects.filter(patient=request.user.patient_profile, status='pending').order_by('-date', '-time')
        except:
            appointments = []
    return render(request, 'requested_appointments.html', {'appointments': appointments})

@login_required(login_url='login')
def teacher_dashboard(request):
    """Teacher notification dashboard - teachers can see all student appointments"""
    if request.user.role != 'teacher':
        messages.error(request, "Only teachers can access this page.")
        return redirect('dashboard')
    
    # Get all notifications for this teacher
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    # Get all pending appointments so teacher can see current status
    pending_appointments = Appointment.objects.filter(status='pending').order_by('-date', '-time')
    accepted_appointments = Appointment.objects.filter(status='accepted').order_by('-date', '-time')
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'pending_appointments': pending_appointments,
        'accepted_appointments': accepted_appointments,
    }
    return render(request, 'teacher_dashboard.html', context)

@login_required(login_url='login')
def mark_notification_read(request, notif_id):
    """Mark a single notification as read"""
    if request.user.role == 'teacher':
        try:
            notif = Notification.objects.get(id=notif_id, user=request.user)
            notif.is_read = True
            notif.save()
        except Notification.DoesNotExist:
            pass
    return redirect('teacher_dashboard')

@login_required(login_url='login')
def mark_all_notifications_read(request):
    """Mark all notifications as read for the teacher"""
    if request.user.role == 'teacher':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
    return redirect('teacher_dashboard')

@login_required(login_url='login')
def check_new_notifications(request):
    """API endpoint for real-time notification polling on teacher dashboard"""
    if request.user.role != 'teacher':
        return JsonResponse({'notifications': []})
    
    last_check = request.GET.get('since', '')
    
    if last_check:
        from datetime import datetime, timezone as tz
        try:
            last_check_dt = datetime.fromisoformat(last_check)
            new_notifs = Notification.objects.filter(
                user=request.user,
                created_at__gt=last_check_dt
            ).order_by('-created_at')
        except (ValueError, TypeError):
            new_notifs = Notification.objects.filter(
                user=request.user, is_read=False
            ).order_by('-created_at')[:5]
    else:
        new_notifs = Notification.objects.none()
    
    data = [{
        'id': n.id,
        'message': n.message,
        'created_at': n.created_at.isoformat(),
        'is_read': n.is_read
    } for n in new_notifs]
    
    from django.utils import timezone
    return JsonResponse({
        'notifications': data,
        'server_time': timezone.now().isoformat(),
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
    })
