import datetime
import json
import os
from django.http import HttpResponse
from django.template import loader

from cupons.models.produto import Produto
from .models import Participantes
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.core import serializers
from .forms import ParticipanteForm
from cupons.models import Cupom
from django.shortcuts import render, get_object_or_404, redirect

import re

from utils.funcoes_cupom import parse_dados_cupom, get_dados_json

from datetime import datetime

import ast

def login_participante(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            participante = Participantes.objects.get(email=email)
            if check_password(senha, participante.senha):
                # Autenticado com sucesso – salvar ID na sessão
                request.session['participante_id'] = participante.id
                return redirect('painel_participante')  # ou a página pós-login
            else:
                erro = "Senha incorreta."
        except Participantes.DoesNotExist:
            erro = "Participante não encontrado."

        return render(request, 'home_participantes.html', {'erro': erro})

    return render(request, 'home_participantes.html')


# -----------------------------------------------------------

def participante(request):
  template = loader.get_template('participante copy.html')
  return HttpResponse(template.render())

# ------------------------------------------

'''def cadastrar_participante(request):
    if request.method == 'POST':
        form = ParticipanteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_participante')
    else:
        form = ParticipanteForm()

    return render(request, 'cadastrar_participante.html', {'form': form})'''

def cadastrar_participante(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        dt_nasc = request.POST.get('dt_nasc')
        cpf = re.sub(r'\D', '', request.POST.get('cpf', ''))  # remove pontuação
        celular = re.sub(r'\D', '', request.POST.get('celular', ''))
        email = request.POST.get('email')
        uf = request.POST.get('uf')
        cidade = request.POST.get('cidade')
        cep = re.sub(r'\D', '', request.POST.get('cep', ''))
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        num = request.POST.get('num')
        senha = request.POST.get('senha')

        # Criptografa a senha
        senha_hash = make_password(senha)

        # Cria e salva o participante
        participante = Participantes(
            nome=nome,
            dt_nasc= datetime.strptime(dt_nasc, '%d/%m/%Y').date(),
            cpf=cpf,
            celular= '55' + celular,
            email=email,
            uf=uf,
            cidade=cidade,
            cep=cep,
            rua=rua,
            bairro=bairro,
            num=num,
            senha=senha_hash
        )
        participante.save()
        return redirect('login_participante')

    return render(request, 'cadastrar_participante.html')
#-------------------------------------------------------------------------------------


def painel_participante(request):
    participante_id = request.session.get('participante_id')
    if not participante_id:
        return redirect('login_participante')
    
    participante = Participantes.objects.get(id=participante_id)

    # filtrar cupons cadastrados para o participante 
    cupons_participante = Cupom.objects.filter(participante = participante_id)
    if cupons_participante == '':
        cupons_participante = 'False'

    context = {
        'cupons': cupons_participante,
        'participante': participante
    }
    
    template = loader.get_template('painel_participante.html')
    return HttpResponse(template.render(context, request))

def cupons_participante(request, id_cupom):
    participante_id = request.session.get('participante_id')
    if not participante_id:
        return redirect('login_participante')
    
    participante = Participantes.objects.get(id=participante_id)

    # filtrar cupons cadastrados para o participante 
    cupons_participante = Cupom.objects.filter(participante = participante_id)

    context = {
        'cupons': cupons_participante,
        'participante': participante
    }
    
    template = loader.get_template('cupom_detalhado.html')
    return HttpResponse(template.render(context, request))

def dados_cupom(request, id_cupom):
    cupom = Cupom.objects.get(id = id_cupom)
    template = loader.get_template('cupom_detalhado.html')
    context = {
        'cupom' : cupom
    }
    return HttpResponse(template.render(context, request))



def home_participantes(request):
    return render(request, 'home_participantes.html')

def como_participar(request):
    return render(request, 'como_participar.html')

def regulamento(request):
    return render(request, 'regulamento.html')

def FAQ(request):
    return render(request, 'FAQ.html')

def resultados(request):
    return render(request, 'resultados.html')

def editar_particip(request, id):
    participante = get_object_or_404(Participantes, id=id)

    if request.method == "POST":
        participante.nome = request.POST.get('nome')
        participante.celular = request.POST.get('celular')
        participante.email = request.POST.get('email')
        participante.save()

    # Recupera cupons do participante (após ou fora do POST)
    cupons_participante = Cupom.objects.filter(participante=participante)

    # Se não tiver cupons, define como False (opcional)
    if not cupons_participante.exists():
        cupons_participante = False

    context = {
        'cupons': cupons_participante,
        'participante': participante
    }

    return render(request, 'painel_participante.html', context)


def login_e_cadastro(request):
    # lógica da view
    return render(request, 'iframe_login_cadastro.html')

def iframe_login(request):
    # lógica da view
    return render(request, 'iframe_login.html')


#--------- PARTE DE EXTRAÇÃO DE VALIDAÇÃO DOS DADOS DO CUPOM --------------------------------


def area_cupom(request, id):
    cupom = get_object_or_404(Cupom, id=id)

    # Tenta processar os dados_json com tratamento de exceções
    try:
        dados_cupom = get_dados_json(cupom.dados_json, cupom.tipo_documento)
    except Exception as e:
        print(f"[ERRO] Falha ao processar dados_json do cupom {cupom.id}: {e}")
        dados_cupom = {}

    # Tenta converter dados_cupom do banco para dict Python
    try:
        if cupom.dados_cupom and isinstance(cupom.dados_cupom, str):
            dados_cupom_dict = ast.literal_eval(cupom.dados_cupom)
        elif isinstance(cupom.dados_cupom, dict):
            dados_cupom_dict = cupom.dados_cupom
        else:
            dados_cupom_dict = {}
    except Exception as e:
        print(f"[ERRO] Falha ao interpretar dados_cupom do cupom {cupom.id}: {e}")
        dados_cupom_dict = {}
    
    produtos_validos = Produto.objects.filter(cupom=id)

    contexto = {
        'cupom': cupom,
        'dados_cupom': dados_cupom_dict,
        'dados_json': dados_cupom,
        'produtos_validos': produtos_validos
    }

    return render(request, 'area_cupom.html', contexto)







    


    





