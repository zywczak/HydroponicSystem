from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .serializers import HydroponicSystemSerializer

class HydroponicSystemViewSet(viewsets.ModelViewSet):
    serializer_class = HydroponicSystemSerializer

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
        serializer = self.get_serializer(hydroponic_system)
        return Response(serializer.data, status=status.HTTP_200_OK)

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