from django.shortcuts import render
from health_check.views import MainView
from django.http import JsonResponse
from rest_framework import status, viewsets
from django.db import connection
import logging


# Create your views here.
logger = logging.getLogger(__name__)


class HealthCheckCustomView(MainView):
    def get(self, request, *args, **kwargs):

        plugins = []
        status = 200

        if "*/*" in request.META.get("HTTP_ACCEPT", ""):
            return self.render_to_response_json(plugins, status)

    def render_to_response_json(self, plugins, status):  # customize JSON output
        # Check if the database is available
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = "Database is healthy"
        except Exception as e:
            db_status = "Database not healthy"
            logger.error(f"Database check failed: {e}")
            status = 503

        return JsonResponse({"status": status, "database": db_status}, status=status)
