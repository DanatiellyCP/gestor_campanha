import datetime
from participantes.models import Participantes
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
import re
from participantes.forms import ParticipanteForm

from datetime import datetime

def participe(request):
    # lógica da view
    return render(request, 'participe.html')



def como_participar(request):    
    return render(request, 'como-participar.html')

def produtos(request):    
    return render(request, 'produtos.html')
    
def lista_resultado(request):    
    return render(request, 'lista-resultados.html')

def duvidas(request):    
    return render(request, 'duvidas.html')

def cadastrar(request):    
    return render(request, 'cadastrar.html')

def logar(request):
    return render(request, 'logar.html')

def painel_home(request):
    return render(request, 'painel_home.html')

def painel_cadastrar_cupom(request):
    return render(request, 'painel_cadastrar_cupom.html')

