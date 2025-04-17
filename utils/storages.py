from django.conf import settings
from django.contrib.staticfiles.storage import StaticFilesStorage
from django.contrib.staticfiles.utils import check_settings, matches_patterns
from django.core.exceptions import ImproperlyConfigured


class CustomStaticFilesStorage(StaticFilesStorage):
    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = settings.STATIC_ROOT
        if base_url is None:
            base_url = settings.STATIC_URL
        base_url = f"{base_url}"
        check_settings(base_url)
        super().__init__(location, base_url, *args, **kwargs)
        # FileSystemStorage fallbacks to MEDIA_ROOT when location
        # is empty, so we restore the empty value.
        if not location:
            self.base_location = None
            self.location = None
