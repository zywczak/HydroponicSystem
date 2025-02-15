from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import HydroponicSystem
from .serializers import MeasurementSerializer


class MeasurementAPIView(APIView):      
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
