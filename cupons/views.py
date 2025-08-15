from dataclasses import asdict
import os
import uuid
import json
import random
from venv import logger
import numpy as np
import cv2
import ast
import re

from django.shortcuts import render, get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q

from campanha.views import Validar_regras_cupom
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


"""
def cadastrar_cupom(request, id_participante):
    participante = get_object_or_404(Participantes, id=id_participante)
    contexto = {'id_participante': id_participante}

    if request.method == 'POST':
        chave_acesso = None
        dados_ocr = ""
        imagem_path = None
        erro = None

        try:
            # Regra: limitar a 1 cupom por dia por participante
            hoje = timezone.localdate()
            if Cupom.objects.filter(participante=participante, data_cadastro=hoje).exists():
                contexto['msg_erro'] = 'Você já cadastrou um cupom hoje. Tente novamente amanhã.'
                return render(request, 'cad_cupom.html', contexto)

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

            # --- Chamada para gerar números da sorte ---
            msg_numeros = cadastrar_numeros_da_sorte(novo_cupom)
            contexto['msg_numeros'] = msg_numeros

        except Exception as e:
            contexto['msg_erro'] = f'Erro ao processar o cadastro: {e}'

    return render(request, 'cad_cupom.html', contexto)
"""


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

                    # Usando sua função para extrair o código QR da imagem
                    chave_acesso = None
                    with open(imagem_local_path, "rb") as f_img:
                        chave_acesso = extrai_codigo_qrcode(f_img)

                    # Se não encontrou QR no arquivo, tenta OCR para pegar código manual
                    if not chave_acesso:
                        dados_ocr = extrair_texto_ocr(imagem_local_path)
                        chave_acesso = extrair_numero_cupom(dados_ocr)

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

            # Validar regras do cupom
            is_cupom_valido = Validar_regras_cupom(dados_nota.mes_emissao, dados_nota.chave , id_participante)

            if is_cupom_valido == True:
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

                # --- Chamada para gerar números da sorte ---
                msg_numeros = cadastrar_numeros_da_sorte(novo_cupom)
                contexto['msg_numeros'] = msg_numeros
            else:
                contexto['msg_erro'] = f'Cupom inválido:'


        except Exception as e:
            contexto['msg_erro'] = f'Erro ao processar o cadastro: {e}'

    return render(request, 'cad_cupom.html', contexto)

