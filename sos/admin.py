from django.contrib import admin
from .models import EmergencyAlert

class EmergencyAlertAdmin(admin.ModelAdmin):
    # Show: id, user, emergency_contact_phone, latitude, longitude, status, created_at
    list_display = ('id', 'user', 'emergency_contact_phone', 'latitude', 'longitude', 'status', 'created_at')
    
    # Filter by status
    list_filter = ('status',)
    
    # Search by username and emergency contact phone
    search_fields = ('user__username', 'emergency_contact_phone')
    
    # Ordering by newest SOS first
    ordering = ('-created_at',)
    
    # Mark important fields readonly
    readonly_fields = ('user', 'ride', 'latitude', 'longitude', 'emergency_contact_name', 'emergency_contact_phone', 'created_at')

admin.site.register(EmergencyAlert, EmergencyAlertAdmin)
