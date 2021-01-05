import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "penguin.settings")
asgi_application = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import re_path
from register.consumers import RegistrationConsumer, TokenConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "penguin.settings")
asgi_application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": asgi_application,
    "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(
        URLRouter([
            re_path(r'^ws/register/token/$', TokenConsumer.as_asgi()),
            re_path(
                r'^ws/register/registration/$', RegistrationConsumer.as_asgi()
            ),
        ])
    )),
})
