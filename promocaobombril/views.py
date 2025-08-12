from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password
from participantes.models import Participantes
from datetime import datetime
import re

# Decorator simples para exigir login via sessão

def require_login(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.session.get('participante_id'):
            return redirect('logar')
        return view_func(request, *args, **kwargs)
    return _wrapped

def participe(request):
    # lógica da view
    return render(request, 'participe.html')

def home_responsive(request):    
    return render(request, 'home_responsive.html')

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
        nome = request.POST.get('nome')
        dt_nasc_str = request.POST.get('nasc', '').strip()
        cpf = re.sub(r'\D', '', request.POST.get('cpf', ''))  # remove pontuação
        celular = re.sub(r'\D', '', request.POST.get('celular', ''))
        email = request.POST.get('email')
        uf = request.POST.get('estado', '').strip()  # nome do campo no template é 'estado'
        cidade = request.POST.get('cidade')
        cep = re.sub(r'\D', '', request.POST.get('cep', ''))
        rua = request.POST.get('logradouro')
        bairro = request.POST.get('bairro')
        num = request.POST.get('numero')
        senha = request.POST.get('senha')
        senha2 = request.POST.get('senha2')

        # Validações básicas
        if not uf:
            return render(request, 'cadastrar.html', {'erro': 'UF é obrigatória.'})
        if senha != senha2:
            return render(request, 'cadastrar.html', {'erro': 'As senhas não conferem.'})

        # Trata data de nascimento
        if dt_nasc_str:
            try:
                dt_nasc = datetime.strptime(dt_nasc_str, '%d/%m/%Y').date()
            except ValueError:
                return render(request, 'cadastrar.html', {'erro': 'Data de nascimento inválida. Use o formato dd/mm/aaaa.'})
        else:
            dt_nasc = None

        # Criptografa a senha
        senha_hash = make_password(senha)

        # Converte número da residência com segurança
        safe_num = None
        if num is not None:
            num = str(num).strip()
            if num:
                try:
                    safe_num = int(num)
                except ValueError:
                    safe_num = None

        # Cria e salva o participante
        participante = Participantes(
            nome=nome,
            dt_nasc=dt_nasc,
            cpf=cpf,
            celular= '55' + celular if celular else '',
            email=email,
            uf=uf,
            cidade=cidade,
            cep=cep,
            rua=rua,
            bairro=bairro,
            num=safe_num,
            senha=senha_hash
        )
        
        print('POST payload (raw):', {
            'nome': nome,
            'dt_nasc': dt_nasc_str,
            'cpf': cpf,
            'celular': celular,
            'email': email,
            'uf': uf,
            'cidade': cidade,
            'cep': cep,
            'rua': rua,
            'bairro': bairro,
            'num': num,
        })

        try:
            participante.save()
        except Exception as e:
            return render(request, 'cadastrar.html', {'erro': f'Erro ao salvar cadastro: {str(e)}'})
        return redirect('logar')
    # GET ou outro método: renderiza o formulário
    return render(request, 'cadastrar.html')

def logar(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            participante = Participantes.objects.get(email=email)
            if check_password(senha, participante.senha):
                # Autenticado com sucesso – salvar ID na sessão
                request.session['participante_id'] = participante.id
                return redirect('painel_home')  # ou a página pós-login
            else:
                erro = "Senha incorreta."
        except Participantes.DoesNotExist:
            erro = "Participante não encontrado."

        return render(request, 'logar.html', {'erro': erro})
    # GET: renderiza página de login
    return render(request, 'logar.html')

# Logout: limpa sessão e volta ao login

def logout_view(request):
    try:
        request.session.flush()
    except Exception:
        request.session.pop('participante_id', None)
    return redirect('logar')

@require_login
def painel_home(request):
    participante = None
    pid = request.session.get('participante_id')
    if pid:
        try:
            participante = Participantes.objects.get(id=pid)
        except Participantes.DoesNotExist:
            # Se algo der errado com a sessão, force logout
            return redirect('logout')

    # Atualização de dados via POST
    salvo = False
    if request.method == 'POST' and participante:
        nome = request.POST.get('nome', participante.nome)
        cpf = re.sub(r'\D', '', request.POST.get('cpf', participante.cpf or ''))
        email = request.POST.get('email', participante.email)
        celular = re.sub(r'\D', '', request.POST.get('celular', participante.celular or ''))

        participante.nome = nome
        participante.cpf = cpf
        participante.email = email
        participante.celular = celular
        participante.save()
        salvo = True

    context = {
        'participante': participante,
        'salvo': salvo,
    }
    return render(request, 'painel_home.html', context)

@require_login
def painel_cadastrar_cupom(request):
    return render(request, 'painel_cadastrar_cupom.html')
