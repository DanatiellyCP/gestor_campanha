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
from datetime import date
from .models import Regras
from cupons.models import Cupom

def Validar_regras_cupom(data_cupom, codigo_cupom, id_participante):
    # Obter regras (assumindo que há apenas um registro ativo)
    regras = Regras.objects.first()
    if not regras:
        return False, "Nenhuma regra de validação foi configurada."

    data_min = regras.min_data_cupom_aceito
    data_max = regras.max_data_cupom_aceito
    qtd_dias = regras.qtd_cupom_dia

    # 1. Validar data limite
    if not (data_min <= data_cupom <= data_max):
        return False, f"Cupom fora do período permitido ({data_min} até {data_max})."

    # 2. Validar se cupom já existe
    if Cupom.objects.filter(numero_documento=codigo_cupom).exists():
        return False, "Este cupom já foi cadastrado anteriormente."

    # 3. Validar quantidade de cupons por participante no dia
    data_atual = date.today()
    cupons_hoje = Cupom.objects.filter(
        participante=id_participante,
        data_cadastro=data_atual
    ).count()

    if cupons_hoje >= qtd_dias:
        return False, f"Limite diário de {qtd_dias} cupons atingido."

    # Se passou por todas as regras
    return True, "Cupom válido."




