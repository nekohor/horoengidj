from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from .views import test_start
from .views import test_end
from .views import TempoDataDemandView
from .views import TempoDataFetchView

urlpatterns = [

    path('demand',
         TempoDataDemandView.as_view(), name='tempo_data_demand'),
    path('fetch',
         TempoDataFetchView.as_view(), name='tempo_data_fetch'),

    path('test/start',
         test_start, name='test_start'),
    path('test/end',
         test_end, name='test_end'),
]
