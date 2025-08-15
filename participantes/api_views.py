# gestor_campanha/participantes/api_views.py

from rest_framework import viewsets
from .models import Participantes
from .serializers import ParticipantesSerializer
from promocaobombril.api_auth import FixedTokenPermission
from cupons.models.cupom import Cupom
from cupons.models.numero_sorte import NumeroDaSorte
from utils.get_modelo import identificar_chave_detalhada
from utils.funcoes_cupom import (
    extrair_texto_ocr,
    extrair_numero_cupom,
    extrai_codigo_qrcode,
    get_dados_json,
)
from cupons.views import (
    guardar_cupom,
    validar_cupom,
    cadastrar_produto,
    cadastrar_numeros_da_sorte,
)
from dataclasses import asdict
import json
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.base import ContentFile
import base64
import re as _re
from django.db import IntegrityError


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from django.utils import timezone
from datetime import datetime

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


class EnviarNotaView(APIView):
    """
    Recebe uma nota via:
      - chave_acesso (44 dígitos) OU
      - imagem_nota (foto/scan da nota fiscal) OU
      - imagem_qrcode (foto/scan do QR Code)

    Identifica o participante por celular e realiza o cadastro do cupom,
    validação e geração de números da sorte.

    Body (multipart/form-data ou JSON):
      - celular: string (obrigatório)
      - chave_acesso: string (opcional)
      - imagem_nota: arquivo (opcional)
      - imagem_qrcode: arquivo (opcional)
    """

    permission_classes = [FixedTokenPermission]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        # Regra de campanha: aceitar cadastro somente entre 15/08/2025 e 15/10/2025
        # (somente quando a variável de ambiente CAMPANHA estiver ON)
        try:
            if str(getattr(settings, 'CAMPANHA', '')).upper() == 'ON':
                hoje_campanha = timezone.localdate()
                inicio = datetime(2025, 8, 15).date()
                fim = datetime(2025, 10, 15).date()
                if not (inicio <= hoje_campanha <= fim):
                    return Response(
                        {
                            "success": False,
                            "message": "Período de participação: 15/08/2025 a 15/10/2025. Tente novamente dentro do período válido.",
                            "data": [],
                        },
                        status=status.HTTP_200_OK,
                    )
        except Exception:
            # Em caso de erro inesperado nessa checagem, não bloquear o fluxo da API
            pass

        celular = request.data.get('celular')
        if not celular:
            return Response(
                {
                    "success": False,
                    "message": "Campo 'celular' é obrigatório.",
                    "data": []
                },
                status=status.HTTP_200_OK,
            )

        # Localiza participante por celular (com/sem 55)
        cel_digits = ''.join(filter(str.isdigit, str(celular)))
        candidatos = [cel_digits]
        if not cel_digits.startswith('55'):
            candidatos.append('55' + cel_digits)
        else:
            candidatos.append(cel_digits[2:])
        participante = (
            Participantes.objects.filter(celular__in=candidatos).order_by('-id').first()
        )
        if not participante:
            return Response(
                {
                    "success": False,
                    "message": "Participante não encontrado pelo celular informado.",
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )

        # Limite diário: 1 cupom por participante por dia (também na API)
        try:
            hoje = timezone.localdate()
            if Cupom.objects.filter(participante=participante, data_cadastro=hoje).exists():
                return Response(
                    {
                        "success": False,
                        "message": "Você já cadastrou um cupom hoje. Tente novamente amanhã.",
                        "data": [],
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception:
            # Em caso de erro inesperado, não bloquear o fluxo
            pass

        # Determina a origem da chave de acesso
        chave_acesso = request.data.get('chave_acesso') or request.data.get('chave')
        imagem_qrcode = request.FILES.get('imagem_qrcode')
        imagem_nota = request.FILES.get('imagem_nota') or request.FILES.get('imagem')

        # Também aceita base64 (data URL ou base64 puro)
        def _decode_b64(data_b64: str, default_name: str) -> ContentFile | None:
            if not data_b64:
                return None
            try:
                # Remove prefixo data URL se houver
                m = _re.match(r'^data:(?P<mime>[^;]+);base64,(?P<data>.+)$', data_b64)
                raw = m.group('data') if m else data_b64
                content = base64.b64decode(raw)
                return ContentFile(content, name=default_name)
            except Exception:
                return None

        if not imagem_qrcode:
            imagem_qrcode_b64 = request.data.get('imagem_qrcode_base64')
            if imagem_qrcode_b64:
                imagem_qrcode = _decode_b64(imagem_qrcode_b64, 'qrcode.jpg')

        if not imagem_nota:
            imagem_nota_b64 = (
                request.data.get('imagem_nota_base64')
                or request.data.get('imagem_base64')
            )
            if imagem_nota_b64:
                imagem_nota = _decode_b64(imagem_nota_b64, 'nota.jpg')

        if not chave_acesso and imagem_qrcode:
            try:
                chave_acesso = extrai_codigo_qrcode(imagem_qrcode)
            except Exception:
                chave_acesso = None

        if not chave_acesso and imagem_nota:
            try:
                texto_ocr = extrair_texto_ocr(imagem_nota)
                chave_acesso = extrair_numero_cupom(texto_ocr)
            except Exception:
                chave_acesso = None

        # Normaliza e valida a chave
        chave_num = ''.join(filter(str.isdigit, str(chave_acesso or '')))
        if len(chave_num) != 44:
            return Response(
                {
                    "success": False,
                    "message": "Chave de acesso inválida ou não encontrada (esperado 44 dígitos).",
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )

        # Validação da chave e coleta de metadados
        dados_nota = identificar_chave_detalhada(chave_num)
        if not getattr(dados_nota, 'valida', False):
            return Response(
                {
                    "success": False,
                    "message": f"Chave inválida: {getattr(dados_nota, 'mensagem', 'erro desconhecido')}",
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )

        # Validação externa (quando disponível)
        try:
            validar = validar_cupom(dados_nota.chave, dados_nota.tipo_documento)
        except Exception:
            validar = None

        # Serializa dados para JSON
        dados_cupom_json = json.dumps(asdict(dados_nota))

        # Cria cupom com status conforme validação externa disponível
        try:
            status_inicial = 'Validado' if validar else 'Pendente'
            novo_cupom = Cupom.objects.create(
                participante=participante,
                dados_cupom=dados_cupom_json,
                tipo_envio='API',
                status=status_inicial,
                numero_documento=getattr(dados_nota, 'codigo_numerico', ''),
                cnpj_loja=getattr(dados_nota, 'cnpj_emitente', ''),
                nome_loja=getattr(dados_nota, 'nome_emitente', 'Desconhecido'),
                dados_json=validar,
                tipo_documento=getattr(dados_nota, 'tipo_documento', ''),
            )
        except IntegrityError:
            return Response(
                {
                    "success": False,
                    "message": "cupom já cadastrado",
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )

        # Produtos e números da sorte
        msg_produto = ''
        downstream_failed = False
        if validar:
            try:
                msg_produto = cadastrar_produto(novo_cupom.id, participante.id)
            except Exception:
                msg_produto = 'Erro ao processar produtos do cupom.'
                downstream_failed = True
        try:
            cadastrar_numeros_da_sorte(novo_cupom)
        except Exception:
            downstream_failed = True

        # Se houve falha em processos downstream e o status não estiver pendente, ajusta para 'Pendente'
        if downstream_failed and novo_cupom.status != 'Pendente':
            try:
                novo_cupom.status = 'Pendente'
                novo_cupom.save(update_fields=['status'])
            except Exception:
                pass

        # Coleta números da sorte gerados
        numeros = list(
            NumeroDaSorte.objects.filter(cupom=novo_cupom).values_list('numero', flat=True)
        )

        return Response(
            {
                "success": True,
                "message": "Cupom cadastrado com sucesso.",
                "data": {
                    "cupom_id": novo_cupom.id,
                    "numeros_da_sorte": numeros,
                    "msg_produto": msg_produto,
                },
            },
            status=status.HTTP_200_OK,
        )