@csrf_exempt
def salvar_qrcode_ajax(request, id_participante):
    if request.method != 'POST':
        return JsonResponse({'status': 'erro', 'mensagem': 'Método inválido.'}, status=405)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'erro', 'mensagem': 'Requisição JSON malformada.'}, status=400)

    dados_qr = body.get('dados_qr')
    if not dados_qr:
        return JsonResponse({'status': 'erro', 'mensagem': 'Nenhum dado de QR Code recebido.'}, status=400)

    # Aqui já temos o texto decodificado do QR, usamos sua função para extrair a chave (mesmo que já esteja)
    chave_acesso = extrai_codigo_qrcode(dados_qr)

    if not chave_acesso or len(chave_acesso) != 44:
        return JsonResponse({'status': 'erro', 'mensagem': 'Chave inválida extraída do QR Code.'}, status=400)

    try:
        participante = get_object_or_404(Participantes, id=id_participante)
    except Participantes.DoesNotExist:
        return JsonResponse({'status': 'erro', 'mensagem': 'Participante não encontrado.'}, status=404)

    dados_nota = identificar_chave_detalhada(chave_acesso)

    if not dados_nota.valida:
        return JsonResponse({'status': 'erro', 'mensagem': f'Chave inválida: {dados_nota.mensagem}'}, status=400)

    status_nota = 'Aprovado'  # validado acima

    validar = validar_cupom(dados_nota.chave, dados_nota.tipo_documento)
    dados_cupom_json = json.dumps(asdict(dados_nota))


    # Validar regras do cupom
    is_cupom_valido = Validar_regras_cupom(dados_nota.mes_emissao, dados_nota.chave , id_participante)

    if is_cupom_valido == True:
        try:
            novo_cupom = Cupom.objects.create(
                participante=participante,
                dados_cupom=dados_cupom_json,
                tipo_envio='QRCode',
                status=status_nota,
                numero_documento=dados_nota.codigo_numerico,
                cnpj_loja=dados_nota.cnpj_emitente,
                dados_json=validar,
                tipo_documento=dados_nota.tipo_documento
            )
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': f'Erro ao salvar cupom no banco: {e}'}, status=500)

        try:
            msg_produto = cadastrar_produto(novo_cupom.id, id_participante)
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': f'Erro ao cadastrar produtos: {e}'}, status=500)

        try:
            msg_numeros = cadastrar_numeros_da_sorte(novo_cupom)
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': f'Erro ao gerar números da sorte: {e}'}, status=500)

        return JsonResponse({
            'status': 'ok',
            'mensagem': f'Cupom cadastrado com sucesso! {msg_produto} {msg_numeros}',
            'id_cupom': novo_cupom.id
        })
    else:
        return JsonResponse({
            'status': '',
            'mensagem': 'Cupom inválido, nãopode ser cadastrado.',
            'id_cupom': ''
        })
        


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
        ean = (produto.get("ean") or produto.get("codigo") or "").strip()
        descricao = (produto.get("descricao", "") or "").strip()
        if not ean and not descricao:
            print("[CAD_PROD] Produto sem EAN e sem descrição ignorado:", produto)
            continue

        print(f"[CAD_PROD] Avaliando produto: EAN={ean if ean else '-'}, DESC='{descricao}'")

        sku_match = validar_produto_cupom(ean, descricao)
        if sku_match:
            try:
                valor_unitario_raw = produto.get("valor_unitario", "0.00")
                valor_unitario = parse_decimal(valor_unitario_raw)
            except ValueError as ve:
                print(f"[CAD_PROD] Valor unitário inválido para o produto {ean}: '{valor_unitario_raw}' erro={ve}")
                continue

            # Normaliza e converte quantidade para inteiro (ex.: '1,0000' -> 1)
            qtd_raw = produto.get("qtd", 1)
            try:
                if isinstance(qtd_raw, (int, float, Decimal)):
                    qtd = int(float(qtd_raw))
                else:
                    qstr = str(qtd_raw).strip()
                    # Remove possíveis separadores de milhar e normaliza decimal vírgula para ponto
                    qstr = qstr.replace(" ", "")
                    qstr = qstr.replace(".", "")  # trata '1.000,00' removendo milhar
                    qstr = qstr.replace(",", ".")  # trata '1,0000' -> '1.0000'
                    qtd = int(float(qstr))
            except Exception as e:
                print(f"[CAD_PROD] Quantidade inválida '{qtd_raw}' para o produto EAN={ean}: erro={e}. Usando 1 por padrão.")
                qtd = 1

            print(f"[CAD_PROD] Produto válido. SKU id={sku_match.id} nome='{sku_match.nome}'. Preparando para salvar: qtd={qtd}, valor_unitario={valor_unitario}")

            produto_obj = Produto(
                cupom=cupom,
                nome=sku_match.nome or descricao,
                quantidade=qtd,
                valor_unitario=valor_unitario,
                num_sorte="",
                sku_validado=sku_match,
            )
            produtos_para_cadastro.append(produto_obj)
        else:
            print(f"[CAD_PROD] Produto NÃO válido pelos SKUs: EAN={ean if ean else '-'}, DESC='{descricao}'")

    if produtos_para_cadastro:
        try:
            Produto.objects.bulk_create(produtos_para_cadastro)
            print(f"[CAD_PROD] bulk_create concluído. Total inserido: {len(produtos_para_cadastro)}")
            return f"{len(produtos_para_cadastro)} produto(s) cadastrado(s)"
        except Exception as e:
            print("[CAD_PROD] ERRO no bulk_create de produtos:", e)
            return "Erro ao salvar produtos do cupom"
    else:
        return "Nenhum produto válido para cadastrar"


def validar_produto_cupom(cod_produto, descricao=None):
    """
    Valida o produto contra a tabela Skus_validos.
    1) Primeira tentativa: EAN exato.
    2) Se não encontrar e houver descrição, faz uma busca por similaridade simples
       (tokenizando a descrição e exigindo que todos os tokens relevantes apareçam em nome).
    """
    # 1) Checagem direta por EAN
    try:
        if cod_produto:
            sku = Skus_validos.objects.filter(ean=cod_produto).order_by('id').first()
            if sku:
                return sku
    except Exception:
        pass

    # 2) Fallback por similaridade usando a descrição
    if descricao:
        print("[VALIDAR_PRODUTO] Iniciando fallback por descrição:", descricao)
        try:
            desc = str(descricao).upper()
            # Tokeniza mantendo letras/números, removendo tokens curtos
            tokens = [t for t in re.split(r"[^A-Z0-9]+", desc) if len(t) >= 3]
            print("[VALIDAR_PRODUTO] Tokens extraídos:", tokens)
            if not tokens:
                print("[VALIDAR_PRODUTO] Nenhum token relevante encontrado.")
                return False
            qs = Skus_validos.objects.all()
            total = qs.count()
            print("[VALIDAR_PRODUTO] SKUs iniciais:", total)

            # Sensibilidade: pelo menos 50% dos tokens devem bater (full ou prefixo de 4)
            COVERAGE_MIN = 0.5

            # Pré-filtro: OR de todos os tokens/prefixos para reduzir candidatos
            combined_q = Q()
            for t in tokens:
                pref = t[:4] if len(t) > 4 else t
                combined_q |= Q(nome__icontains=t) | Q(nome__icontains=pref)

            candidatos = list(qs.filter(combined_q))
            print(f"[VALIDAR_PRODUTO] Candidatos após pré-filtro OR: {len(candidatos)} de {total}")

            melhor = None
            melhor_cov = 0.0
            for c in candidatos:
                nome_up = (c.nome or "").upper()
                if not nome_up:
                    continue
                acertos = 0
                for t in tokens:
                    pref = t[:4] if len(t) > 4 else t
                    if t in nome_up or pref in nome_up:
                        acertos += 1
                cobertura = acertos / len(tokens)
                if cobertura >= COVERAGE_MIN:
                    # guarda o de maior cobertura
                    if cobertura > melhor_cov:
                        melhor = c
                        melhor_cov = cobertura

            if melhor:
                print(f"[VALIDAR_PRODUTO] Correspondência por descrição: id={melhor.id}, ean={melhor.ean}, cobertura={melhor_cov:.0%}")
                return melhor
            else:
                print("[VALIDAR_PRODUTO] Nenhuma correspondência final encontrada com cobertura mínima de 50%.")
        except Exception as e:
            print("[VALIDAR_PRODUTO] Erro no fallback por descrição:", e)
            return False

    return False


