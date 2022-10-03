from rest_framework import serializers
from .models import userDetails

class UserSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(required=False)

    class Meta:
        model = userDetails
        fields = ("__all__")