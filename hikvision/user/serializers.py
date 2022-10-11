from rest_framework import serializers
from .models import userDetails

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = userDetails
        fields = ("__all__")