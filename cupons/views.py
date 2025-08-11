from dataclasses import asdict
import os
import uuid
import json
from venv import logger
import numpy as np
import cv2
import ast

from django.shortcuts import render, get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from cupons.models.series import Serie
from utils.get_modelo import identificar_chave_detalhada 

from .models import Cupom, Produto, NumeroDaSorte
from skus_validos.models import Skus_validos 
from participantes.models import Participantes
from utils.funcoes_cupom import extrair_texto_ocr, extrair_numero_cupom, extrai_codigo_qrcode, validar_documento, get_dados_json
from utils.api_sefaz import gerar_link_sefaz, consulta_nfe, consulta_api_nfce, consulta_api_CFeSat
from decimal import Decimal, InvalidOperation

def guardar_cupom(arquivo):
    """Salva a imagem do cupom no storage padrão e retorna o caminho salvo."""
    ext = os.path.splitext(arquivo.name)[1]
    nome_arquivo = f"cupom_{uuid.uuid4().hex}{ext}"
    caminho_arquivo = os.path.join('cupons', nome_arquivo)
    return default_storage.save(caminho_arquivo, ContentFile(arquivo.read()))

import json
from dataclasses import asdict
from django.shortcuts import render, get_object_or_404

from django.shortcuts import render, get_object_or_404
from django.core.files.storage import default_storage
import cv2
import json
from dataclasses import asdict

def cadastrar_cupom(request, id_participante):
    participante = get_object_or_404(Participantes, id=id_participante)
    contexto = {'id_participante': id_participante}

    if request.method == 'POST':
        chave_acesso = None
        dados_ocr = ""
        imagem_path = None
        erro = None

        try:
            if 'submit_codigo' in request.POST:
                # Captura código digitado manualmente
                chave_acesso = request.POST.get('cod_cupom')

            elif 'submit_imagem' in request.POST:
                arquivo = request.FILES.get('img_cupom')
                if not arquivo:
                    erro = 'Nenhum arquivo de imagem foi selecionado.'
                else:
                    # Salva arquivo e obtém caminho local
                    imagem_path = guardar_cupom(arquivo)
                    imagem_local_path = default_storage.path(imagem_path)

                    # Lê imagem para processar OCR e QR Code
                    imagem_cv = cv2.imread(imagem_local_path)
                    if imagem_cv is None:
                        raise ValueError("Não foi possível carregar a imagem para processamento.")
                    
                    gray = cv2.cvtColor(imagem_cv, cv2.COLOR_BGR2GRAY)
                    detector = cv2.QRCodeDetector()
                    dados_qr, _, _ = detector.detectAndDecode(gray)

                    # Extrai texto via OCR
                    dados_ocr = extrair_texto_ocr(imagem_local_path)
                    # Prioriza QR, senão OCR para extrair chave
                    chave_acesso = extrair_numero_cupom(dados_qr or dados_ocr)

            if erro:
                contexto['msg_erro'] = erro
                return render(request, 'cad_cupom.html', contexto)

            if not chave_acesso:
                contexto['msg_erro'] = "Informe o código do cupom."
                return render(request, 'cad_cupom.html', contexto)

            # Validação da chave do cupom
            dados_nota = identificar_chave_detalhada(chave_acesso)
            if not dados_nota.valida:
                contexto['msg_erro'] = f"Chave inválida: {dados_nota.mensagem}"
                return render(request, 'cad_cupom.html', contexto)

            # Status fixo pois já validado
            status_nota = 'Aprovado'

            # Validação adicional (ex: consulta externa)
            validar = validar_cupom(dados_nota.chave, dados_nota.tipo_documento)

            # Serializa dados para JSON (string) para armazenar
            dados_cupom_json = json.dumps(asdict(dados_nota))

            # Criação do cupom no banco
            novo_cupom = Cupom.objects.create(
                participante=participante,
                dados_cupom=dados_cupom_json,
                tipo_envio='Codigo' if 'submit_codigo' in request.POST else 'Imagem',
                status=status_nota,
                numero_documento=dados_nota.codigo_numerico,
                cnpj_loja=dados_nota.cnpj_emitente,
                dados_json=validar,
                tipo_documento=dados_nota.tipo_documento
            )

            # Cadastro dos produtos vinculados ao cupom
            msg_produto = cadastrar_produto(novo_cupom.id, id_participante)
            contexto['msg_sucesso'] = f'Cupom cadastrado com sucesso! {msg_produto}'

        except Exception as e:
            contexto['msg_erro'] = f'Erro ao processar o cadastro: {e}'

    return render(request, 'cad_cupom.html', contexto)



# paraca cadastrar por imagem

