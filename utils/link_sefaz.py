def gerar_link_sefaz(chave: str) -> str | None:
    """
    Retorna o endpoint de consulta NFCe na API InfoSimples com base na UF extraída da chave.
    
    Parâmetros:
        chave (str): Chave NFCe com 44 caracteres numéricos.
    
    Retorna:
        str | None: URL de consulta ou None se inválida.
    """
    if not isinstance(chave, str) or len(chave) != 44 or not chave.isdigit():
        return None  # Chave inválida

    # Mapeamento código -> sigla UF
    codigos_uf = {
        "11": "ro", "12": "ac", "13": "am", "14": "rr", "15": "pa",
        "16": "ap", "17": "to", "21": "ma", "22": "pi", "23": "ce",
        "24": "rn", "25": "pb", "26": "pe", "27": "al", "28": "se",
        "29": "ba", "31": "mg", "32": "es", "33": "rj", "35": "sp",
        "41": "pr", "42": "sc", "43": "rs", "50": "ms", "51": "mt",
        "52": "go", "53": "df"
    }

    # Endpoints nfce InfoSimples
    links_infosimples = {
        uf: f"https://api.infosimples.com/api/v2/consultas/sefaz/{uf}/nfce"
              

              
        for uf in codigos_uf.values()
    }

    # Código numérico da UF (primeiros dois dígitos da chave)
    uf_codigo = chave[:2]
    uf_sigla = codigos_uf.get(uf_codigo)

    return links_infosimples.get(uf_sigla)