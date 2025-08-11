from rest_framework import viewsets
from .models import Participantes
from .serializers import ParticipantesSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class ParticipantesViewSet(viewsets.ModelViewSet):
    queryset = Participantes.objects.all()
    serializer_class = ParticipantesSerializer
    permission_classes = [IsAuthenticated]

class BuscarParticipantePorCelularView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        celular = request.data.get('celular')

        if not celular:
            return Response(
                {
                    "success": False,
                    "message": "O número de celular é obrigatório.",
                    "data": []
                },
                status=status.HTTP_200_OK
            )

        try:
            participante = Participantes.objects.get(celular=celular)
            serializer = ParticipantesSerializer(participante)
            return Response(
                {
                    "success": True,
                    "message": "Participante encontrado.",
                    "data": [serializer.data]
                },
                status=status.HTTP_200_OK
            )
        except Participantes.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Participante não encontrado.",
                    "data": []
                },
                status=status.HTTP_200_OK
            )
        
# PARA CRIAR PARTICIPANTE VIA API - danny - 08-08-2025
