from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.hashers import check_password, make_password
from participantes.models import Participantes
from cupons.models.cupom import Cupom
from datetime import datetime
import re
import json
from dataclasses import asdict
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

# Lista de CPFs inválidos (importada do módulo dedicado)
from cpfs_invalidos import CPFS_INVALIDOS

# Conjunto para busca mais rápida (O(1))
CPFS_INVALIDOS_SET = set(CPFS_INVALIDOS)

# Helpers de cupom e validação
from utils.get_modelo import identificar_chave_detalhada
from utils.funcoes_cupom import (
    extrair_texto_ocr,
    extrair_numero_cupom,
    extrai_codigo_qrcode,
    get_dados_json,
)
from cupons.views import (
    guardar_cupom,
    validar_cupom,
    cadastrar_produto,
    cadastrar_numeros_da_sorte,
)
from cupons.models.numero_sorte import NumeroDaSorte

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

@csrf_exempt
def cpf_invalido_check(request):
    """
    Endpoint para verificar se um CPF está na lista de inválidos.
    Aceita CPF via querystring (?cpf=xxx) ou corpo POST (form/json).
    Retorna JSON apenas com booleano: true (existe) ou false (não existe)
    """
    cpf_raw = (
        request.GET.get('cpf')
        or request.POST.get('cpf')
        or ''
    )
    cpf = re.sub(r'\D', '', cpf_raw)
    if not cpf:
        # Sem CPF, respondemos false para manter contrato simples (apenas true/false)
        return JsonResponse(False, safe=False)

    exists = cpf in CPFS_INVALIDOS_SET
    return JsonResponse(exists, safe=False)

def home_responsive(request):    
    return render(request, 'home_responsive.html')

def como_participar(request):    
    return render(request, 'como-participar.html')

def tutorial(request):    
    return render(request, 'tutorial.html')

def produtos(request):    
    return render(request, 'produtos.html')
    
def lista_resultado(request):    
    return render(request, 'lista-resultados.html')

def duvidas(request):    
    return render(request, 'duvidas.html')

def regulamento(request):    
    return render(request, 'regulamentos.html')

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

        # Regra: impedir cadastro de menor de 18 anos
        if dt_nasc is not None:
            try:
                today = datetime.today().date()
                age = today.year - dt_nasc.year - ((today.month, today.day) < (dt_nasc.month, dt_nasc.day))
                if age < 18:
                    return render(request, 'cadastrar.html', {'erro': 'É necessário ser maior de 18 anos para se cadastrar.'})
            except Exception:
                # Em caso de qualquer falha inesperada no cálculo, retornar erro genérico de data
                return render(request, 'cadastrar.html', {'erro': 'Data de nascimento inválida.'})

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
        # Renderiza tela de sucesso para mostrar feedback e redirecionar após 5s
        return render(request, 'cadastrar.html', {'sucesso': True})
    return render(request, 'cadastrar.html')

def logar(request):
    if request.method == 'POST':
        cpf_raw = (request.POST.get('cpf') or '').strip()
        cpf = re.sub(r'\D', '', cpf_raw)
        senha = request.POST.get('senha') or ''

        if not cpf or not senha:
            return render(request, 'logar.html', {'erro': 'Informe CPF e senha.'})

        try:
            # Busca por CPF normalizado (somente dígitos); pega o mais recente por segurança
            participante = (
                Participantes.objects.filter(cpf=cpf).order_by('-id').first()
            )
            if not participante:
                return render(request, 'logar.html', {'erro': 'Participante não encontrado.'})

            # Senha pode estar ausente ou em formato inválido
            if not participante.senha:
                return render(request, 'logar.html', {'erro': 'Conta sem senha válida. Redefina sua senha.'})

            if check_password(senha, participante.senha):
                # Autenticado com sucesso – salvar ID na sessão
                request.session['participante_id'] = participante.id
                return redirect('painel_home')
            else:
                return render(request, 'logar.html', {'erro': 'Senha incorreta.'})
        except Exception as e:
            # Log opcional: print(e)
            return render(request, 'logar.html', {'erro': 'Não foi possível autenticar. Tente novamente.'})

    # GET: renderiza página de login e, se houver, mensagem de sucesso pós-cadastro
    sucesso = request.GET.get('signup') == '1'
    contexto = {}
    if sucesso:
        contexto['msg_sucesso'] = 'Cadastro realizado com sucesso! Faça login para continuar.'
    return render(request, 'logar.html', contexto)

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
    cupons_participantes = Cupom.objects.none()

    if pid:
        try:
            participante = Participantes.objects.get(id=pid)
            # Filtra os cupons do participante autenticado (mais recentes primeiro)
            cupons_participantes = Cupom.objects.filter(participante=participante).order_by('-data_cadastro', '-hora_cadastro')
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
        'cupons_participantes': cupons_participantes,
        'participante': participante,
        'salvo': salvo,
    }
    return render(request, 'painel_home.html', context)

