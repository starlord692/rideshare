from django.contrib import admin
from .models import Ride, RideRequest

class RideAdmin(admin.ModelAdmin):
    # Show: id, driver, pickup_location, dropoff_location, departure_time (and split date/time if needed)
    list_display = ('id', 'driver', 'pickup_location', 'dropoff_location', 'departure_time', 'status', 'available_seats')
    
    # Filter by status, departure_time (representing date/time)
    list_filter = ('status', 'departure_time')
    
    # Search by pickup_location, dropoff_location, driver username
    search_fields = ('pickup_location', 'dropoff_location', 'driver__username')
    
    # Ordering by latest ride first
    ordering = ('-departure_time',)

class RideRequestAdmin(admin.ModelAdmin):
    # Show: id, ride, passenger, status, created_at
    list_display = ('id', 'ride', 'passenger', 'status', 'created_at')
    
    # Filter by status
    list_filter = ('status',)
    
    # Search by passenger username, ride pickup/drop locations
    search_fields = ('passenger__username', 'ride__pickup_location', 'ride__dropoff_location')
    
    # Ordering by newest request first
    ordering = ('-created_at',)

admin.site.register(Ride, RideAdmin)
admin.site.register(RideRequest, RideRequestAdmin)
