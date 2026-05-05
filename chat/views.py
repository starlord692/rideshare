from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Message
from rides.models import Ride, RideRequest

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'ride', 'sender', 'sender_name', 'content', 'timestamp']

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ride_id = self.kwargs['ride_id']
        return Message.objects.filter(ride_id=ride_id).order_by('timestamp')

    def list(self, request, *args, **kwargs):
        ride_id = self.kwargs['ride_id']
        try:
            ride = Ride.objects.get(id=ride_id)
            # Check if user is driver or accepted passenger
            is_driver = ride.driver == request.user
            is_accepted_passenger = RideRequest.objects.filter(ride=ride, passenger=request.user, status='accepted').exists()

            if not (is_driver or is_accepted_passenger):
                return Response(
                    {"error": "Chat unlocks after ride owner accepts your request."},
                    status=status.HTTP_403_FORBIDDEN
                )

            return super().list(request, *args, **kwargs)
        except Ride.DoesNotExist:
            return Response({"error": "Ride not found."}, status=status.HTTP_404_NOT_FOUND)
