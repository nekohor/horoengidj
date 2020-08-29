from django.urls import path
from .views import KanBanView

urlpatterns = [
    path('kanban', KanBanView.as_view()),
]
