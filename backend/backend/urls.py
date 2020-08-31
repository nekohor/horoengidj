"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include

from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.urls import re_path


from django.urls import path
from rest_framework_simplejwt import views as JWTAuthenticationViews
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    re_path(r'^media/(?P<path>.*)$', static_serve,
            {'document_root': settings.MEDIA_ROOT}),

    # favicon.cio
    path('favicon.ico', RedirectView.as_view(
        url=r'static/img/favicon.ico')),

    path('api/token', JWTAuthenticationViews.TokenObtainPairView.as_view(),
         name='get_token'),
    path('api/token/refresh',
         JWTAuthenticationViews.TokenRefreshView.as_view(), name='refresh_token'),

    path('mci/', include('mci.urls')),
    path('tempo/', include('temport.urls')),
]
