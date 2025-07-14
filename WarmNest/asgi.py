# """
# ASGI config for WarmNest project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WarmNest.settings')

# application = get_asgi_application()

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
print("ASGI is loading...")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WarmNest.settings')
django.setup()

import User.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            User.routing.websocket_urlpatterns
        )
    ),
})
