from django.contrib import admin
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    info=openapi.Info(
        title="Combo Investment API",
        default_version="v1",
        description="Combo Investment API Documentation",
    ),
    public=False,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("admin/", admin.site.urls),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/groww/", include("groww.urls")),
    path("api/datahub/", include("datahub.urls")),
    path("api/data_import/", include("data_import.urls")),
    path("api/user_investments/", include("user_investment.urls")),
    path("api/industry/", include("industries.urls")),
    path("api/user_investments/mutual_funds/", include("mutual_funds.urls")),
    path("api/nse_scrapper/", include("scrapper.urls")),
    path("api/users/", include("users.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]
