from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    # Show: username, email, phone_number, role, emergency_contact_phone, is_active, last_login
    list_display = ('username', 'email', 'phone_number', 'role', 'emergency_contact_phone', 'is_active', 'last_login')
    
    # Filter by role, is_active
    list_filter = ('role', 'is_active', 'is_staff')
    
    # Search by username, email, phone_number
    search_fields = ('username', 'email', 'phone_number')
    
    # Ordering by newest user first (using date_joined as it exists in AbstractUser)
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('phone_number', 'role', 'profile_image', 'emergency_contact_name', 'emergency_contact_phone', 'vehicle_details')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Fields', {'fields': ('phone_number', 'role', 'emergency_contact_name', 'emergency_contact_phone')}),
    )

admin.site.register(User, CustomUserAdmin)
