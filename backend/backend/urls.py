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
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.urls import re_path


from django.urls import path
from rest_framework_simplejwt import views as JWTAuthenticationViews

from temport.views import test_start
from temport.views import test_end
from temport.views import TempoDataDemandView
from temport.views import TempoDataFetchView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/token', JWTAuthenticationViews.TokenObtainPairView.as_view(),
         name='get_token'),
    path('api/token/refresh',
         JWTAuthenticationViews.TokenRefreshView.as_view(), name='refresh_token'),

    path('tempo/demand',
         TempoDataDemandView.as_view(), name='tempo_data_demand'),
    path('tempo/fetch',
         TempoDataFetchView.as_view(), name='tempo_data_fetch'),

    path('test/start',
         test_start, name='test_start'),
    path('test/end',
         test_end, name='test_end'),

    re_path(r'^media/(?P<path>.*)$', static_serve,
            {'document_root': settings.MEDIA_ROOT}),
]
