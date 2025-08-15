from django.http import HttpResponse
from django.template import loader

from .models import Usuarios
from participantes.models import Participantes
from datetime import date, datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from functools import wraps
from utils.funcoes import limpar_lista_sku, retorna_atividades
from utils.link_sefaz import gerar_link_sefaz
from django.core.paginator import Paginator
from django.db.models import Q
from cupons.models import Cupom, NumeroDaSorte
from campanha.models import Regras


from campanha.models import Sorteios
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncMonth

 

## Função para restringir acessos por niveis - Danny - 27-06-2025
def nivel_required(nivel_permitido):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.nivel == nivel_permitido:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Acesso não autorizado")
        return _wrapped_view
    return decorator


## Função para restringir acesso apenas para administradores - Danny - 27-06-2025
def is_admin(user):
    return user.nivel == 'admin'

def home(request):
  template = loader.get_template('home.html')
  return HttpResponse(template.render())
  

@login_required
##@nivel_required('admin')
def cadastro(request):
  # salvar os dados da tela para o banco de dados
  if request.method == "GET": 
    return render(request, 'cadastro.html')
  elif request.method == "POST":
    nome = request.POST.get('nome')
    usr = request.POST.get('usuario')
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    #hashed_password = make_password(password=str(senha), salt='xxsaw21', hasher='pbkdf2_sha256')

    status = request.POST.get('status')
    ativo = True if status == "1" or status.lower() == "ativo" else False
    
    nivel = request.POST.get('nivel')
    if (nivel != '1') or (nivel != '2') or (nivel != '3'):
       nivel = 0

    

    #avatar = request.POST.get('avatar_escolhido')
    #avatar_selecionado =  '/statc/avatar/' + avatar


    novo_usuario = Usuarios.objects.create_user(username = usr, 
                                                password = senha, 
                                                last_login = date.today(),
                                                is_superuser = False,
                                                is_staff = False,
                                                first_name = nome,
                                                email = email,
                                                is_active = ativo,
                                                nivel = nivel)
                                                #foto = avatar_selecionado)

    novo_usuario.save()
    return redirect('usuarios')
  
@login_required(login_url='login')
def sistema(request):
  current_user = request.user

  nivel_logado = current_user.nivel
  atividades = retorna_atividades(nivel_logado)

  context = {
    'usuario': current_user,
    'atividades_usuario': atividades
  }


  template = loader.get_template('sistema.html')
  return HttpResponse(template.render(context, request))

@login_required
def usuarios(request):
  usuarios = Usuarios.objects.all().values()
  template = loader.get_template('todos_usuarios.html')
  context = {
    'usuarios': usuarios,
  }
  return HttpResponse(template.render(context, request))

# dash
@login_required
def dash(request):
  # pegar os dados que serão exibidos 
  participantes = Participantes.objects.all().count
  cupons =  Cupom.objects.all().count
  numeros_sorte = NumeroDaSorte.objects.all().count
  sorteios = Sorteios.objects.all().count

  context = {
     'participantes' : participantes,
     'cupons' : cupons,
     'numeros_sorte': numeros_sorte,
     'sorteios' : sorteios
  }


  template = loader.get_template('dash.html')
  return HttpResponse(template.render(context, request))

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {
        'regioes': REGIOES.keys()
    })


from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncMonth
from datetime import datetime
from participantes.models import Participantes

# Mapeamento de estados por região
REGIOES = {
    'Norte': ['AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO'],
    'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
    'Centro-Oeste': ['DF', 'GO', 'MT', 'MS'],
    'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
    'Sul': ['PR', 'RS', 'SC']
}

# Página de gráficos
def graficos_participantes(request):
    return render(request, 'graficos_participantes.html', {
        'regioes': REGIOES.keys()
    })

