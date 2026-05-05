import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from rides.models import Ride, RideRequest

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.ride_id = self.scope['url_route']['kwargs']['ride_id']
        self.room_group_name = f'chat_{self.ride_id}'

        logger.info(f"WebSocket connect attempt: User {self.user} for Ride {self.ride_id}")

        if not self.user.is_authenticated:
            logger.warning(f"Unauthenticated user {self.user} tried to connect to chat.")
            await self.close()
            return

        # Check permission
        permission = await self.has_chat_permission()
        if not permission:
            logger.warning(f"User {self.user} denied access to chat for Ride {self.ride_id}")
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket connected: User {self.user} joined room {self.room_group_name}")

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnect: User {self.user} left room {self.room_group_name} with code {close_code}")
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_content = text_data_json['message']

            logger.info(f"Message received from {self.user} in Ride {self.ride_id}: {message_content[:50]}...")

            # Save message to database
            saved_msg = await self.save_message(message_content)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'sender': self.user.username,
                    'timestamp': saved_msg.timestamp.strftime('%I:%M %p')
                }
            )
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event.get('timestamp', '')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def has_chat_permission(self):
        try:
            ride = Ride.objects.get(id=self.ride_id)
            if ride.driver == self.user:
                return True
            # Check for accepted ride request
            return RideRequest.objects.filter(ride=ride, passenger=self.user, status='accepted').exists()
        except Ride.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error checking chat permission: {str(e)}")
            return False

    @database_sync_to_async
    def save_message(self, content):
        ride = Ride.objects.get(id=self.ride_id)
        return Message.objects.create(ride=ride, sender=self.user, content=content)
