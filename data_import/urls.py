from django.urls import path, re_path, include
from rest_framework import routers

from . import views


router = routers.SimpleRouter()
router.register(r"trade-book", views.TradeBookViewSet, basename="TradeBook")


urlpatterns = [
    re_path("^", include(router.urls)),
]
