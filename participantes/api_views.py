# gestor_campanha/participantes/api_views.py

from rest_framework import viewsets
from .models import Participantes
from .serializers import ParticipantesSerializer
from promocaobombril.api_auth import FixedTokenPermission
from cupons.models.cupom import Cupom
from cupons.models.numero_sorte import NumeroDaSorte

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class ParticipantesViewSet(viewsets.ModelViewSet):
    queryset = Participantes.objects.all()
    serializer_class = ParticipantesSerializer
    permission_classes = [FixedTokenPermission]

class BuscarParticipanteView(APIView):
    """
    Endpoint unificado da API para buscar um participante por CPF, celular ou e-mail.
    A busca é feita na seguinte ordem de prioridade: CPF, depois e-mail, depois celular.
    """
    permission_classes = [FixedTokenPermission]

    def post(self, request):
        cpf = request.data.get('cpf')
        email = request.data.get('email')
        celular = request.data.get('celular')

        participante = None

        if cpf:
            # Limpa o CPF para uma busca robusta (remove pontos, traços, etc.)
            cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
            participante = (
                Participantes.objects.filter(cpf=cpf_limpo).order_by('-id').first()
            )

        elif email:
            # Busca por e-mail ignorando maiúsculas/minúsculas
            participante = (
                Participantes.objects.filter(email__iexact=email).order_by('-id').first()
            )

        elif celular:
            # Normaliza celular: mantém apenas dígitos, tenta com e sem prefixo 55
            cel_digits = ''.join(filter(str.isdigit, str(celular)))
            candidatos = [cel_digits]
            if not cel_digits.startswith('55'):
                candidatos.append('55' + cel_digits)
            else:
                candidatos.append(cel_digits[2:])  # também tenta sem 55

            participante = (
                Participantes.objects.filter(celular__in=candidatos)
                .order_by('-id')
                .first()
            )

        else:
            return Response(
                {
                    "success": False,
                    "message": "Um dos campos (cpf, email ou celular) é obrigatório.",
                    "data": []
                },
                status=status.HTTP_200_OK
            )

        if not participante:
            return Response(
                {
                    "success": False,
                    "message": "Participante não encontrado.",
                    "data": []
                },
                status=status.HTTP_200_OK
            )

        # Se encontrou o participante por qualquer um dos métodos
        serializer = ParticipantesSerializer(participante)
        return Response(
            {
                "success": True,
                "message": "Participante encontrado.",
                "data": [serializer.data]
            },
            status=status.HTTP_200_OK
        )


class BuscarCuponsPorCelularView(APIView):
    """
    Retorna apenas os códigos de sorteio (números da sorte) do participante
    identificado por celular.
    Autorização: FixedTokenPermission (aceita token fixo ou usuário autenticado).
    Body esperado (POST JSON): { "celular": "5582987124616" }
    """
    permission_classes = [FixedTokenPermission]

    def post(self, request):
        celular = request.data.get('celular')
        if not celular:
            return Response(
                {
                    "success": False,
                    "message": "Campo 'celular' é obrigatório.",
                    "data": []
                },
                status=status.HTTP_200_OK
            )

        # Normaliza celular: só dígitos, tenta com e sem 55
        cel_digits = ''.join(filter(str.isdigit, str(celular)))
        candidatos = [cel_digits]
        if not cel_digits.startswith('55'):
            candidatos.append('55' + cel_digits)
        else:
            candidatos.append(cel_digits[2:])

        participante = (
            Participantes.objects.filter(celular__in=candidatos)
            .order_by('-id')
            .first()
        )

        if not participante:
            return Response(
                {
                    "success": False,
                    "message": "Participante não encontrado pelo celular informado.",
                    "data": []
                },
                status=status.HTTP_200_OK
            )

        numeros = (
            NumeroDaSorte.objects
            .filter(participante=participante, status='ativo')
            .order_by('-id')
            .values_list('numero', flat=True)
        )
        data = list(numeros)

        return Response(
            {
                "success": True,
                "message": f"{len(data)} código(s) encontrado(s).",
                "data": data,
            },
            status=status.HTTP_200_OK
        )