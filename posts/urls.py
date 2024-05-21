from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path("", views.PostAPIView.as_view(), name="api_post"),
    path("postcreate/", views.PostcreateView.as_view(), name="postcreate"),
    path("<int:post_id>/", views.PostDetailAPIView.as_view()),
    path("<int:post_id>/comments/", views.PostDetailAPIView.as_view()),

]
