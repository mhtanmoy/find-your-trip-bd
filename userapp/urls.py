from django.urls import path
from rest_framework import routers
from userapp.views import UserLoginView, UserRegistrationView


class OptionalSlashRouter(routers.SimpleRouter):
    def __init__(self):
        super().__init__()
        self.trailing_slash = "/?"


router = OptionalSlashRouter()
router.register(r"login", UserLoginView, basename="user-login")
router.register(r"register", UserRegistrationView, basename="user-register")


urlpatterns = [
    # Add your URL patterns here
] + router.urls
