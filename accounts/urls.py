from django.urls import path
from . import views
urlpatterns = [
    path('profile/<int:article_id>',views.ProfileView.as_view(), name="profile"),
    path('profile/<int:article_id>/update/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/image/<str:username>/', views.ProfileImageView.as_view(), name='profile_image_update'),
    path('profile/<int:article_id>/change-password/', views.PasswordChangeView.as_view(), name='change-password'),
]
