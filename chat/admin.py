from django.contrib import admin
from .models import Message

class MessageAdmin(admin.ModelAdmin):
    # Show: id, sender, ride, short message preview, timestamp
    list_display = ('id', 'sender', 'ride', 'short_content', 'timestamp')
    
    # Search by message content and sender username
    search_fields = ('content', 'sender__username')
    
    # Filter by timestamp/date
    list_filter = ('timestamp',)
    
    # Ordering by newest message first
    ordering = ('-timestamp',)

    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Message Content'

admin.site.register(Message, MessageAdmin)
