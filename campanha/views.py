"""
2. Validade do Cupom Fiscal:
Cupons com data de compra fora do período de participação (15/08/2025 a 15/10/2025) não devem ser aceitos.  
O sistema deve recusar o cadastro de cupons que contenham menos de 3 produtos da marca Bombril.  
Produtos vendidos de forma fracionada ou sem código de barras não são válidos para a promoção e não devem ser considerados.  

3. Limites e Duplicidade de Cadastro:
Um mesmo cupom fiscal não pode ser cadastrado mais de uma vez na promoção.  
Cada participante (identificado pelo CPF) pode cadastrar no máximo 1 (um) cupom fiscal por dia.  
O sistema deve limitar o cadastro a um total de 60 (sessenta) cupons fiscais por participante (CPF) durante todo o período da promoção.	

"""
from django.shortcuts import render
from datetime import date, datetime
from .models import Regras
from cupons.models import Cupom

from datetime import datetime, date
from .models import Regras
from cupons.models import Cupom

def Validar_regras_cupom(data_cupom, codigo_cupom, id_participante):
    # Se data_cupom vier como string, converte para date
    if isinstance(data_cupom, str):
        '''try:
            data_cupom = datetime.strptime(data_cupom, "dd/mm/yyyy").date()
        except ValueError:
            return False, "Data do cupom em formato inválido."'''
    
    

    regras = Regras.objects.first()
    if not regras:
        return False, "Nenhuma regra de validação foi configurada."

    data_min = regras.min_data_cupom_aceito  # date
    data_max = regras.max_data_cupom_aceito  # date
    qtd_dias = regras.qtd_cupom_dia

    if not (data_min <= data_cupom <= data_max):
        return False, f"Cupom fora do período permitido ({data_min} até {data_max})."

    if Cupom.objects.filter(numero_documento=codigo_cupom).exists():
        return False, "Este cupom já foi cadastrado anteriormente."

    data_atual = date.today()
    cupons_hoje = Cupom.objects.filter(
        participante=id_participante,
        data_cadastro=data_atual
    ).count()

    if cupons_hoje >= qtd_dias:
        return False, f"Limite diário de {qtd_dias} cupons atingido."

    return True, "Cupom válido."





