from django.shortcuts import render
from health_check.views import MainView
from django.http import JsonResponse
from rest_framework import status, viewsets
from django.db import connection
from utils.logging import logger
from recommender.services.cache_district_data import collect_and_cache_district_data
from django.core.cache import cache


# Create your views here.


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

        print(collect_and_cache_district_data())
        example = cache.get("district_data_Dhaka_23.7115253_90.4111451")
        if example:
            logger.info(f"Cached data: {example}")
        else:
            logger.info("No cached data found.")

        logger.info(f"Health check status: {status}")
        return JsonResponse({"status": status, "database": db_status}, status=status)
