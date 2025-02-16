from django.urls import path

from .views import RegisterUserAPIView, UserLoginAPIView

urlpatterns = [
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('register/', RegisterUserAPIView.as_view(), name='register'),          
]