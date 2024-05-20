from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path("", views.PostAPIView.as_view(), name="api_post"),
    path("postcreate/", views.PostcreateView.as_view(), name="postcreate")
]
