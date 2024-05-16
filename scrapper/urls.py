from django.urls import path
from . import views

urlpatterns = [
    path("security/", views.NSEViewSet.as_view()),
]
