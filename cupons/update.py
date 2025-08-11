from models.cupom import Cupom
import json

# Busca todos os cupons que têm dados_cupom preenchido
cupons = Cupom.objects.exclude(dados_cupom__isnull=True).exclude(dados_cupom="")

for cupom in cupons:
    try:
        # Se dados_cupom for string, converte para dict
        if isinstance(cupom.dados_cupom, str):
            dados = json.loads(cupom.dados_cupom.replace("'", '"'))  # tenta corrigir aspas simples
        else:
            dados = cupom.dados_cupom  # já é dict/JSONField

        tipo_doc = dados.get("tipo_documento")
        if tipo_doc:
            cupom.tipo_documento = tipo_doc
            cupom.save(update_fields=["tipo_documento"])
            print(f"Cupom {cupom.id} atualizado para {tipo_doc}")
        else:
            print(f"Cupom {cupom.id} não tem tipo_documento no JSON.")

    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON do cupom {cupom.id}: {cupom.dados_cupom}")
