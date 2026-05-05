from django.db import models
from django.conf import settings
from rides.models import Ride, RideRequest

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('request_received', 'Request Received'),
        ('request_accepted', 'Request Accepted'),
        ('request_rejected', 'Request Rejected'),
        ('general', 'General')
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='general')
    is_read = models.BooleanField(default=False)
    related_ride = models.ForeignKey(Ride, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    related_request = models.ForeignKey(RideRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
