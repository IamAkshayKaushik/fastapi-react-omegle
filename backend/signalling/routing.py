"""
setting up WebSocket URL patterns for a Django application.
"""


from django.urls import path
from .consumer import SignallingConsumer

websocket_urlpatterns = [
    # re_path(r'^ws/chat/(?P<room_name>\w+)/$', SignallingConsumer.as_asgi()),
    path("ws/signal/", SignallingConsumer.as_asgi(), name="signal",),
]