@require_login
def painel_cadastrar_cupom(request):
    # Garantir que o template tenha o id do participante para montar a action corretamente
    pid = request.session.get('participante_id')
    if not pid:
        return redirect('logout')
    return render(request, 'painel_cadastrar_cupom.html', {'id_participante': pid})

@require_login
def painel_detalhes_cupom(request):
    # Garantir participante logado
    pid = request.session.get('participante_id')
    if not pid:
        return redirect('logout')

    # ID do cupom via querystring ?id=123
    try:
        cupom_id = int(request.GET.get('id', ''))
    except (TypeError, ValueError):
        return redirect('painel_home')

    # Busca cupom do participante
    try:
        participante = Participantes.objects.get(id=pid)
        cupom = Cupom.objects.select_related('participante').prefetch_related('produtos').get(
            id=cupom_id, participante=participante
        )
    except (Participantes.DoesNotExist, Cupom.DoesNotExist):
        return redirect('painel_home')

    # Produtos relacionados
    produtos = list(cupom.produtos.all())

    # Números da sorte relacionados
    numeros_objs = list(NumeroDaSorte.objects.filter(cupom=cupom).order_by('id'))
    numeros = [n.numero for n in numeros_objs]

    # Tenta extrair dados detalhados caso necessários no futuro
    dados_extra = None
    try:
        if cupom.dados_json:
            dados_extra = get_dados_json(cupom.dados_json, cupom.tipo_documento)
    except Exception:
        dados_extra = None

    contexto = {
        'cupom': cupom,
        'produtos': produtos,
        'numeros': numeros,
        'participante': participante,
        'dados_extra': dados_extra,
    }
    return render(request, 'painel_detalhes_cupom.html', contexto)


