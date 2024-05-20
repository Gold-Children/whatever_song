from django.urls import path
from . import views
urlpatterns = [
    path('profile/<int:article_id>',views.ProfileView.as_view(), name="detail"),
]
