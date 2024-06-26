from django.urls import path
from . import views

urlpatterns = [
    path('', views.CoachPageView.as_view(), name='coach'),
    path('result/<int:pk>/', views.ResultPageView.as_view(), name='coach_result'),
    path('api/input/', views.InputView.as_view(), name='api_input'),
    path('api/result/<int:pk>/', views.ResultView.as_view(), name='api_result'), 
    path('api/user/', views.UserCoachedVocalView.as_view(), name='user_coached_vocal'),

    path('api/status/', views.CheckStatusView.as_view(), name='status'),
    path('api/kakao-api-key/',views.get_kakao_api_key, name='get_kakao_api_key'),
]
