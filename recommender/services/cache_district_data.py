import json
from recommender.services.district_data import load_districts
from recommender.services.weather_service import (
    get_avg_temp_at_2pm,
    get_temp_at_2pm_by_date,
)
from recommender.services.air_quality_service import get_air_quality, get_pm25_by_date
import time
from django.core.cache import cache
from utils.logging import logger
import numpy as np


CACHE_TTL = 60 * 60


def collect_and_cache_district_data():
    districts = load_districts()

    if not districts:
        logger.error("No district data available.")
        return

    logger.info(f"Found {len(districts)} districts to process.")

    for district in districts:
        name = district["name"]
        lat = district["lat"]
        lon = district["long"]
        cache_key = f"district_data_{name}_{lat}_{lon}"

        try:
            avg_temp = get_avg_temp_at_2pm(lat, lon)
            air_quality = get_air_quality(lat, lon)
        except Exception as e:
            logger.error(f"Error fetching data for {name}: {e}")
            continue

        if avg_temp is not None and air_quality is not None:
            district_data = {
                "name": name,
                "lat": lat,
                "long": lon,
                "avg_temp": avg_temp,
                "air_quality": air_quality,
            }

            cache.set(cache_key, json.dumps(district_data), timeout=CACHE_TTL)
            logger.info(f"Cached data for {name}: {district_data}")
        else:
            logger.error(f"Failed to fetch data for {name}. Skipping...")
            continue


def cache_daily_district_data():
    districts = load_districts()
    for district in districts:
        name = district["name"]
        lat = district["lat"]
        lon = district["long"]

        try:
            temps = get_temp_at_2pm_by_date(lat, lon)
            pm25s = get_pm25_by_date(lat, lon)
        except Exception as e:
            logger.error(f"Daily fetch failed for {name}: {e}")
            continue

        if (
            temps is not None
            and not temps.empty
            and pm25s is not None
            and not pm25s.empty
        ):
            common_dates = set(temps.index) & set(pm25s.index)
            logger.info(f"Common dates found for {name}: {common_dates}")

            if common_dates:
                for date in common_dates:
                    avg_temp = temps[date]
                    pm25 = pm25s[date]

                    avg_temp = None if np.isnan(avg_temp) else round(float(avg_temp), 2)
                    pm25 = None if np.isnan(pm25) else round(float(pm25), 2)

                    cache_key = f"district_date_{name}_{lat}_{lon}_{date}"
                    district_data = {
                        "name": name,
                        "lat": lat,
                        "long": lon,
                        "avg_temp": avg_temp,
                        "air_quality": pm25,
                    }
                    print(district_data)
                    cache.set(cache_key, json.dumps(district_data), timeout=CACHE_TTL)
                    logger.info(f"Cached daily data for {name} on {date}")
            else:
                logger.warning(
                    f"No common dates found for {name} between temperature and air quality data."
                )
        else:
            logger.error(f"Failed to fetch daily data for {name}. Skipping...")
            continue
