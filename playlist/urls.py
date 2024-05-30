from django.urls import path
from . import views

urlpatterns = [
    path("", views.PlaylistPageView.as_view(), name="playlist"),
    path("data/", views.PlaylistDataAPIView.as_view(), name="playlist-data"),
    path("search/", views.PlaylistSearchAPIView.as_view(), name="playlist-search"),
    path("zzim/<str:playlist_id>/", views.PlaylistZzimAPIView.as_view(), name="playlist-zzim"),
    path("user-zzim/", views.UserZzimPlaylistsAPIView.as_view(), name="user_zzim"),
]
