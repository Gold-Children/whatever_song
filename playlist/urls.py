from django.urls import path
from . import views

urlpatterns = [
    path('', views.PlaylistAPIView.as_view(), name='playlist'),
    path('search/', views.PlaylistSearchAPIView.as_view(), name='playlist-search'),
]
