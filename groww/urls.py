from django.urls import path, re_path, include
from rest_framework import routers

from . import views


router = routers.SimpleRouter()
router.register(r"", views.GrowwRequestViewSet, basename="GrowwRequest")
router.register(
    r"header", views.GrowwRequestHeaderViewSet, basename="GrowwRequest-Header"
)


urlpatterns = [
    re_path("^", include(router.urls)),
]
