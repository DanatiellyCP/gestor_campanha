import requests
import logging
from django.conf import settings

def consulta_nfe(chave):
    api_key = 'gw0qcYijpRgnmpRCp6GM9oSUVYh2iRdA3PjxtBhu'
    url = 'https://api.infosimples.com/api/v2/consultas/receita-federal/nfe'
    args = {
      "nfe":  chave,       #"VALOR_DO_PARAMETRO_NFE",
      "token": api_key,      #"INFORME_AQUI_O_TOKEN_DA_CHAVE_DE_ACESSO",
      "timeout": 300
    }

    response = requests.post(url, args)
    response_json = response.json()
    response.close()

    if response_json['code'] == 200:
      print("Retorno com sucesso: ", response_json['data'])
    elif response_json['code'] in range(600, 799):
      mensagem = "Resultado sem sucesso. Leia para saber mais: \n"
      mensagem += "Código: {} ({})\n".format(response_json['code'], response_json['code_message'])
      mensagem += "; ".join(response_json['errors'])
      print(mensagem)

    print("Cabeçalho da consulta: ", response_json['header'])
    #print("URLs com arquivos de visualização (HTML/PDF): ", response_json['site_receipts'])

consulta_nfe('35250216911751000108550010000003841475354330')