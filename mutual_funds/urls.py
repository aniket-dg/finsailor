from django.urls import path, re_path, include
from rest_framework import routers

from . import views


router = routers.SimpleRouter()
router.register(
    r"fund-investment", views.FundInvestmentViewSet, basename="FundInvestment"
)


urlpatterns = [
    re_path("^", include(router.urls)),
]
