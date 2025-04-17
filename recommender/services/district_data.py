import requests
from django.conf import settings
from django.core.cache import cache
from utils.logging import logger


def load_districts():
    try:
        # Check if the data is already cached
        cached_data = cache.get("district_data")
        if cached_data:
            return cached_data
        else:
            url = "https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json"
            response = requests.get(url)
            data = response.json()
            cache.set("district_data", data, timeout=60 * 60)
            logger.info("District data loaded from API and cached.")
            return data["districts"]

    except Exception as e:
        logger.error(f"Failed to load district data: {e}")
        return []
