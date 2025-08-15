### FUNÇÕES PARA A VALIDAÇÃO DE CUPONS DE CONSUMIDOR E NOTAS FISCAIS
import requests
import json
import os
import re
import base64
from io import BytesIO

try:
    from PIL import Image  # type: ignore
except Exception:
    Image = None  # type: ignore

try:
    import pytesseract  # type: ignore
except Exception:
    pytesseract = None  # type: ignore

# OpenCV e numpy para leitura de QR a partir de imagem
try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # mantém import opcional para ambientes sem cv2
    cv2 = None  # type: ignore
    np = None  # type: ignore

# Fallback com pyzbar
try:
    from pyzbar.pyzbar import decode as zbar_decode  # type: ignore
except Exception:
    zbar_decode = None  # type: ignore

from utils.get_modelo import identificar_chave_detalhada

def extrair_texto_ocr(imagem_path):
    """
    Recebe o caminho da imagem e retorna o texto extraído via OCR.
    """
    # Se dependências de OCR não estiverem disponíveis no servidor, não quebre o fluxo
    if Image is None or pytesseract is None:
        return ""
    try:
        imagem = Image.open(imagem_path)
        texto = pytesseract.image_to_string(imagem, lang="por")
        return texto
    except Exception as e:
        print(f"Erro ao processar OCR: {e}")
        return ""



def parse_dados_cupom(texto):
    """Extrai dados estruturados do conteúdo OCR do QR Code (modelo SAT SP)."""
    dados = {}

    # CNPJ
    cnpj_match = re.search(r'CNPJ\s*[:\-]?\s*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', texto)
    if cnpj_match:
        dados['cnpj'] = cnpj_match.group(1)

    # Data e hora
    data_match = re.search(r'Data[:\-]?\s*(\d{2}/\d{2}/\d{4})', texto)
    hora_match = re.search(r'(\d{2}:\d{2}:\d{2})', texto)
    if data_match:
        dados['data'] = data_match.group(1)
    if hora_match:
        dados['hora'] = hora_match.group(1)

    # Valor total
    total_match = re.search(r'Total[:\-]?\s*R?\$?\s*([0-9,.]+)', texto, re.IGNORECASE)
    if total_match:
        dados['total'] = total_match.group(1)

    # Número SAT
    sat_match = re.search(r'SAT[:\-]?\s*(\d+)', texto)
    if sat_match:
        dados['sat'] = sat_match.group(1)

    # Chave QR (44 dígitos)
    chave_match = re.search(r'\b(\d{44})\b', texto)
    if chave_match:
        dados['chave_qr'] = chave_match.group(1)

    return dados

def _to_pil_image(source):
    """
    Aceita vários formatos de entrada e retorna um PIL.Image.
    - source pode ser: caminho (str), bytes, BytesIO, ContentFile (Django) ou já uma Image.
    """
    if isinstance(source, Image.Image):
        return source
    if isinstance(source, (bytes, bytearray)):
        return Image.open(BytesIO(source))
    # ContentFile tem atributo 'read' e possivelmente 'name'
    if hasattr(source, 'read') and callable(source.read):
        try:
            data = source.read()
            # reseta ponteiro se possível, pois o chamador pode reutilizar
            try:
                source.seek(0)
            except Exception:
                pass
            return Image.open(BytesIO(data))
        except Exception:
            pass
    # Caminho de arquivo
    if isinstance(source, str) and os.path.exists(source):
        return Image.open(source)
    # Último recurso: tentar interpretar como data URL base64
    if isinstance(source, str) and source.startswith('data:'):
        try:
            head, b64 = source.split(',', 1)
            raw = base64.b64decode(b64)
            return Image.open(BytesIO(raw))
        except Exception:
            pass
    raise ValueError("Formato de imagem não suportado para leitura de QR.")


def decode_qr_image(source):
    """
    Decodifica QR Code a partir de uma imagem (arquivo/bytes/ContentFile/PIL.Image).
    Tenta primeiro com OpenCV; se falhar, tenta pyzbar.
    Retorna o texto do QR ou string vazia.
    """
    try:
        pil_img = _to_pil_image(source).convert('RGB')
    except Exception:
        return ''

    # OpenCV
    if cv2 is not None and np is not None:
        try:
            arr = np.array(pil_img)
            # PIL RGB -> BGR
            img_bgr = arr[:, :, ::-1]
            detector = cv2.QRCodeDetector()
            data, points, _ = detector.detectAndDecode(img_bgr)
            if data:
                return data.strip()
        except Exception:
            pass

    # pyzbar fallback
    if zbar_decode is not None:
        try:
            results = zbar_decode(pil_img)
            if results:
                # pega o primeiro
                data = results[0].data.decode('utf-8', errors='ignore')
                return data.strip()
        except Exception:
            pass

    return ''


