from django.urls import path, re_path, include
from rest_framework import routers

from . import views

# router = routers.SimpleRouter()
# router.register(
# r"security", views.ImportContractNoteData, basename="ImportContractNoteData"
# )

urlpatterns = [
    # re_path("^", include(router.urls)),
    path(
        "import/contract-report/",
        views.ImportContractNoteData.as_view(),
        name="import-cn",
    ),
    path(
        "import/demat-report/",
        views.ImportDematReportData.as_view(),
        name="import-demat",
    ),
]
