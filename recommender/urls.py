from django.urls import path
from rest_framework import routers
from recommender.views import HealthCheckCustomView, TopDistrictViewSet
from django.conf import settings
from django.conf.urls.static import static


class OptionalSlashRouter(routers.SimpleRouter):
    def __init__(self):
        super().__init__()
        self.trailing_slash = "/?"


router = OptionalSlashRouter()
router.register(r"top_districts", TopDistrictViewSet, basename="top_districts")


urlpatterns = [
    path("health_check/", HealthCheckCustomView.as_view(), name="health_check"),
] + router.urls

if settings.DEBUG:
    urlpatterns = urlpatterns + static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