# Dados para os gráficos (AJAX)
def participantes_dados(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    regiao = request.GET.get('regiao')

    participantes = Participantes.objects.all()

    # Filtrar por data_cadastro
    if data_inicio and data_fim:
        try:
            inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            fim = datetime.strptime(data_fim, "%Y-%m-%d")
            participantes = participantes.filter(data_cadastro__range=[inicio, fim])
        except:
            pass

    # Filtrar por região
    if regiao in REGIOES:
        participantes = participantes.filter(uf__in=REGIOES[regiao])

    # Gráfico de barras: participantes por mês
    participantes_mes = (
        participantes
        .annotate(mes=TruncMonth('data_cadastro'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    labels_mes = [p['mes'].strftime('%m/%Y') for p in participantes_mes]
    dados_mes = [p['total'] for p in participantes_mes]

    # Gráfico de pizza: participantes por região
    dados_estado = []
    labels_estado = []
    for reg, estados in REGIOES.items():
        count = participantes.filter(uf__in=estados).count()
        if count > 0:
            labels_estado.append(reg)
            dados_estado.append(count)

    return JsonResponse({
        'labels_mes': labels_mes,
        'dados_mes': dados_mes,
        'labels_estado': labels_estado,
        'dados_estado': dados_estado
    })


@login_required
def relatorios(request):
  template = loader.get_template('relatorios.html')
  return HttpResponse(template.render())


# Detalhamento de usuarios
@login_required
def detalhe(request, id):
  usuario = Usuarios.objects.get(id=id)
  template = loader.get_template('detalhe.html')
  context = {
    'usuarios': usuario,
  }
  return HttpResponse(template.render(context, request))

# Deletar usuarios
@login_required
def deletar(request, id):
  usuario = Usuarios.objects.get(id=id)
  usuario.delete()
  return redirect('usuarios')

# Editar usuarios
@login_required
def editar(request, id):
  if request.method == "GET": 
    return render(request, 'usuarios.html')
  elif request.method == "POST":
    usuario = Usuarios.objects.get(id=id)
    usr = request.POST.get('usuario')
    email = request.POST.get('email')
    
    status = request.POST.get('status')
    ativo = True if status == "1" or status.lower() == "ativo" else False

    nivel = request.POST.get('nivel')

    usuario.username = usr 
    usuario.email = email
    usuario.is_active = ativo
    usuario.nivel = nivel
    
    usuario.save()
    return redirect('usuarios')

# Editar perfil do usuarios
@login_required
def perfil(request, id):
  if request.method == "GET": 
    return render(request, 'sistema.html')
  elif request.method == "POST":

    usuario = Usuarios.objects.get(id=id)

    nome  = request.POST.get('nome')
    usr   = request.POST.get('usuario')
    email = request.POST.get('email')
    
    senha = request.POST.get('senha')
    if senha != '*******':
      usuario.password = make_password(senha)

    usuario.first_name = nome
    usuario.username = usr 
    usuario.email = email
    
    usuario.save()
    return redirect('sistema')
  


@login_required
def dados_participantes(request):
    search_query = request.GET.get('q', '')

    participantes = Participantes.objects.annotate(
        total_cupons=Count('cupom')  # 'cupom' = related_name do FK em Cupom
    )

    if search_query:
        participantes = participantes.filter(
            Q(nome__icontains=search_query) |
            Q(cpf__icontains=search_query) |
            Q(email__icontains=search_query)|
            Q(celular__icontains=search_query)
        )

    total_part = participantes.count()

    # Paginação
    paginator = Paginator(participantes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Lógica de páginas com elipses
    current_page = page_obj.number
    total_pages = paginator.num_pages
    if total_pages <= 7:
        page_range = range(1, total_pages + 1)
    else:
        if current_page <= 4:
            page_range = list(range(1, 6)) + ['...', total_pages]
        elif current_page >= total_pages - 3:
            page_range = [1, '...'] + list(range(total_pages - 4, total_pages + 1))
        else:
            page_range = [1, '...'] + list(range(current_page - 1, current_page + 2)) + ['...', total_pages]

    return render(request, 'dados_participantes.html', {
        'page_obj': page_obj,
        'page_range': page_range,
        'Total': total_part,
        'search_query': search_query,
        'msg': ''
    })




"""
def dados_participantes(request):
    # QuerySet de participantes
    lista_participantes = Participantes.objects.all()

    # Criar paginator - 5 itens por página
    participantes_paginator = Paginator(lista_participantes, 5)

    # Número da página atual (padrão: 1)
    page_num = request.GET.get('page')
    page = participantes_paginator.get_page(page_num)

    # Renderizar template
    template = loader.get_template('dados_participantes.html')
    context = {
        'page': page
    }
    return HttpResponse(template.render(context, request))
"""


@login_required
def sorteios(request):
  template = loader.get_template('sorteios.html')
  return HttpResponse(template.render())


# Editar Participantes
@login_required
def editar_participante(request):
    if request.method == "POST":
        # Pegamos o ID do participante enviado pelo botão Salvar
        participante_id = request.POST.get('id_participante')

        participante = get_object_or_404(Participantes, id=participante_id)

        # Capturamos os campos editáveis (note o uso do ID no nome dos campos)
        participante.nome = request.POST.get(f'nome_{participante_id}')
        participante.cpf = request.POST.get(f'cpf_{participante_id}')
        participante.email = request.POST.get(f'email_{participante_id}')
        participante.celular = request.POST.get(f'celular_{participante_id}')
        # A coluna cupons é só leitura, então não alteramos aqui

        participante.save()

        return redirect('dados_participantes')

    # Se cair em GET, apenas redireciona
    return redirect('dados_participantes')


# Detalhamento de participante
@login_required
def participante_detalhado(request, id):
  participante = Participantes.objects.get(id=id)
  
  # Busca todos os cupons e números da sorte relacionados
  cupons_participante = Cupom.objects.filter(participante=participante.id)
  numeros_sorte = NumeroDaSorte.objects.filter(participante=participante.id)

  template = loader.get_template('participante_detalhado.html')
  context = {
    'participante': participante,
    'cupons': cupons_participante,
    'numeros_sorte' : numeros_sorte
  }
  return HttpResponse(template.render(context, request))


# Pesquisar participante por nome ou por cpf
@login_required
def pesquisar_participante(request):
  if request.method == "GET": 
    template = loader.get_template('pesquisar_participante.html')
    context = {
      'participante': '',
    }
    return HttpResponse(template.render(context, request))
    
  elif request.method == "POST":
    texto = request.POST.get('texto')
    
    try:
      participante = Participantes.objects.get(cpf=texto) 
      template = loader.get_template('pesquisar_participante.html')
      context = {
        'participante': participante,
       
      }
      return HttpResponse(template.render(context, request))
    
    except Participantes.DoesNotExist:
       template = loader.get_template('pesquisar_participante.html')
       context = {
        'mensagem': 'Não houve retorno para essa pesquisa. Tente usar outro parâmetro'
       }
       return HttpResponse(template.render(context, request))


def deletar_skus(request):
  current_user = request.user
  nivel_logado = current_user.nivel
  atividades = retorna_atividades(nivel_logado)


  if current_user.is_superuser == 1:
    try:
      msg = limpar_lista_sku('skus_validos') 
    except:
      msg = 'Não foi possível limpara a lista - Consultar a equipe de desenvolvimento'
    
    context = {
      'usuario': current_user,
      'atividades_usuario': atividades,
      'msg_sku' : msg
    }
    template = loader.get_template('sistema.html')
    return HttpResponse(template.render(context, request))
  
  else:
    msg = 'Usuário não altorizado a fazer essa ação!'
    context = {
      'usuario': current_user,
      'atividades_usuario': atividades,
      'msg_sku' : msg
    }
    template = loader.get_template('sistema.html')
    return HttpResponse(template.render(context, request))


@login_required
def cupons_enviados(request):
    lista_cupons = Cupom.objects.all().values()
    total_cup = Cupom.objects.count()

    paginator = Paginator(lista_cupons, 10)  # 10 cupons por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Lógica de elipses
    current_page = page_obj.number
    total_pages = paginator.num_pages
    if total_pages <= 7:
        page_range = range(1, total_pages + 1)
    else:
        if current_page <= 4:
            page_range = list(range(1, 6)) + ["...", total_pages]
        elif current_page >= total_pages - 3:
            page_range = [1, "..."] + list(range(total_pages - 4, total_pages + 1))
        else:
            page_range = [1, "..."] + list(range(current_page - 1, current_page + 2)) + ["...", total_pages]

    context = {
        'page_obj': page_obj,
        'page_range': page_range,
        'Total': total_cup
    }
    return render(request, 'cupons_enviados.html', context)



# Deletar participantes
@login_required
def deletar_participante(request, id):
  participante = Participantes.objects.get(id=id)
  participante.delete()
  return redirect('dados_participantes')  


# gerar a lista csv com os dados do sorteio
@login_required
def gerar_lista_csv(request):
  ...
    
@login_required
def editar_regra(request):
    # Se tiver apenas uma regra, pega ela, senão pega a primeira
    regra = Regras.objects.first()
    if not regra:
        regra = Regras.objects.create(
            min_data_cupom_aceito="01/01/2025",
            max_data_cupom_aceito="31/12/2025",
            qtd_cupom_dia=1
        )

    if request.method == "POST":
        regra.min_data_cupom_aceito = request.POST.get("min_data_cupom_aceito")
        regra.max_data_cupom_aceito = request.POST.get("max_data_cupom_aceito")
        regra.qtd_cupom_dia = request.POST.get("qtd_cupom_dia")
        regra.save()
        return redirect("editar_regra")

    context = {
        "regra": regra
    }
    return render(request, "regras.html", context)


# - CAMPANHA
# usuarios/views.py
def sorteios(request):
  if request.method == 'POST':
      data_sorteio = request.POST.get('data_sorteio')
      hora_sorteio = request.POST.get('hora_sorteio')
      usuario_id = request.POST.get('usuario_id')
      status = request.POST.get('status')
      observacoes = request.POST.get('observacoes')
      resultado_sorteio = request.POST.get('resultado_sorteio')

      current_user = request.user
   
      Sorteios.objects.create(
        data_cadastro=date.today(),
        hora_cadastro=datetime.now().time(),
        usuario_id=current_user,
        data_sorteio=data_sorteio,
        hora_sorteio=hora_sorteio,
        status=status,
        observacoes=observacoes,
        resultado_sorteio=resultado_sorteio
      )
      return redirect("sorteios")
  else:
      sorteios = Sorteios.objects.all().values()
      context = {
        "sorteios": sorteios
      } 
      return render(request, "sorteios.html", context)
  


# LISTA EM FORMATO CSV PARA SORTEIO
def filtrar_lista_sorteio(data_inicio, data_fim):
   # Query ORM equivalente à sua SQL com WHERE entre datas
  numeros = NumeroDaSorte.objects.select_related('participante', 'cupom').filter(
      cupom__data_cadastro__range=(data_inicio, data_fim)
  ).values(
      'numero',
      'participante__cpf',
      'participante__email',
      'participante__celular',
      'participante__nome',
      'cupom__data_cadastro',
      'cupom__hora_cadastro'
  )

  # Exemplo de como percorrer os resultados
  #for n in numeros:
      #print(n)
  return numeros

def listagem_sorteio(request):
   context = {'':''}
   if request.method == 'POST':
      data_inicio = request.POST.get('data_inicio')
      data_fim = request.POST.get('data_fim')
      
      numeros = filtrar_lista_sorteio(data_inicio, data_fim)
      context = {
        "numeros": numeros
      } 
      return render(request, "listagem_sorteio.html", context)
   else:
      return render(request, "listagem_sorteio.html", context)
     




    
