import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('sos')

class SOSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Only allow authenticated users to connect
        if self.scope["user"].is_anonymous:
            logger.warning("Anonymous WebSocket connection attempt rejected.")
            await self.close()
            return

        await self.channel_layer.group_add("sos_alerts", self.channel_name)
        await self.accept()
        logger.info(f"WebSocket SOS connection accepted for user: {self.scope['user'].username}")

    async def disconnect(self, close_code):
        # Leave the group on disconnect
        if not self.scope["user"].is_anonymous:
            logger.info(f"WebSocket SOS disconnected for user: {self.scope['user'].username} (code: {close_code})")
        await self.channel_layer.group_discard("sos_alerts", self.channel_name)

    async def sos_alert(self, event):
        # Do not send the alert back to the same user who triggered it
        if self.scope["user"].id == event.get("sender_id"):
            return

        # Send the alert payload to the WebSocket
        logger.info(f"Forwarding SOS alert {event.get('alert_id')} to user: {self.scope['user'].username}")
        await self.send(text_data=json.dumps(event))
