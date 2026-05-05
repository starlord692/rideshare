import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SOSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Only allow authenticated users to connect
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add("sos_alerts", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group on disconnect
        await self.channel_layer.group_discard("sos_alerts", self.channel_name)

    async def sos_alert(self, event):
        # Do not send the alert back to the same user who triggered it
        if self.scope["user"].id == event.get("sender_id"):
            return

        # Send the alert payload to the WebSocket
        await self.send(text_data=json.dumps(event))
