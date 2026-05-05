from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Ride, RideRequest
from .serializers import RideSerializer, RideRequestSerializer
from notifications.models import Notification
import math

def haversine(lat1, lon1, lat2, lon2):
    # Radius of earth in kilometers
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class RideListCreateView(generics.ListCreateAPIView):
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Public rides: open/upcoming/active/ongoing, seats available, not created by the requester
        status_list = ['open', 'upcoming', 'active', 'ongoing']
        queryset = Ride.objects.filter(status__in=status_list, available_seats__gt=0)
        
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(driver=self.request.user)
            
        # Optional search filters
        pickup = self.request.query_params.get('pickup')
        dropoff = self.request.query_params.get('dropoff')
        
        if pickup:
            queryset = queryset.filter(pickup_location__icontains=pickup)
        if dropoff:
            queryset = queryset.filter(dropoff_location__icontains=dropoff)
            
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        # Check if user is a driver or both
        if self.request.user.role not in ['driver', 'both']:
            raise ValidationError("Only drivers can offer rides.")

        # Check for active ride
        active_ride_exists = Ride.objects.filter(
            driver=self.request.user,
            status__in=["open", "upcoming", "active", "ongoing"]
        ).exists()
        
        if active_ride_exists:
            raise ValidationError("You already have an active ride. Complete or cancel it before offering a new ride.")
            
        serializer.save(driver=self.request.user, available_seats=serializer.validated_data.get('total_seats', 4))

class MyOfferedRidesView(generics.ListAPIView):
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ride.objects.filter(driver=self.request.user).order_by('-created_at')

class MyRideRequestsView(generics.ListAPIView):
    serializer_class = RideRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RideRequest.objects.filter(passenger=self.request.user).order_by('-created_at')

class RideRequestsForRideView(generics.ListAPIView):
    serializer_class = RideRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        ride_id = self.kwargs['pk']
        return RideRequest.objects.filter(ride_id=ride_id, ride__driver=self.request.user).order_by('-created_at')

class RideRequestCreateView(generics.CreateAPIView):
    serializer_class = RideRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ride = serializer.validated_data['ride']
        
        if ride.driver == request.user:
            return Response({"error": "You cannot request to join your own ride."}, status=status.HTTP_400_BAD_REQUEST)
        if ride.available_seats < serializer.validated_data.get('seats_requested', 1):
            return Response({"error": "Not enough seats available."}, status=status.HTTP_400_BAD_REQUEST)
        if RideRequest.objects.filter(ride=ride, passenger=request.user).exists():
            return Response({"error": "You have already requested to join this ride."}, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        
        # Create notification for driver
        Notification.objects.create(
            recipient=ride.driver,
            title="New Ride Request",
            message=f"{request.user.username} has requested to join your ride.",
            notification_type='request_received',
            related_ride=ride,
            related_request=serializer.instance
        )
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)

class ApproveRideRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        ride_request = get_object_or_404(RideRequest.objects.select_for_update(), pk=pk)
        ride = ride_request.ride
        
        if ride.driver != request.user:
            return Response({"error": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
            
        if ride_request.status != 'pending':
            return Response({"error": "Request is not pending."}, status=status.HTTP_400_BAD_REQUEST)
            
        if ride.available_seats < ride_request.seats_requested:
            return Response({"error": "Not enough seats available."}, status=status.HTTP_400_BAD_REQUEST)
            
        ride_request.status = 'accepted'
        ride_request.save()
        
        ride.available_seats -= ride_request.seats_requested
        ride.save()
        
        # Notify passenger
        Notification.objects.create(
            recipient=ride_request.passenger,
            title="Ride Request Accepted",
            message=f"Your request to join the ride to {ride.dropoff_location} was accepted!",
            notification_type='request_accepted',
            related_ride=ride,
            related_request=ride_request
        )
        
        return Response(RideRequestSerializer(ride_request).data)

class RejectRideRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        ride_request = get_object_or_404(RideRequest.objects.select_for_update(), pk=pk)
        ride = ride_request.ride
        
        if ride.driver != request.user:
            return Response({"error": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
            
        if ride_request.status != 'pending':
            return Response({"error": "Request is not pending."}, status=status.HTTP_400_BAD_REQUEST)
            
        ride_request.status = 'rejected'
        ride_request.save()
        
        # Notify passenger
        Notification.objects.create(
            recipient=ride_request.passenger,
            title="Ride Request Rejected",
            message=f"Your request to join the ride to {ride.dropoff_location} was rejected.",
            notification_type='request_rejected',
            related_ride=ride,
            related_request=ride_request
        )
        
        return Response(RideRequestSerializer(ride_request).data)

class CompleteRideView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        ride = get_object_or_404(Ride, pk=pk, driver=request.user)
        
        # Check if trip time has passed
        from django.utils import timezone
        if timezone.now() < ride.departure_time:
            return Response(
                {"error": "Trip is yet to come. You can complete this ride only after the scheduled trip time."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        ride.status = 'completed'
        ride.save()
        
        # Notify accepted passengers
        accepted_requests = ride.requests.filter(status='accepted')
        for req in accepted_requests:
            Notification.objects.create(
                recipient=req.passenger,
                title="Ride Completed",
                message=f"The ride to {ride.dropoff_location} has been marked as completed.",
                notification_type='general',
                related_ride=ride
            )
            
        return Response({'status': 'completed'})

class CancelRideView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        ride = get_object_or_404(Ride, pk=pk, driver=request.user)
        ride.status = 'cancelled'
        ride.save()
        
        # Notify accepted passengers
        accepted_requests = ride.requests.filter(status='accepted')
        for req in accepted_requests:
            Notification.objects.create(
                recipient=req.passenger,
                title="Ride Cancelled",
                message=f"The ride to {ride.dropoff_location} has been cancelled by the driver.",
                notification_type='general',
                related_ride=ride
            )
            
        return Response({'status': 'cancelled'})

class RideDetailView(generics.RetrieveAPIView):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
