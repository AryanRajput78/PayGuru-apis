from rest_framework import generics, status
from rest_framework.response import Response

from .models import deviceDetails
from .serializers import DeviceSerializer

#API to List all the devices from the device table. (Development Done.)
class deviceList(generics.ListAPIView):
    queryset = deviceDetails.objects.all()
    serializer_class = DeviceSerializer
device_list = deviceList.as_view()

# API to Create and List a record from the device table. (Development Done.)
class deviceCreate(generics.CreateAPIView):
    queryset = deviceDetails.objects.all()
    serializer_class = DeviceSerializer
device_list_create = deviceCreate.as_view()

# API to Update and Delete a record from the device table. (Development Done.)
class deviceUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = deviceDetails.objects.all()
    serializer_class = DeviceSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.errors, status=status.HTTP_200_OK)
device_update = deviceUpdate.as_view()