def gerar_numero_sorte():
    """
    Escolhe aleatoriamente uma série entre 00 e 99, mas evitando repetir
    qualquer uma das últimas 95 séries utilizadas. Em seguida, gera os 5
    dígitos finais aleatórios e garante unicidade do número completo.
    """
    # Coleta as últimas 95 séries usadas (prefixos dos números existentes)
    recentes = list(NumeroDaSorte.objects.order_by('-id').values_list('numero', flat=True)[:95])
    series_bloqueadas = set()
    for n in recentes:
        pref = str(n)[:2]
        if pref.isdigit():
            try:
                series_bloqueadas.add(int(pref))
            except Exception:
                continue

    # Candidatas são todas as séries 0..99 que não estão entre as bloqueadas
    candidatas = [s for s in range(100) if s not in series_bloqueadas]
    if not candidatas:
        # Segurança: caso extremo, libera todas
        candidatas = list(range(100))

    proxima_serie = random.choice(candidatas)

    # Gera 5 dígitos aleatórios e garante unicidade do número completo
    max_tentativas = 300
    for _ in range(max_tentativas):
        ultimos_cinco = random.randint(0, 99999)
        numero_sorte = f"{proxima_serie:02d}{ultimos_cinco:05d}"
        if not NumeroDaSorte.objects.filter(numero=numero_sorte).exists():
            return numero_sorte

    # Fallback extremo: tenta com outra série disponível, se houver
    for s in candidatas:
        ultimos_cinco = random.randint(0, 99999)
        numero_sorte = f"{s:02d}{ultimos_cinco:05d}"
        if not NumeroDaSorte.objects.filter(numero=numero_sorte).exists():
            return numero_sorte

    # Último fallback: retorna mesmo que exista (chance ínfima de colisão)
    ultimos_cinco = random.randint(0, 99999)
    return f"{proxima_serie:02d}{ultimos_cinco:05d}"


def edita_numero_serie(id, num_serie, status):
    serie_atual = Serie.objects.get(id=id)
    serie_atual.numero_atual = num_serie
    serie_atual.status = status
    serie_atual.save()


def completa_numero(numero, tamanho):
    return str(numero).zfill(tamanho)


def cadastrar_numeros_da_sorte(cupom):
    # Baseado nos produtos já salvos (modelo Produto) vinculados ao cupom
    total_valido = 0
    tem_acelerador = False

    produtos = Produto.objects.filter(cupom=cupom).select_related('sku_validado')
    print(f"[NUM_SORTE] Produtos do cupom {cupom.id}: {produtos.count()}")

    for p in produtos:
        sku = p.sku_validado
        if not sku:
            continue
        try:
            qtd = int(p.quantidade)
        except Exception:
            qtd = 0
        total_valido += max(0, qtd)
        if getattr(sku, 'is_acelerador', False):
            tem_acelerador = True

    n_por_quantidade = total_valido // 3
    n_por_acelerador = 1 if tem_acelerador else 0
    total_numeros = n_por_quantidade + n_por_acelerador

    if total_numeros == 0:
        return "Cupom não tem direito a números da sorte."

    # Impõe limite de no máximo 2 números por cupom, considerando os já existentes
    existentes = NumeroDaSorte.objects.filter(cupom=cupom).count()
    disponiveis = max(0, 2 - existentes)

    if disponiveis == 0:
        return "Cupom já possui o limite de 2 números da sorte."

    total_numeros = min(total_numeros, disponiveis)

    for _ in range(total_numeros):
        num_sorte = gerar_numero_sorte()
        NumeroDaSorte.objects.create(
            cupom=cupom,
            participante=cupom.participante,
            numero=num_sorte,
            status='ativo'
        )

    return f"Foram cadastrados {total_numeros} números da sorte."