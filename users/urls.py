from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('signup/', views.student_signup, name='student_signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_user, name='logout'),
    path('register-patient/', views.register_patient, name='register_patient'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('book-appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment_with_doc'),
    path('my-schedule/', views.my_schedule, name='my_schedule'),
    path('doctors/', views.doctors_list, name='doctors_list'),
    path('doctors/available/', views.available_doctors, name='available_doctors'),
    path('appointments/requested/', views.requested_appointments, name='requested_appointments'),
    path('appointments/accept/<int:appt_id>/', views.accept_appointment, name='accept_appointment'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('notification/read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_read'),
    path('api/notifications/', views.check_new_notifications, name='check_notifications'),
]