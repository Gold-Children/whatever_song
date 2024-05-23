from django.urls import path
from . import views

urlpatterns = [
    path("", views.PlaylistAPIView.as_view(), name="playlist"),
    path("search/", views.PlaylistSearchAPIView.as_view(), name="playlist-search"),
    path("<int:playlist_id>/zzim/", views.PlaylistZzimAPIView.as_view(), name="playlist-zzim"),
    path('test/', views.test, name='playlist-html'),
]
