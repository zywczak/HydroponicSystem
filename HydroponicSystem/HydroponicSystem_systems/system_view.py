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
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)         

    def retrieve(self, request, pk=None):
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
        hydroponic_system = self.get_object()
        if hydroponic_system.owner != request.user:
            raise PermissionDenied("You cannot edit this resource.")
        serializer = self.get_serializer(hydroponic_system, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        hydroponic_system = self.get_object()
        if hydroponic_system.owner != request.user:
            raise PermissionDenied("You cannot delete this resource.")
        hydroponic_system.delete()
        return Response({"message": "Hydroponic system has been removed."}, status=status.HTTP_204_NO_CONTENT)
    
    def list(self, request):
        try:
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

            sort_by = request.query_params.get("sort_by", "created_at")
            sort_order = request.query_params.get("sort_order", "asc")

            if sort_order not in ["asc", "desc"]:
                return Response(
                    {"detail": "Invalid value for 'sort_order'. Use 'asc' for ascending or 'desc' for descending."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            sort_field = f"-{sort_by}" if sort_order == "desc" else sort_by

            queryset = HydroponicSystem.objects.filter(filters).order_by(sort_field)

            page = self.paginate_queryset(queryset)
            
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)