from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Find Your Trip BD API",
        default_version="v1.0",
        description="Your API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

admin.site.site_header = "Find Your Trip BD Admin"
admin.site.index_title = "Find Your Trip BD Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("recommender.urls")),
    path("auth/", include("userapp.urls")),
]
if settings.DEBUG:
    optional_urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    urlpatterns += (
        path(
            "docs/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
    )
    urlpatterns += optional_urlpatterns
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
