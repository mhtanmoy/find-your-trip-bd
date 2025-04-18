from django.shortcuts import render
from health_check.views import MainView
from django.http import JsonResponse
from rest_framework import status, viewsets
from django.db import connection
from utils.logging import logger
from recommender.services.cache_district_data import collect_and_cache_district_data
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from utils.response_wrapper import ResponseWrapper
import re
import json


class HealthCheckCustomView(MainView):
    def get(self, request, *args, **kwargs):

        plugins = []
        status = 200

        if "*/*" in request.META.get("HTTP_ACCEPT", ""):
            return self.render_to_response_json(plugins, status)

    def render_to_response_json(self, plugins, status):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = "Database is healthy"
        except Exception as e:
            db_status = "Database not healthy"
            logger.error(f"Database check failed: {e}")
            status = 503  # 503 Service Unavailable

        logger.info(f"Health check status: {status}")
        return JsonResponse({"status": status, "database": db_status}, status=status)


class TopDistrictViewSet(viewsets.ViewSet):
    def list(self, request):
        keys = cache.keys("district_data_*")
        district_data = []
        for key in keys:
            data = cache.get(key)
            if data:
                district_data.append(json.loads(data))

        district_data = sorted(
            district_data, key=lambda x: (x["avg_temp"], x["air_quality"])
        )

        if not district_data:
            logger.warning("No district data found in cache.")
            return ResponseWrapper(
                status=status.HTTP_404_NOT_FOUND,
                error_message="No district data found.",
            )
        logger.info(f"Total districts found: {len(district_data)}")

        # pagination
        paginator = PageNumberPagination()
        # default page size 10, take from params
        paginator.page_size = request.query_params.get("page_size", 10)
        page = paginator.paginate_queryset(district_data, request, view=self)
        if page is not None:
            district_data = paginator.get_paginated_response(page).data
        else:
            district_data = paginator.get_paginated_response(district_data).data

        return ResponseWrapper(
            data=district_data,
            status=status.HTTP_200_OK,
        )
