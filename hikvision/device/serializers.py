from rest_framework import serializers
from .models import deviceDetails

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = deviceDetails
        fields = [
            'id',
            'ip',
            'port',
            'user_id',
            'password',
            'master_status',
            'status',
        ]