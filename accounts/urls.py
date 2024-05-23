from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('signup/', views.SignUpPageView.as_view(), name='signup'),
    path('api/signup/', views.SignUpView.as_view(), name='api_signup'),
    path('login/', views.LoginPageView.as_view(), name="login"),
    path('api/token/', TokenObtainPairView.as_view(), name="token_obtain"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('test/', views.test, name='test'),
    path('profile/<int:pk>/',views.ProfilePageView.as_view(), name="profile"),
    path('api/profile/<int:pk>/',views.ProfileView.as_view(), name="api_profile"),
    path('profile/<int:pk>/update/', views.ProfileUpdateView.as_view(), name='profileupdate'),
    path('profile/image/<int:pk>/', views.ProfileImageView.as_view(), name='profile_image_update'),
    path('profile/<int:pk>/change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    path('profile/delete-account/<int:user_id>/', views.ProfiledeleteView.as_view(), name='delete-account'),
]
