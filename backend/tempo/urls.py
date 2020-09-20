from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from .views import test_start
from .views import test_end
from .views import AsyncTempoExportTaskView
from .views import AwaitTempoExportTaskView

urlpatterns = [

    path('export/task/async',
         AsyncTempoExportTaskView.as_view(), name='tempo_export_task_async'),
    path('export/task/await',
         AwaitTempoExportTaskView.as_view(), name='tempo_export_task_await'),
    path('test/start',
         test_start, name='test_start'),
    path('test/end',
         test_end, name='test_end'),
]
