### FUNÇÕES PARA A VALIDAÇÃO DE CUPONS DE CONSUMIDOR E NOTAS FISCAIS
import requests
import json
import os
import re

from utils.get_modelo import identificar_chave_detalhada

def extrair_texto_ocr(imagem_path):
    """
    Recebe o caminho da imagem e retorna o texto extraído via OCR.
    """
    try:
        imagem = Image.open(imagem_path)
        texto = pytesseract.image_to_string(imagem, lang="por")
        return texto
    except Exception as e:
        print(f"Erro ao processar OCR: {e}")
        return f"Erro ao processar OCR: {e}"



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

def extrai_codigo_qrcode(texto):
    #pegar o texto extraido pela camera e separa a parte do codigo do cupom - danny - 07-08-2025

    # copiar do 0 até a pos 77 #chave: CFe35250845495694001942590013611591810634041386|20250804173321|68.17|
    pos = texto.find("|")

    texto_qr_code = texto[0:pos]
    
    codigo = texto_qr_code.replace("CFe", "")
    codigo = codigo.replace(" ", "")

    print('pos ' + str(pos))
    print('texto_qr_code' + texto_qr_code)
    print('codigo: ' + codigo)

    return codigo


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