def _parse_qr_payload_to_key(payload: str) -> str:
    """
    Recebe o texto contido no QR e tenta extrair a chave de acesso (44 dígitos).
    Suporta SAT (CFe...|...) e NFE/NFCE (apenas 44 dígitos no texto/URL).
    """
    if not payload:
        return ''
    txt = str(payload).strip()
    if txt.startswith('CFe'):
        pos = txt.find('|')
        head = txt[:pos] if pos > -1 else txt
        somente_digitos = re.sub(r'\D', '', head)
        return somente_digitos
    # Tenta 44 dígitos
    m = re.search(r"\b(\d{44})\b", txt)
    return m.group(1) if m else ''


def extrai_codigo_qrcode(source):
    """
    Lê um QR Code de uma imagem (arquivo/bytes/ContentFile/PIL.Image) e retorna a chave (44 dígitos)
    quando possível. Caso não encontre, retorna string vazia.
    """
    payload = decode_qr_image(source)
    if not payload:
        return ''
    chave = _parse_qr_payload_to_key(payload)
    return chave


def extrair_numero_cupom(texto):
    """
    Extrai a chave de acesso (44 dígitos) do cupom fiscal a partir de OCR ou QR Code.
    """
    match = re.search(r'\b\d{44}\b', texto)
    return match.group() if match else ''

def consulta_sefaz(url):
    dados_cupom = requests.POST(url)

    if dados_cupom.status_code == 200:
        print(dados_cupom.json())
        return dados_cupom.json()
    else:
        print(dados_cupom.status_code)
        return dados_cupom.status_code


# função para verificar se produtos em cupom enviado estão validos na campanha
def validar_produto(lista_produtos_cupom):
    for i in lista_produtos_cupom:
        if i == '':
            retorno = 'ok'


# extrair produtos do cupom
def extrair_produtos(cupom):
    ...

def validar_documento(codigo_documento):
    "função para validar notas enviadas, separar o tipo da nota, "
    "verificar se é autentica e extrair informações pelo codigo informado"
    dados = identificar_chave_detalhada(codigo_documento)
    return dados


def get_dados_json(dados_json, tipo_cupom):
    import json

    # Converte string JSON para dict
    if isinstance(dados_json, str):
        dados = json.loads(dados_json)
    else:
        dados = dados_json

    if tipo_cupom == 'SAT-cfe':
        cupom = dados["data"][0]
        emitente = cupom["emitente"]
        produtos = cupom.get("produtos", [])
        nfe = None
        cobranca = {
            "forma_pagamento": cupom.get("forma_pagamento")
        }
        chave_acesso = cupom.get("chave_acesso")

    elif tipo_cupom == 'NFC-e':
        cupom = dados[0]
        emitente = cupom["emitente"]
        produtos = cupom.get("produtos", [])
        nfe = None
        cobranca = {
            "forma_pagamento": cupom.get("forma_pagamento")
        }
        chave_acesso = cupom.get("chave_acesso")

    elif tipo_cupom == 'NF-e':
        cupom = dados["data"][0]
        emitente = cupom["emitente"]
        produtos = cupom.get("produtos", [])
        nfe = cupom.get("nfe", {})
        cobranca = cupom.get("cobranca", {})
        chave_acesso = nfe.get("chave_acesso") or cupom.get("chave_acesso")

    else:
        raise ValueError(f"Tipo de cupom desconhecido: {tipo_cupom}")

    lista_produtos = []
    for i, p in enumerate(produtos, start=1):
        lista_produtos.append({
            "num": p.get("num") or i,
            "descricao": p.get("descricao"),
            "qtd": p.get("quantidade") or p.get("qtd"),
            "valor_unitario": p.get("valor_unitario") or p.get("valor_unitario_comercial"),
            "valor_total_item": p.get("valor_total_item") or p.get("valor"),
            "codigo": p.get("codigo") or p.get("ean_tributavel") or p.get("ean_comercial"),
            "ean": p.get("ean_tributavel") or p.get("ean_comercial")

        })

    emitente_formatado = {
        "nome": emitente.get("nome_razao_social") or emitente.get("nome"),
        "cnpj": emitente.get("cnpj"),
        "endereco": emitente.get("endereco"),
        "bairro": emitente.get("bairro"),
        "municipio": emitente.get("municipio"),
        "cep": emitente.get("cep")
    }

    resultado = {
        "emitente": emitente_formatado,
        "nfe": nfe,
        "cobranca": cobranca,
        "chave_acesso": chave_acesso,
        "produtos": lista_produtos
    }

    return resultado
