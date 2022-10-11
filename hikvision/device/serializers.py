from rest_framework import serializers
from .models import deviceDetails

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = deviceDetails
        exclude = ['id', 'status']