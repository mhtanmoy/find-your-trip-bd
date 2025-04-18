import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
from utils.logging import logger
from django.conf import settings


def get_avg_temp_at_2pm(lat, lon):
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
        "timezone": "Asia/Dhaka",
        "forecast_days": 7,
    }
    try:
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            )
        }

        hourly_data["temperature_2m"] = hourly_temperature_2m

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        avg = hourly_dataframe[hourly_dataframe["date"].dt.hour == 14][
            "temperature_2m"
        ].mean()
        logger.info(
            f"Average temperature at 2 PM: {avg}°C for coordinates ({lat}, {lon})"
        )
        return round(float(avg), 2)

    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
        return None


def get_temp_at_2pm_by_date(lat, lon):
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
        "timezone": "Asia/Dhaka",
        "forecast_days": 7,
    }
    try:
        responses = openmeteo.weather_api(url, params=params)
        logger.info(f"Weather API response: {responses.status_code}")
        response = responses[0]
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

        dates = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )

        df = pd.DataFrame({"date": dates, "temp": hourly_temperature_2m})
        df = df[df["date"].dt.hour == 14]
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

        return df.set_index("date")["temp"].to_dict()

    except Exception as e:
        logger.error(f"Weather daily fetch failed: {e}")
        return None