def cadastrar_cupom(request, id_participante):
    participante = get_object_or_404(Participantes, id=id_participante)
    contexto = {'id_participante': id_participante}

    if request.method == 'POST':
        chave_acesso = None
        dados_ocr = ""
        imagem_path = None
        erro = None

        try:
            if 'submit_codigo' in request.POST:
                # Captura e normaliza código digitado manualmente
                raw = (request.POST.get('cod_cupom') or '').strip()
                if raw:
                    if raw.startswith('CFe'):
                        # Formato SAT: usa a parte antes do '|', remove 'CFe' e espaços
                        pos = raw.find('|')
                        head = raw[:pos] if pos > -1 else raw
                        # Mantém somente dígitos
                        chave_acesso = re.sub(r'\D', '', head)
                    else:
                        # Remove não dígitos e espera 44 dígitos para NF-e/NFC-e
                        chave_acesso = re.sub(r'\D', '', raw)
                else:
                    chave_acesso = None

            elif 'submit_imagem' in request.POST:
                arquivo = request.FILES.get('img_cupom')
                if not arquivo:
                    erro = 'Nenhum arquivo de imagem foi selecionado.'
                else:
                    # Salva arquivo e obtém caminho local
                    imagem_path = guardar_cupom(arquivo)
                    imagem_local_path = default_storage.path(imagem_path)

                    # 1) Tenta extrair via QR Code a partir da imagem
                    try:
                        chave_acesso = extrai_codigo_qrcode(imagem_local_path)
                    except Exception:
                        chave_acesso = None

                    # 2) Se não encontrou por QR, tenta OCR + parse numérico (44 dígitos)
                    if not chave_acesso:
                        try:
                            dados_ocr = extrair_texto_ocr(imagem_local_path)
                            chave_acesso = extrair_numero_cupom(dados_ocr) or None
                        except Exception:
                            chave_acesso = None

            # Normalização final: garantir apenas dígitos caso algo tenha sobrado com letras/URL
            if chave_acesso:
                chave_acesso = re.sub(r'\D', '', str(chave_acesso))
                # Se não tiver exatamente 44 dígitos, tenta extrair algum bloco de 44 dígitos
                if len(chave_acesso) != 44:
                    m = re.search(r"\b\d{44}\b", str(chave_acesso))
                    if m:
                        chave_acesso = m.group(0)

            if erro:
                contexto['msg_erro'] = erro
                return render(request, 'painel_cadastrar_cupom.html', contexto)

            if not chave_acesso:
                contexto['msg_erro'] = "Não foi possível ler o código do cupom. Envie uma foto nítida do QR ou digite o código manualmente."
                return render(request, 'painel_cadastrar_cupom.html', contexto)

            # Validação da chave do cupom
            dados_nota = identificar_chave_detalhada(chave_acesso)
            if not dados_nota.valida:
                # Debug seguro no servidor
                try:
                    _norm = str(chave_acesso or '')
                    _mask = _norm[:6] + ('*' * max(0, len(_norm) - 10)) + _norm[-4:] if len(_norm) > 10 else ('*' * len(_norm))
                    print('[DEBUG cupom] chave normalizada:', _mask, 'len=', len(_norm), 'mensagem:', dados_nota.mensagem)
                except Exception:
                    pass
                # Evita duplicar prefixo caso a mensagem já contenha 'Chave inválida'
                msg = dados_nota.mensagem or 'Chave inválida.'
                if not msg.lower().startswith('chave inválida'):
                    msg = f"Chave inválida: {msg}"
                # Acrescenta o total de dígitos lidos
                try:
                    msg = f"{msg} (lido: {len(str(chave_acesso or ''))} dígitos)"
                except Exception:
                    pass
                contexto['msg_erro'] = msg
                return render(request, 'painel_cadastrar_cupom.html', contexto)

            # Status compatível com o modelo
            status_nota = 'Validado'

            # Validação adicional (ex: consulta externa)
            validar = None
            try:
                validar = validar_cupom(dados_nota.chave, dados_nota.tipo_documento)
            except Exception as _e:
                # Mantém validar = None; trataremos abaixo
                validar = None

            # Serializa dados para JSON (string) para armazenar
            dados_cupom_json = json.dumps(asdict(dados_nota))

            # Criação do cupom no banco (ajustando campos ao modelo)
            try:
                novo_cupom = Cupom.objects.create(
                    participante=participante,
                    dados_cupom=dados_cupom_json,
                    tipo_envio='Sistema',
                    status=status_nota,
                    numero_documento=getattr(dados_nota, 'codigo_numerico', ''),
                    cnpj_loja=getattr(dados_nota, 'cnpj_emitente', ''),
                    nome_loja=getattr(dados_nota, 'nome_emitente', 'Desconhecido'),
                    dados_json=validar,
                    tipo_documento=getattr(dados_nota, 'tipo_documento', '')
                )
            except IntegrityError:
                contexto['msg_erro'] = 'cupom já cadastrado'
                return render(request, 'painel_cadastrar_cupom.html', contexto)

            # Cadastro dos produtos vinculados ao cupom (somente se houver dados válidos)
            msg_produto = ''
            msg_numeros = ''
            if validar:
                try:
                    msg_produto = cadastrar_produto(novo_cupom.id, id_participante)
                except Exception as e_prod:
                    msg_produto = f'Erro ao processar produtos do cupom.'

                try:
                    # --- Chamada para gerar números da sorte ---
                    msg_numeros = cadastrar_numeros_da_sorte(novo_cupom)
                except Exception as e_num:
                    msg_numeros = 'Falha ao gerar números da sorte.'
            else:
                msg_produto = 'Dados do cupom indisponíveis; produtos não processados.'

            contexto['msg_sucesso'] = f'Cupom cadastrado com sucesso! {msg_produto}'
            if msg_numeros:
                contexto['msg_numeros'] = msg_numeros

            # Redireciona para a tela de detalhes do cupom recém cadastrado
            detalhes_url = f"{reverse('painel_detalhes_cupom')}?id={novo_cupom.id}"
            return redirect(detalhes_url)

        except Exception as e:
            # Log seguro no servidor e feedback amigável ao usuário
            try:
                print('[ERROR cupom] Falha inesperada no cadastro:', str(e))
            except Exception:
                pass
            contexto['msg_erro'] = 'Não foi possível concluir o cadastro do seu cupom no momento. Tente novamente mais tarde.'

    return render(request, 'painel_cadastrar_cupom.html', contexto)

