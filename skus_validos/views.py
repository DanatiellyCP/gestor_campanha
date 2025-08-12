from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from gestor_campanha import settings
from .models import Skus_validos
import pandas as pd
import chardet
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def detectar_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def skus(request):
    # exibir as skus em tabela 
    #skus = Skus_validos.objects.all().values()
    skus = Skus_validos.objects.all().order_by('id').values()
    template = loader.get_template('skus.html')
    context = {
        'skus': skus,
    }
    return HttpResponse(template.render(context, request))




def import_data_from_csv(file_path):
    try:
        # Detectar encoding automaticamente
        encoding = detectar_encoding(file_path)
        print(f"Encoding detectado: {encoding}")

        # Ler CSV com encoding detectado
        df = pd.read_csv(file_path, encoding=encoding)

        # Limpar espaços dos nomes das colunas
        df.columns = df.columns.str.strip()

        # Inserir no banco
        for _, row in df.iterrows():
            Skus_validos.objects.create(
                nome=row.get('Nome'),
                ean=row.get('Ean'),
                dun=row.get('Dun'),
                categoria=row.get('Categoria')
            )

        print("✅ Dados importados com sucesso!")

    except Exception as e:
        print(f"❌ Erro durante a importação: {e}")




def salvar_arquivo_pasta(arquivo):
     # Caminho relativo dentro da pasta media
    nome_arquivo = arquivo.name
    caminho_arquivo = os.path.join('planilhas', nome_arquivo)

    # Salva o arquivo na pasta media/planilhas/
    path_salvo = default_storage.save(caminho_arquivo, ContentFile(arquivo.read()))
    return os.path.join(settings.MEDIA_ROOT, path_salvo)



def importar_skus(request):
    if request.method == "GET": 
        return render(request, 'importar_skus.html')

    elif request.method == "POST":
        planilha = request.FILES.get('planilha')
        if not planilha:
            return render(request, 'importar_skus.html', {'erro': 'Arquivo não enviado!'})

        # Salvar o arquivo na pasta
        caminho = salvar_arquivo_pasta(planilha)

        # Importar os dados
        import_data_from_csv(caminho)

        context = {
            'texto': f'{planilha.name} importada com sucesso!'
        }

        return render(request, 'importar_skus.html', context)


        
