from rest_framework.routers import DefaultRouter

from .system_view import HydroponicSystemViewSet

router = DefaultRouter()

router.register(r'systems', HydroponicSystemViewSet, basename='hydroponicsystem')
