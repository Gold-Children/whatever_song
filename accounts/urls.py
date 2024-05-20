from django.urls import path
from . import views
urlpatterns = [
    path('signup/', views.SignUpPageView.as_view(), name='signup'),
    path('api/signup/', views.SignUpView.as_view(), name='api_signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]
