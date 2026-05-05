from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('driver', 'Driver'),
        ('passenger', 'Passenger'),
        ('both', 'Both'),
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.URLField(blank=True, null=True) # URL to image
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='passenger')
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Driver specific
    vehicle_details = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.username
