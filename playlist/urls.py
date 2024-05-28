from django.urls import path
from . import views

urlpatterns = [
    path("", views.PlaylistPageView.as_view(), name="playlist"),
    path("data/", views.PlaylistDataAPIView.as_view(), name="playlist-data"),
    path("search/", views.PlaylistSearchAPIView.as_view(), name="playlist-search"),
    path("zzim/<int:playlist_id>/", views.PlaylistZzimAPIView.as_view(), name="playlist-zzim"),
]
