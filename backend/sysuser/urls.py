from django.urls import path

from rest_framework_simplejwt import views as JWTAuthenticationViews
from .views import UserInfoView
from .views import UserLogoutView

urlpatterns = [
    path('login', JWTAuthenticationViews.TokenObtainPairView.as_view(),
         name='user_login'),

    path('info', UserInfoView.as_view(),
         name='user_info'),

    path('logout', UserLogoutView.as_view(),
         name='user_logout'),
]
