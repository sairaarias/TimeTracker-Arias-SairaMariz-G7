from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'department', 'employee_id', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'department')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_id')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('TimeTracker Custom Details', {
            'fields': ('role', 'contact_number', 'department', 'employee_id', 'profile_photo')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('TimeTracker Custom Details', {
            'fields': ('role', 'email', 'contact_number', 'department', 'employee_id', 'profile_photo')
        }),
    )
