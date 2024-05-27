from django.urls import path
from . import views
urlpatterns = [
    path("", views.CoachAPIView.as_view(), name="coach"),
    path("result/", views.CoachResultAPIView.as_view(), name="coach-result"),
]
