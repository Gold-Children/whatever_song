from django.urls import path
from . import views
urlpatterns = [
    path('profile/<int:article_id>',views.ProfileView.as_view(), name="profile"),
    path('profile/<int:article_id>/update/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/image/<int:article_id>/', views.ProfileImageView.as_view(), name='profile_image_update'),
    path('profile/<int:article_id>/change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    path('profile/delete-account/<int:user_id>/', views.ProfiledeleteView.as_view(), name='delete-account'),
]
