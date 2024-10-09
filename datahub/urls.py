from django.urls import path, re_path, include
from rest_framework import routers

from . import views


router = routers.SimpleRouter()
router.register(r"security", views.SecurityViewSet, basename="Security")
router.register(r"corporate_actions", views.CorporateActionViewSet, basename="CorporateAction")
router.register(r"general_info", views.GeneralInfoViewSet, basename="GeneralInfo")
urlpatterns = [
    re_path("^", include(router.urls)),
    # path("security", views.SecurityViewSet, name="security"),
]
