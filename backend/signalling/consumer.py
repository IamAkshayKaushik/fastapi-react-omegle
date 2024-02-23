"""
Consumer file for signaling server
"""

from channels.generic.websocket import AsyncWebsocketConsumer


class SignallingConsumer(AsyncWebsocketConsumer):
    """
    Consumer class for signaling server
    """

    async def connect(self):
        """
        Called when a websocket connection is established
        """
        return await super().connect()

    async def disconnect(self, code):
        """
        Called when a websocket disconnects
        """
        return await super().disconnect(code)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Called when a websocket message is received
        """
        return await super().receive(text_data, bytes_data)
