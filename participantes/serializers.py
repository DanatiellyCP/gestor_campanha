# participantes/serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Participantes

class ParticipantesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participantes
        fields = '__all__'
        extra_kwargs = {
            'senha': {'write_only': True}  # senha não aparece no GET
        }

    def create(self, validated_data):
        if 'senha' in validated_data and validated_data['senha']:
            validated_data['senha'] = make_password(validated_data['senha'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'senha' in validated_data and validated_data['senha']:
            validated_data['senha'] = make_password(validated_data['senha'])
        return super().update(instance, validated_data)
