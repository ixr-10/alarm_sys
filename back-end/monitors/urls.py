from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    ServerViewSet, MetricViewSet, AlarmViewSet,
    login_view, logout_view, dashboard_view
)

router = DefaultRouter()
router.register('servers', ServerViewSet)
router.register('metrics', MetricViewSet)
router.register('alarms', AlarmViewSet)

urlpatterns = [
    path('login/', login_view),
    path('logout/', logout_view),
    path('dashboard/', dashboard_view),
] + router.urls