from rest_framework import serializers # type: ignore
from .models import bancoApi

class DesafioSerializer(serializers.ModelSerializer):
    class Meta:
        model = bancoApi
        fields = '__all__'