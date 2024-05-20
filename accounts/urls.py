from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('signup/', views.SignUpPageView.as_view(), name='signup'),
    path('api/signup/', views.SignUpView.as_view(), name='api_signup'),
    path('login/', views.login, name='login'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('logout/', views.logout, name='logout'),
    path('test/', views.test, name='test'),
    path('profile/<int:article_id>',views.ProfileView.as_view(), name="profile"),
    path('profile/<int:article_id>/update/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('profile/image/<int:article_id>/', views.ProfileImageView.as_view(), name='profile_image_update'),
    path('profile/<int:article_id>/change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    path('profile/delete-account/<int:user_id>/', views.ProfiledeleteView.as_view(), name='delete-account'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
