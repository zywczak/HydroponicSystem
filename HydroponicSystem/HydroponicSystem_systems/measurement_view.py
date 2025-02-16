from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import HydroponicSystem, Measurement
from .serializers import MeasurementSerializer
from datetime import datetime
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

class MeasurementAPIView(APIView):    
    pagination = PageNumberPagination

    def post(self, request, system_id):
        try:
            system = HydroponicSystem.objects.get(id=system_id, owner=request.user)
        except HydroponicSystem.DoesNotExist:
            raise PermissionDenied("You do not have permission to add measurements in this system.")

        serializer = MeasurementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(system=system)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)          

    def get(self, request, system_id):

        try:
            system = HydroponicSystem.objects.get(id=system_id, owner=request.user)
        except HydroponicSystem.DoesNotExist:
            raise PermissionDenied("You do not have permission to this system")

        filters = Q(system=system)

        ph_min = request.query_params.get("ph_min")
        ph_max = request.query_params.get("ph_max")
        temp_min = request.query_params.get("temperature_min")
        temp_max = request.query_params.get("temperature_max")
        tds_min = request.query_params.get("tds_min")
        tds_max = request.query_params.get("tds_max")
        timestamp_after = request.query_params.get("timestamp_after")
        timestamp_before = request.query_params.get("timestamp_before")

        if ph_min:
            filters &= Q(ph__gte=ph_min)
        if ph_max:
            filters &= Q(ph__lte=ph_max)
        if temp_min:
            filters &= Q(temperature__gte=temp_min)
        if temp_max:
            filters &= Q(temperature__lte=temp_max)
        if tds_min:
            filters &= Q(tds__gte=tds_min)
        if tds_max:
            filters &= Q(tds__lte=tds_max)

        try:
            if timestamp_after:
                filters &= Q(timestamp__gte=datetime.strptime(timestamp_after, "%Y-%m-%d"))
            if timestamp_before:
                filters &= Q(timestamp__lte=datetime.strptime(timestamp_before, "%Y-%m-%d"))
        except ValueError:
            return Response(
                {"detail": "Invalid timestamp format. Expected format: YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sort_by = request.query_params.get("sort_by", "timestamp")
        sort_order = request.query_params.get("sort_order", "asc")

        if sort_order not in ["asc", "desc"]:
            return Response(
                {"detail": "Invalid value for 'sort_order'. Use 'asc' or 'desc'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if sort_order == "desc":
            sort_by = f"-{sort_by}"

        measurements = Measurement.objects.filter(filters).order_by(sort_by)

        paginator = self.pagination()
        paginated_measurements = paginator.paginate_queryset(measurements, request)

        serializer = MeasurementSerializer(paginated_measurements, many=True)
        return paginator.get_paginated_response(serializer.data)