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
    if request.method == 'POST':
        form = ParticipanteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('logar')
    else:
        form = ParticipanteForm()
    
    return render(request, 'cadastrar.html', {'form': form})

def logar(request):
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

        return render(request, 'logar.html', {'erro': erro})

    return render(request, 'logar.html')
