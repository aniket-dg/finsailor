from django.urls import path, re_path, include
from rest_framework import routers

from . import views


router = routers.SimpleRouter()
router.register(r"investment", views.InvestmentViewSet, basename="Investment")
router.register(r"transactions", views.TransactionViewSet, basename="Transaction")


urlpatterns = [
    re_path("^", include(router.urls)),
]
