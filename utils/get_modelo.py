from dataclasses import dataclass

@dataclass
class DocumentoFiscal:
    valida: bool
    mensagem: str
    tipo_documento: str
    uf_codigo: str
    ano_emissao: str
    mes_emissao: str
    cnpj_emitente: str
    modelo: str
    serie: int
    numero_nota: int
    codigo_numerico: str
    dv_informado: str
    dv_calculado: str
    chave: str


def calcular_dv_sat(chave_sem_dv: str) -> str:
    pesos = [2, 3, 4, 5, 6, 7, 8, 9]
    soma = 0
    # percorre de trás para frente (reverso)
    for i, digito in enumerate(reversed(chave_sem_dv)):
        soma += int(digito) * pesos[i % len(pesos)]
    resto = soma % 11
    dv = 11 - resto
    if dv in [10, 11]:
        dv = 0
    return str(dv)



def calcular_dv_nfe_nfce(chave_sem_dv: str) -> str:
    pesos = [2, 3, 4, 5, 6, 7, 8, 9]
    soma = 0
    peso_idx = 0
    for digito in reversed(chave_sem_dv):
        soma += int(digito) * pesos[peso_idx]
        peso_idx = (peso_idx + 1) % len(pesos)
    resto = soma % 11
    dv = 11 - resto
    if dv >= 10:
        dv = 0
    return str(dv)

def identificar_chave_detalhada(chave: str) -> DocumentoFiscal:
    chave_limpa = ''.join(filter(str.isdigit, chave))
    if len(chave_limpa) != 44:
        return DocumentoFiscal(
            valida=False,
            mensagem="Chave inválida: deve conter 44 dígitos.",
            tipo_documento="Desconhecido",
            uf_codigo="",
            ano_emissao="",
            mes_emissao="",
            cnpj_emitente="",
            modelo="",
            serie=0,
            numero_nota=0,
            codigo_numerico="",
            dv_informado="",
            dv_calculado="",
            chave=chave_limpa
        )

    uf_codigo = chave_limpa[0:2]
    ano_emissao = "20" + chave_limpa[2:4]
    mes_emissao = chave_limpa[4:6]
    cnpj_emitente = chave_limpa[6:20]
    modelo = chave_limpa[20:22]
    serie = int(chave_limpa[22:25])
    numero_nota = int(chave_limpa[25:34])
    codigo_numerico = chave_limpa[34:43]
    dv_informado = chave_limpa[43]

    tipo_documento = (
        "NF-e" if modelo == "55" 
        else "NFC-e" if modelo == "65" 
        else "SAT-cfe" if modelo == "59" 
        else "Desconhecido"
    )

    if tipo_documento == "Desconhecido":
        return DocumentoFiscal(
            valida=False,
            mensagem=f"Modelo inválido: {modelo}",
            tipo_documento=tipo_documento,
            uf_codigo=uf_codigo,
            ano_emissao=ano_emissao,
            mes_emissao=mes_emissao,
            cnpj_emitente=cnpj_emitente,
            modelo=modelo,
            serie=serie,
            numero_nota=numero_nota,
            codigo_numerico=codigo_numerico,
            dv_informado=dv_informado,
            dv_calculado="",
            chave=chave_limpa
        )

    if tipo_documento == "SAT":
        dv_calculado = calcular_dv_sat(chave_limpa[:-1])
    else:
        dv_calculado = calcular_dv_nfe_nfce(chave_limpa[:-1])

    valida = dv_informado == dv_calculado

    mensagem = "Chave válida." if valida else "Chave inválida (DV ou modelo incorreto)."

    return DocumentoFiscal(
        valida=valida,
        mensagem=mensagem,
        tipo_documento=tipo_documento,
        uf_codigo=uf_codigo,
        ano_emissao=ano_emissao,
        mes_emissao=mes_emissao,
        cnpj_emitente=cnpj_emitente,
        modelo=modelo,
        serie=serie,
        numero_nota=numero_nota,
        codigo_numerico=codigo_numerico,
        dv_informado=dv_informado,
        dv_calculado=dv_calculado,
        chave=chave_limpa
    )

# Exemplo rápido
# chave_teste = "35250501157555004100590004797948322835671276"
# print(identificar_chave_detalhada(chave_teste))