# para ler qrccode -----------------------------------------------------------------
@csrf_exempt
# @login_required
def salvar_qrcode_ajax(request, id_participante):
    """Recebe dados do QR Code lido pela câmera via AJAX e tenta registrar o cupom."""
    if request.method != 'POST':
        return JsonResponse({'status': 'erro', 'mensagem': 'Método inválido.'}, status=405)

    try:
        contexto = {'id_participante': id_participante}

        body = json.loads(request.body)
        dados_qr = body.get('dados_qr')
        
        if not dados_qr:
            return JsonResponse({'status': 'erro', 'mensagem': 'Nenhum dado de QR Code recebido.'}, status=400)

        chave_acesso =  extrai_codigo_qrcode(dados_qr)
        print('chave: ' +  chave_acesso)
        if not chave_acesso or len(chave_acesso) != 44:
            return JsonResponse({'status': 'erro', 'mensagem': 'Não foi possível extrair uma chave válida do QR Code.'}, status=400)

        participante = get_object_or_404(Participantes, id=id_participante)

        dados_nota = identificar_chave_detalhada(chave_acesso)

        if not dados_nota.valida:
            contexto['msg_erro'] = f"Chave inválida: {dados_nota.mensagem}"
            return render(request, 'cad_cupom.html', contexto)

        status_nota = 'Aprovado'  # já validado acima

        validar = validar_cupom(dados_nota.chave, dados_nota.tipo_documento)

        # Serializa dados_nota para string JSON, caso dados_cupom seja TextField
        dados_cupom_json = json.dumps(asdict(dados_nota))

        novo_cupom = Cupom.objects.create(
            participante=participante,
            dados_cupom=dados_cupom_json,  # string JSON
            tipo_envio='Codigo',
            status=status_nota,
            numero_documento=dados_nota.codigo_numerico,
            cnpj_loja=dados_nota.cnpj_emitente,
            dados_json=validar,            # dict direto se for JSONField
            tipo_documento=dados_nota.tipo_documento
        )
        
        msg_produto = cadastrar_produto(novo_cupom.id, id_participante)
        print(msg_produto)

        contexto['msg_sucesso'] = f'Cupom cadastrado com sucesso! {msg_produto}'
        return render(request, 'cad_cupom.html', contexto)
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'erro', 'mensagem': 'Requisição JSON malformada.'}, status=400)
    except Participantes.DoesNotExist:
        return JsonResponse({'status': 'erro', 'mensagem': 'Participante não encontrado.'}, status=404)
    except Exception as e:
        # Logar o erro real no servidor é importante
        logger.error(f"Erro inesperado em salvar_qrcode_ajax: {e}")
        #return JsonResponse({'status': 'erro', 'mensagem': 'Ocorreu um erro interno.'}, status=500)



def validar_cupom(chave, tipo):
   
    if tipo == 'SAT-cfe':
       dados_sefaz = consulta_api_CFeSat(chave)
    
    if tipo == 'NF-e':
        dados_sefaz = consulta_nfe(chave)
        

    if tipo == 'NFC-e':
        dados_sefaz = consulta_api_nfce(chave)
    
    return dados_sefaz


#------------------- PRODUTOS --------------------------------------

def parse_decimal(value):
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    if isinstance(value, str):
        value = value.replace(',', '.').strip()
        try:
            return Decimal(value)
        except InvalidOperation:
            raise ValueError(f"Valor inválido para decimal: {value}")
    raise ValueError(f"Tipo inválido para decimal: {type(value)}")


def cadastrar_produto(id_cupom, id_participante):
    cupom = Cupom.objects.get(id=id_cupom)

    try:
        dados_cupom = get_dados_json(cupom.dados_json, cupom.tipo_documento)
    except Exception as e:
        print(f"[ERRO] Falha ao processar dados_json do cupom {cupom.id}: {e}")
        return 'Erro ao processar cupom'

    produtos_para_cadastro = []

    for produto in dados_cupom.get("produtos", []):
        ean = produto.get("ean") or produto.get("codigo")
        if not ean:
            continue

        if validar_produto_cupom(ean):
            try:
                valor_unitario_raw = produto.get("valor_unitario", "0.00")
                valor_unitario = parse_decimal(valor_unitario_raw)
            except ValueError as ve:
                print(f"[ERRO] Valor unitário inválido para o produto {ean}: {ve}")
                continue

            novo_numero_sorte = gerar_numero_sorte()
            produto_obj = Produto(
                cupom=cupom,
                nome=produto.get("descricao", ""),
                quantidade=produto.get("qtd", 1),
                valor_unitario=valor_unitario,
                num_sorte=novo_numero_sorte
            )
            produtos_para_cadastro.append(produto_obj)

    if produtos_para_cadastro:
        Produto.objects.bulk_create(produtos_para_cadastro)
        return f"{len(produtos_para_cadastro)} produto(s) cadastrado(s)"
    else:
        return "Nenhum produto válido para cadastrar"


def validar_produto_cupom(cod_produto):
    try:
        sku = Skus_validos.objects.get(ean=cod_produto)
        return True
    except Skus_validos.DoesNotExist:
        return False


def gerar_numero_sorte():
    try:
        serie_atual = Serie.objects.get(status='Aberta')
    except Serie.DoesNotExist:
        serie_atual = Serie.objects.create(
            nome_serie='serie_00',
            numero_atual=0,
            status='Aberta'
        )

    num_atual = serie_atual.numero_atual
    nome_serie = serie_atual.nome_serie.replace('serie_', '')

    if num_atual < 99999:
        novo_numero = num_atual + 1
        edita_numero_serie(serie_atual.id, novo_numero, 'Aberta')
        # Aqui concateno os números com zero à esquerda, formando uma string de 7 dígitos
        numero_sorte = f"{int(nome_serie):02d}{novo_numero:05d}"
        return numero_sorte
    else:
        edita_numero_serie(serie_atual.id, 0, 'Fechada')
        nova_serie = Serie.objects.create(
            nome_serie=f'serie_{int(nome_serie) + 1}',
            numero_atual=0,
            status='Aberta'
        )
        numero_sorte = f"{int(nome_serie) + 1:02d}00000"
        return numero_sorte


def edita_numero_serie(id, num_serie, status):
    serie_atual = Serie.objects.get(id=id)
    serie_atual.numero_atual = num_serie
    serie_atual.status = status
    serie_atual.save()


def completa_numero(numero, tamanho):
    return str(numero).zfill(tamanho)



