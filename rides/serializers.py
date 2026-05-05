from rest_framework import serializers
from .models import Ride, RideRequest

class RideSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.username', read_only=True)
    driver_rating = serializers.FloatField(read_only=True, default=5.0) # Mock default for now

    class Meta:
        model = Ride
        fields = '__all__'
        read_only_fields = ('driver', 'available_seats', 'status')

class RideRequestSerializer(serializers.ModelSerializer):
    passenger_name = serializers.CharField(source='passenger.username', read_only=True)
    passenger_phone = serializers.CharField(source='passenger.phone_number', read_only=True)
    passenger_email = serializers.CharField(source='passenger.email', read_only=True)
    ride_pickup = serializers.CharField(source='ride.pickup_location', read_only=True)
    ride_dropoff = serializers.CharField(source='ride.dropoff_location', read_only=True)
    ride_date = serializers.DateTimeField(source='ride.departure_time', read_only=True)

    class Meta:
        model = RideRequest
        fields = '__all__'
        read_only_fields = ('passenger', 'status')
