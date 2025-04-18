import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from utils.logging import logger
from django.conf import settings


def get_air_quality(lat, lon):
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["pm2_5"],
        "timezone": "Asia/Dhaka",
        "forecast_days": 7,
    }
    try:
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_pm2_5 = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            )
        }

        hourly_data["pm2_5"] = hourly_pm2_5
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        avg = hourly_dataframe[hourly_dataframe["date"].dt.hour == 14]["pm2_5"].mean()
        logger.info(
            f"Average PM2.5 level at 2 PM: {avg} µg/m³ for coordinates ({lat}, {lon})"
        )
        return round(float(avg), 2)

    except Exception as e:
        logger.error(f"Air quality fetch failed: {e}")
        return None


def get_pm25_by_date(lat, lon):
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["pm2_5"],
        "timezone": "Asia/Dhaka",
        "forecast_days": 7,
    }

    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        hourly = response.Hourly()
        hourly_pm2_5 = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            )
        }

        hourly_data["pm2_5"] = hourly_pm2_5
        hourly_df = pd.DataFrame(data=hourly_data)

        # Filter only 2 PM entries and format date
        df_2pm = hourly_df[hourly_df["date"].dt.hour == 14].copy()
        df_2pm["date"] = df_2pm["date"].dt.strftime("%Y-%m-%d")

        # Return as { "2025-04-18": 15.2, ... }
        return df_2pm.set_index("date")["pm2_5"].round(2)

    except Exception as e:
        logger.error(f"Air quality daily fetch failed: {e}")
        return None
