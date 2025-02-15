from django.urls import path

from .views import RegisterUserAPIView, UserLoginAPIView

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view()),
    path('login/', UserLoginAPIView.as_view()),       
]