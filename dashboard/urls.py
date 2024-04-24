from django.urls import path
from . import views

urlpatterns = [
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
