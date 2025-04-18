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
from drf_yasg.utils import swagger_auto_schema
from recommender.serializers import TravelQueryParamsSerializer, TopDistrictsSerializer
from datetime import datetime
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
    @swagger_auto_schema(
        operation_summary="Get top districts based on temperature and air quality",
        operation_description="This endpoint provides a list of top districts based on temperature and air quality.",
        query_serializer=TopDistrictsSerializer,
    )
    def list(self, request):
        keys = cache.keys("district_data_*")
        if not keys:
            logger.warning("No district data found in cache.")
            return ResponseWrapper(
                status=status.HTTP_404_NOT_FOUND,
                error_message="No district data found.",
                error_code=404,
            )

        district_data = []
        for key in keys:
            data = cache.get(key)
            if data:
                district_data.append(json.loads(data))

        if not district_data:
            logger.warning("No district data found in cache after filtering.")
            return ResponseWrapper(
                status=status.HTTP_404_NOT_FOUND,
                error_message="No district data found.",
                error_code=404,
            )

        district_data = sorted(
            district_data, key=lambda x: (x["avg_temp"], x["air_quality"])
        )
        logger.info(f"Total districts found: {len(district_data)}")

        # pagination
        paginator = PageNumberPagination()
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


class TravelRecommendationViewSet(viewsets.ViewSet):

    @swagger_auto_schema(
        operation_summary="Get travel recommendation based on location and date",
        operation_description="This endpoint provides a travel recommendation based on the current location and destination district's temperature and air quality.",
        query_serializer=TravelQueryParamsSerializer,
    )
    def list(self, request):
        try:
            lat, lon, des_name, date = self.extract_and_validate_params(request)
            current_location_data, destination_data = self.fetch_cached_data(
                lat, lon, des_name, date
            )
        except Exception as e:
            logger.error(f"Error extracting parameters: {e}")
            return ResponseWrapper(
                status=status.HTTP_400_BAD_REQUEST,
                error_message=f"Error extracting parameters: {e}",
                error_code=400,
            )

        current_temp, destination_temp, current_air_quality, destination_air_quality = (
            self.extract_data(current_location_data, destination_data)
        )
        if None in (
            current_temp,
            destination_temp,
            current_air_quality,
            destination_air_quality,
        ):
            return ResponseWrapper(
                status=status.HTTP_404_NOT_FOUND,
                error_message="Data not found for the given location or destination.",
                error_code=404,
            )

        recommendation, reasons, short_reason = self.generate_recommendation(
            current_temp, destination_temp, current_air_quality, destination_air_quality
        )

        return ResponseWrapper(
            status=status.HTTP_200_OK,
            data={
                "recommendation": recommendation,
                "destination": destination_data["name"],
                "current_temperature": current_temp,
                "destination_temperature": destination_temp,
                "current_air_quality": current_air_quality,
                "destination_air_quality": destination_air_quality,
                "reasons": reasons,
                "short_reason": short_reason,
            },
        )

    def extract_and_validate_params(self, request):
        lat = request.query_params.get("lat")
        lon = request.query_params.get("lon")
        des_name = request.query_params.get("name")
        date = request.query_params.get("date")

        if not all([lat, lon, des_name, date]):
            logger.error("Missing required parameters.")
            raise ValueError("Missing required parameters.")

        try:
            lat = float(lat)
            lon = float(lon)
            date = datetime.strptime(date, "%Y-%m-%d").date()
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid parameter format: {e}")
            return ResponseWrapper(
                status=status.HTTP_400_BAD_REQUEST,
                error_message="Invalid parameter format.",
                error_code=400,
            )

        return lat, lon, des_name, date

    def fetch_cached_data(self, lat, lon, des_name, date):
        current_location_key = cache.keys(f"district_date_*{lat}_{lon}_{date}*")
        destination_key = cache.keys(f"district_date_*{des_name}_*_{date}*")

        if not current_location_key or not destination_key:
            logger.error(
                f"District data not found for current location: {lat}, {lon} or destination: {des_name}."
            )
            raise ValueError(
                "District data not found for the given location or destination."
            )

        try:
            current_location_data = json.loads(cache.get(current_location_key[0]))
            destination_data = json.loads(cache.get(destination_key[0]))
        except (TypeError, json.JSONDecodeError) as e:
            logger.error(f"Error decoding cached data: {e}")
            raise ValueError("Error decoding cached data. Please try again later.")

        return current_location_data, destination_data

    def extract_data(self, current_location_data, destination_data):
        current_temp = current_location_data.get("avg_temp")
        destination_temp = destination_data.get("avg_temp")
        current_air_quality = current_location_data.get("air_quality")
        destination_air_quality = destination_data.get("air_quality")
        return (
            current_temp,
            destination_temp,
            current_air_quality,
            destination_air_quality,
        )

    def generate_recommendation(
        self,
        current_temp,
        destination_temp,
        current_air_quality,
        destination_air_quality,
    ):
        flag = False
        reasons = []
        short_reason = ""

        temp_diff_val = current_temp - destination_temp
        air_quality_diff_val = current_air_quality - destination_air_quality

        # Temperature comparison
        if destination_temp < current_temp:
            flag = True
            reasons.append(
                f"Your destination is {round(abs(temp_diff_val), 1)}°C cooler."
            )
        elif destination_temp > current_temp:
            reasons.append(
                f"Your destination is {round(abs(temp_diff_val), 1)}°C warmer."
            )
        else:
            reasons.append("Both places have the same temperature.")

        # Air quality comparison
        if destination_air_quality < current_air_quality:
            flag = True
            reasons.append(
                f"Your destination has better air quality by {round(abs(air_quality_diff_val), 1)} PM2.5 points."
            )
        elif destination_air_quality > current_air_quality:
            reasons.append(
                f"Your destination has worse air quality by {round(abs(air_quality_diff_val), 1)} PM2.5 points."
            )
        else:
            reasons.append("Both places have similar air quality.")

        # Generate short reason
        if (
            destination_temp > current_temp
            and destination_air_quality > current_air_quality
        ):
            short_reason = "Your destination is hotter and has worse air quality than your current location. It’s better to stay where you are."
        elif (
            destination_temp < current_temp
            and destination_air_quality < current_air_quality
        ):
            short_reason = f"Your destination is {round(abs(temp_diff_val), 1)}°C cooler and has significantly better air quality. Enjoy your trip!"
        elif destination_temp < current_temp:
            short_reason = f"Your destination is {round(abs(temp_diff_val), 1)}°C cooler. Enjoy your trip!"
        elif destination_air_quality < current_air_quality:
            short_reason = "Your destination has significantly better air quality. Enjoy your trip!"
        else:
            short_reason = "Both places are similar in temperature and air quality."

        recommendation = "Recommended" if flag else "Not Recommended"
        return recommendation, reasons, short_reason
