from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from .serializers import HydroponicSystemSerializer, MeasurementSerializer
from datetime import datetime
from .models import HydroponicSystem, Measurement
from django.db.models import Q

class HydroponicSystemViewSet(viewsets.ModelViewSet):
    serializer_class = HydroponicSystemSerializer
    
    def get_queryset(self):
        return HydroponicSystem.objects.filter(owner=self.request.user)

    http_method_names = ['get', 'post', 'put', 'delete']

    def create(self, request):
        """
        Create a new hydroponic system for the authenticated user.

        ### Request Body:
        - **name** (string, required): Name of the hydroponic system.
        - **location** (string, optional): Location of the system.
        
        #### Example Request:
        POST /systems/
        ```json
        {
            "name": "Greenhouse A",
            "location": "Farm #1"
        }
        ```
       
        ### Responses:
        - **201 Created**: Returns the created hydroponic system.
        - **400 Bad Request**: If the request data is invalid.

         ### Example Response:
        ```json
        {
            "id": 15,
            "name": "Greenhouse A",
            "location": "Farm #1",
            "created_at": "2025-02-17T11:56:38.938336Z",
            "owner": 4
        }
        ```
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)         

    def retrieve(self, request, pk=None):
        """
        Retrieve details of a specific hydroponic system along with the latest measurements.

        ### Example Request:
        GET /systems/1/

        ### Responses:
        - **200 OK**: Returns the hydroponic system details and its latest measurements.
        - **403 Forbidden**: If the user does not own the requested hydroponic system.
        - **404 Not Found**: If the system does not exist.

        ### Example Response:
        ```json
        {
            "hydroponic_system": {
                "id": 1,
                "name": "Green",
                "location": "Farm #1",
                "created_at": "2025-02-15T17:10:58.803766Z",
                "owner": 4
            },
            "latest_measurements": [
                {
                    "id": 16,
                    "timestamp": "2025-02-15T19:08:31.972081Z",
                    "ph": 6.5,
                    "temperature": 22.5,
                    "tds": 900,
                    "system": 1
                },
                ...
            ]
        }
        ```
        """
        hydroponic_system = self.get_object()
        
        if hydroponic_system.owner != request.user:
            raise PermissionDenied("You do not have access to this resource.")

        latest_measurements = Measurement.objects.filter(system=hydroponic_system).order_by('-timestamp')[:10]

        hydroponic_serializer = self.get_serializer(hydroponic_system)
        measurement_serializer = MeasurementSerializer(latest_measurements, many=True)

        response_data = {
            "hydroponic_system": hydroponic_serializer.data,
            "latest_measurements": measurement_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """
        Update a hydroponic system

        ### Request Body:
        - **name** (string, optional): The new name of the hydroponic system.
        - **location** (string, optional): The new location of the hydroponic system.

        ### Example Request:
        PUT /systems/5/
        ```json
        {
            "name": "Updated Hydroponic System",
            "location": "Greenhouse B"
        }
        ```

        ### Responses:
        - **200 OK**: Returns the updated hydroponic system data. Example:
        - **400 Bad Request**: If the request data is invalid.
        - **403 Forbidden**: If the user is not the owner of the system.
        - **404 Not Found**: If the system does not exist.

        ### Example Response:
        ```json
        {
            "id": 5,
            "name": "Updated Hydroponic System",
            "location": "Greenhouse B",
            "owner": 2,
            "created_at": "2024-01-15T12:30:00Z"
        }
        ```
        """
        hydroponic_system = self.get_object()
        if hydroponic_system.owner != request.user:
            raise PermissionDenied("You cannot edit this resource.")
        serializer = self.get_serializer(hydroponic_system, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        Delete a hydroponic system.

        ### Example Request:
        DELETE /systems/5/
        
        ### Responses:
        - **204 No Content**: Successfully deleted the hydroponic system.
        - **403 Forbidden**: If the user is not the owner of the system.
        - **404 Not Found**: If the system does not exist.

        ### Example Response:
        ```json
        {
            "message": "Hydroponic system has been removed."
        }
        ```
        """
        hydroponic_system = self.get_object()
        if hydroponic_system.owner != request.user:
            raise PermissionDenied("You cannot delete this resource.")
        hydroponic_system.delete()
        return Response({"message": "Hydroponic system has been removed."}, status=status.HTTP_204_NO_CONTENT)
    
    def list(self, request):
        """
        List of hydroponic systems owned by the authenticated user.

        ### Query Parameters:
        - **name** (string, optional): Filter by system name (case-insensitive partial match).
        - **location** (string, optional): Filter by location (case-insensitive partial match).
        - **created_after** (YYYY-MM-DD, optional): Filter systems created after the given date.
        - **created_before** (YYYY-MM-DD, optional): Filter systems created before the given date.
        - **sort_by** (string, optional): Field to sort results by (default: `created_at`).
        - **sort_order** (string, optional): Sorting order (`asc` or `desc`, default: `asc`).

        #### Example Request:
        GET /systems/?name=greenhouse&sort_by=name&sort_order=desc
        
        ### Responses:
        - **200 OK**: Returns a list of hydroponic systems.
        - **400 Bad Request**: If a query parameter is incorrectly formatted.
        
        ### Example Response:
        ```json
        {
            "count": 12,
            "next": "http://localhost:8000/systems/?page=2",
            "previous": null,
            "results": [
                {
                    "id": 1,
                    "name": "Greenhouse A",
                    "location": "Farm #1",
                    "created_at": "2025-02-15T17:10:58.803766Z",
                    "owner": 4
                },
                {
                    "id": 4,
                    "name": "= A",
                    "location": "Farm #1",
                    "created_at": "2025-02-15T17:11:57.798625Z",
                    "owner": 4
                },
                ...
            ]
        }
        ```
        """ 
        
        try:
            #filtering
            filters = Q(owner=request.user)

            name = request.query_params.get("name")
            if name:
                filters &= Q(name__icontains=name)

            location = request.query_params.get("location")
            if location:
                filters &= Q(location__icontains=location)

            created_after = request.query_params.get("created_after")
            created_before = request.query_params.get("created_before")

            try:
                if created_after:
                    filters &= Q(timestamp__gte=datetime.strptime(created_after, "%Y-%m-%d"))
                
                if created_before:
                    filters &= Q(timestamp__lte=datetime.strptime(created_before, "%Y-%m-%d"))
            
            except ValueError:
                    return Response(
                        {"detail": "Invalid date format. Expected format: YYYY-MM-DD."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            #sorting
            sort_by = request.query_params.get("sort_by", "created_at")
            sort_order = request.query_params.get("sort_order", "asc")

            if sort_order not in ["asc", "desc"]:
                return Response(
                    {"detail": "Invalid value for 'sort_order'. Use 'asc' for ascending or 'desc' for descending."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            sort_field = f"-{sort_by}" if sort_order == "desc" else sort_by

            queryset = HydroponicSystem.objects.filter(filters).order_by(sort_field)

            #pagination
            page = self.paginate_queryset(queryset)
            
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)