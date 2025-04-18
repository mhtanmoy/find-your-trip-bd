import json
from recommender.services.district_data import load_districts
from recommender.services.weather_service import get_avg_temp_at_2pm
from recommender.services.air_quality_service import get_air_quality
import time
from django.core.cache import cache
from utils.logging import logger


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
