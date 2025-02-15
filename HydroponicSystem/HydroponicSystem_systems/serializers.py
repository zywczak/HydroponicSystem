from rest_framework.serializers import ModelSerializer
from .models import HydroponicSystem, Measurement

class HydroponicSystemSerializer(ModelSerializer):
    class Meta:
        model = HydroponicSystem
        fields = '__all__'
        read_only_fields = ['owner', 'created_at']

class MeasurementSerializer(ModelSerializer):
    class Meta:
        model = Measurement
        fields = '__all__'
        read_only_fields = ['system', 'timestamp']