from django.urls import path

from .measurement_view import MeasurementAPIView

urlpatterns = [
    path('systems/<int:system_id>/measurements/', MeasurementAPIView.as_view(), name="measurement"),
]