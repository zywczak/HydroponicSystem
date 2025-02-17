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
        """
        Add a new measurement for a specific hydroponic system.

        ## URL Parameter:
        - **system_id** (integer, required): The ID of the hydroponic system.

        ## Request Body:
        - **temperature** (float, required): The recorded temperature (in °C).
        - **ph** (float, required): The pH level of the system.
        - **tds** (integer, required): Total dissolved solids (TDS) in ppm.
        - **timestamp** (string, optional, default: current time): The timestamp of the measurement.

        ## Example Request:
        POST /systems/1/measurements/

        ```json
        {
            "ph": 6.5,
            "temperature": 22.5,
            "tds": 900
        }
        ```

        ## Responses:
        - **201 Created**: Successfully created a new measurement.
        - **400 Bad Request**: If the request data is invalid.
        - **403 Forbidden**: If the user does not have permission to add measurements to the system.

        ## Example Response:
        ```json
        {
            "id": 17,
            "timestamp": "2025-02-17T12:22:43.652462Z",
            "ph": 6.5,
            "temperature": 22.5,
            "tds": 900,
            "system": 1
        }
        ```
        """
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
        """
        List of measurements for a specific hydroponic system.

        ## URL Parameter:
        - **system_id** (integer, required): The ID of the hydroponic system.

        ## Query Parameters (Optional):
        - **ph_min** (float): Filter measurements with pH greater than or equal to this value.
        - **ph_max** (float): Filter measurements with pH less than or equal to this value.
        - **temperature_min** (float): Filter measurements with temperature greater than or equal to this value.
        - **temperature_max** (float): Filter measurements with temperature less than or equal to this value.
        - **tds_min** (float): Filter measurements with total dissolved solids greater than or equal to this value.
        - **tds_max** (float): Filter measurements with total dissolved solids less than or equal to this value.
        - **timestamp_after** (YYYY-MM-DD): Filter measurements recorded after this date.
        - **timestamp_before** (YYYY-MM-DD): Filter measurements recorded before this date.
        - **sort_by** (string, default: `timestamp`): Field to sort the results by.
        - **sort_order** (string, default: `asc`): Sorting order (`asc` for ascending, `desc` for descending).

        ## Example Request:
        GET /systems/1/measurements/?ph_min=6.0&ph_max=7.0&temperature_min=20&sort_by=temperature&sort_order=desc

        ## Responses:
        - **200 OK**: Returns a paginated list of measurements.
        - **400 Bad Request**: If a query parameter is incorrectly formatted.
        - **403 Forbidden**: If the user does not have permission to access the system.

        ## Example Response:
        ```json
        {
            "count": 2,
            "next": null,
            "previous": null,
            "results": [
                {
                    "id": 12,
                    "timestamp": "2025-02-17T12:00:00Z",
                    "ph": 6.8,
                    "temperature": 25.0,
                    "tds": 480,
                    "system": 5
                },
                {
                    "id": 11,
                    "timestamp": "2025-02-17T11:56:38.938336Z",
                    "ph": 6.4,
                    "temperature": 24.5,
                    "tds": 500,
                    "system": 5  
                }
            ]
        }
        ```
        """
        try:
            system = HydroponicSystem.objects.get(id=system_id, owner=request.user)
        except HydroponicSystem.DoesNotExist:
            raise PermissionDenied("You do not have permission to this system")

        #filtering
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

        #sorting
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

        #pagination
        paginator = self.pagination()
        paginated_measurements = paginator.paginate_queryset(measurements, request)

        serializer = MeasurementSerializer(paginated_measurements, many=True)
        return paginator.get_paginated_response(serializer.data)