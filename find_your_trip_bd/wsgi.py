"""
WSGI config for find_your_trip_bd project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


ENV_VAR = os.environ.get("ENV", "local")
settings_module = "find_your_trip_bd." + ENV_VAR + "_settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

application = get_wsgi_application()
