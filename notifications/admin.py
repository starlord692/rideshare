from django.contrib import admin
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    # Show: id, recipient, short message preview, notification_type, is_read, created_at
    list_display = ('id', 'recipient', 'short_message', 'notification_type', 'is_read', 'created_at')
    
    # Filter by is_read, notification_type
    list_filter = ('is_read', 'notification_type', 'created_at')
    
    # Search by message and recipient username
    search_fields = ('message', 'recipient__username')
    
    # Ordering by newest notification first
    ordering = ('-created_at',)

    def short_message(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Message Preview'

admin.site.register(Notification, NotificationAdmin)
