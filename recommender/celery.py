from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

ENV_VAR = os.environ.get("ENV", "local")
settings_module = "find_your_trip_bd." + ENV_VAR + "_settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

app = Celery("find_your_trip_bd")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    try:
        from recommender.tasks import scheduled_cache_district_data, load_districts_task

        load_districts_task.apply_async(countdown=30)
        scheduled_cache_district_data.apply_async(countdown=120)

    except Exception as e:
        print(f"Error in setup_periodic_tasks: {e}")
