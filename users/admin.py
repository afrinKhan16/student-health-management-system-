from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Patient, Doctor, Schedule, Appointment, Prescription, Bill, Notification

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Configuration', {'fields': ('role',)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Schedule)
admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(Bill)
admin.site.register(Notification)