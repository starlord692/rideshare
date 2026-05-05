import logging
import json
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import EmergencyAlert
from rest_framework import serializers
from rides.models import Ride
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger('sos')

class EmergencySerializer(serializers.ModelSerializer):
    ride_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = EmergencyAlert
        fields = ['latitude', 'longitude', 'ride_id']

class SOSCreateView(generics.CreateAPIView):
    serializer_class = EmergencySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        logger.info(f"SOS Triggered by Authenticated User: {user.username} (ID: {user.id})")
        
        # Log request body
        try:
            body = json.loads(request.body)
            logger.info(f"SOS payload: {body}")
        except:
            logger.info(f"SOS payload: {request.data}")

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"SOS Validation Failed for {user.username}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        lat = serializer.validated_data.get('latitude')
        lng = serializer.validated_data.get('longitude')
        ride_id = serializer.validated_data.get('ride_id')
        
        logger.info(f"coordinates received for {user.username}: Lat={lat}, Lng={lng}")
        
        contact_name = user.emergency_contact_name
        contact_phone = user.emergency_contact_phone
        
        warning = None
        if not contact_name or not contact_phone:
            logger.warning(f"User {user.username} has missing emergency contact info.")
            contact_name = contact_name or "Emergency Services"
            contact_phone = contact_phone or "911"
            warning = "Emergency contact details are incomplete in your profile."
        
        ride = None
        if ride_id:
            try:
                ride = Ride.objects.get(id=ride_id)
            except Ride.DoesNotExist:
                logger.warning(f"Ride ID {ride_id} not found for SOS.")

        try:
            alert = EmergencyAlert.objects.create(
                user=user,
                ride=ride,
                latitude=lat,
                longitude=lng,
                emergency_contact_name=contact_name,
                emergency_contact_phone=contact_phone,
                status='sent'
            )
            logger.info(f"EmergencyAlert saved id: {alert.id} for user: {user.username}")
            
            # Broadcast via WebSocket
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "sos_alerts",
                    {
                        "type": "sos_alert",
                        "alert_id": alert.id,
                        "sender_id": user.id,
                        "username": user.username,
                        "latitude": float(alert.latitude),
                        "longitude": float(alert.longitude),
                        "emergency_contact_phone": alert.emergency_contact_phone,
                        "created_at": alert.created_at.isoformat(),
                        "message": "Emergency SOS alert received",
                    }
                )
                logger.info(f"Broadcasted SOS alert {alert.id} to group sos_alerts")
            except Exception as broadcast_err:
                logger.error(f"Failed to broadcast SOS alert: {str(broadcast_err)}")

            response_data = {
                'success': True,
                'message': 'SOS sent',
                'emergency_contact_phone': contact_phone
            }
            if warning:
                response_data['warning'] = warning
                
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.exception(f"Exception during SOS trigger for {user.username}: {str(e)}")
            return Response({
                'success': False,
                'message': f"Failed to save SOS alert: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SOSListView(generics.ListAPIView):
    serializer_class = EmergencySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return EmergencyAlert.objects.all().order_by('-created_at')
        return EmergencyAlert.objects.filter(user=self.request.user).order_by('-created_at')
