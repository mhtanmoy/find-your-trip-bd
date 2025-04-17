from django.urls import path
from rest_framework import routers
from recommender.views import HealthCheckCustomView


class OptionalSlashRouter(routers.SimpleRouter):
    def __init__(self):
        super().__init__()
        self.trailing_slash = "/?"


router = OptionalSlashRouter()


urlpatterns = [
    path("health_check/", HealthCheckCustomView.as_view(), name="health_check"),
] + router.urls
