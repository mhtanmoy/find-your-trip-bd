from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

ENV_VAR = os.environ.get("ENV", "local")
settings_module = "find_your_trip_bd." + ENV_VAR + "_settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

app = Celery("find_your_trip_bd")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
