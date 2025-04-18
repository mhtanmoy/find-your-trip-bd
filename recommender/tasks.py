from celery import shared_task
from recommender.services.cache_district_data import collect_and_cache_district_data
from recommender.services.district_data import load_districts


@shared_task
def scheduled_cache_district_data():
    return collect_and_cache_district_data()


@shared_task
def load_districts_task():
    return load_districts()
