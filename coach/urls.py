from django.urls import path
from . import views
urlpatterns = [
    path("", views.CoachAPIView.as_view(), name="coach"),
]
