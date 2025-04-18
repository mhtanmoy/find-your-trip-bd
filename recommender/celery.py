from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.signals import worker_ready

ENV_VAR = os.environ.get("ENV", "local")
settings_module = "find_your_trip_bd." + ENV_VAR + "_settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

app = Celery("find_your_trip_bd")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@worker_ready.connect
def at_worker_ready(sender, **kwargs):
    """
    Called when the worker is fully booted and ready to accept tasks.
    Used for initial one-time async job calls.
    """
    with sender.app.connection() as conn:
        try:
            from recommender.tasks import (
                scheduled_cache_district_data,
                load_districts_task,
                cache_daily_district_data_task,
            )

            print(">> Running initial data caching tasks...")

            load_districts_task.apply_async(countdown=0, connection=conn)
            scheduled_cache_district_data.apply_async(countdown=30, connection=conn)
            cache_daily_district_data_task.apply_async(countdown=60, connection=conn)

        except Exception as e:
            print(f"Error in initial task dispatch: {e}")
