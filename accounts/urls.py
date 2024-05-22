from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup/', views.SignUpPageView.as_view(), name='signup'),
    path('api/signup/', views.SignUpView.as_view(), name='api_signup'),
    path('login/', views.login, name='login'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('logout/', views.logout, name='logout'),
    path('test/', views.test, name='test'),
    path('profile/<int:pk>/', views.ProfilePageView.as_view(), name="profile"),
    path('api/profile/<int:pk>/', views.ProfileView.as_view(), name="api_profile"),

    path('profile/<int:pk>/edit/', views.ProfileUpdatePageView.as_view(), name='profile_edit'),
    path('api/profile/<int:pk>/update/', views.ProfileUpdateView.as_view(), name='api_profile_update'),

    path('api/profile/<int:pk>/image/', views.ProfileImageView.as_view(), name='profile_image_update'),
    path('api/profile/<int:pk>/change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    path('api/profile/<int:pk>/delete/', views.ProfiledeleteView.as_view(), name='profile-delete'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]