import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path

from register.consumers import TokenConsumer


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "penguin.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r'^ws/register/token/$', TokenConsumer.as_asgi()),
        ])
    ),
})
