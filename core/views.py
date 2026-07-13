from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Contato, TentativaLogin, PerfilUsuario, Moeda, PreferenciaMoeda, RequisicaoCompra, Transacao, HistoricoTransacao
from .forms import ContatoForm, PerfilUsuarioForm, RequisicaoCompraForm
from .constantes import PALAVRAS_PROIBIDAS


# ============================================
# SPLASH E HOME
# ============================================

def splash(request):
    return render(request, 'core/splash.html')

def home(request):
    return render(request, 'core/home.html')

def verificar_produto_ilicito(titulo, descricao):
    """Verifica se um produto contém palavras proibidas"""
    texto = (titulo + ' ' + descricao).lower()
    for palavra in PALAVRAS_PROIBIDAS:
        if palavra.lower() in texto:
            return True, palavra
    return False, None


# ============================================
# AUTENTICAÇÃO
# ============================================

def registar(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            PerfilUsuario.objects.create(usuario=user)
            messages.success(request, 'Conta criada com sucesso! Faça login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'core/registar.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Verificar se a conta está bloqueada
        try:
            user_obj = User.objects.get(username=username)
            tentativa, created = TentativaLogin.objects.get_or_create(usuario=user_obj)
            if tentativa.bloqueado:
                messages.error(request, '🔒 Conta bloqueada por excesso de tentativas. Tente novamente mais tarde.')
                return render(request, 'core/login.html')
        except User.DoesNotExist:
            pass
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Resetar tentativas após login bem-sucedido
            try:
                tentativa, created = TentativaLogin.objects.get_or_create(usuario=user)
                tentativa.tentativas = 0
                tentativa.bloqueado = False
                tentativa.save()
            except:
                pass
            return redirect('home')
        else:
            # Incrementar tentativas
            try:
                user_obj = User.objects.get(username=username)
                tentativa, created = TentativaLogin.objects.get_or_create(usuario=user_obj)
                tentativa.tentativas += 1
                if tentativa.tentativas >= 5:
                    tentativa.bloqueado = True
                    messages.error(request, '🔒 Conta bloqueada por excesso de tentativas.')
                else:
                    messages.error(request, f'Credenciais inválidas. Tentativa {tentativa.tentativas} de 5.')
                tentativa.save()
            except User.DoesNotExist:
                messages.error(request, 'Credenciais inválidas.')
    
    return render(request, 'core/login.html')

def logout_view(request):
    """Faz logout do utilizador e redireciona para o login"""
    logout(request)
    return redirect('login')


# ============================================
# CONTACTOS
# ============================================

@login_required
def adicionar_contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            contato = form.save(commit=False)
            contato.usuario = request.user
            contato.save()
            messages.success(request, 'Contato adicionado com sucesso!')
            return redirect('listar')
    else:
        form = ContatoForm()
    return render(request, 'core/adicionar.html', {'form': form})

@login_required
def listar_contatos(request):
    contatos = Contato.objects.filter(usuario=request.user)
    return render(request, 'core/listar.html', {'contatos': contatos})

@login_required
def buscar_contatos(request):
    query = request.GET.get('q', '')
    if query:
        contatos = Contato.objects.filter(
            Q(nome__icontains=query) | Q(telefone__icontains=query),
            usuario=request.user
        )
    else:
        contatos = Contato.objects.filter(usuario=request.user)
    return render(request, 'core/buscar.html', {'contatos': contatos, 'query': query})

@login_required
def editar_contato(request, pk):
    contato = get_object_or_404(Contato, id=pk, usuario=request.user)
    if request.method == 'POST':
        form = ContatoForm(request.POST, instance=contato)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contato atualizado!')
            return redirect('listar')
    else:
        form = ContatoForm(instance=contato)
    return render(request, 'core/editar.html', {'form': form})

@login_required
def excluir_contato(request, pk):
    contato = get_object_or_404(Contato, id=pk, usuario=request.user)
    if request.method == 'POST':
        contato.delete()
        messages.success(request, 'Contato excluído!')
        return redirect('listar')
    return render(request, 'core/excluir.html', {'contato': contato})


# ============================================
# PERFIL
# ============================================

@login_required
def perfil(request):
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado!')
            return redirect('perfil')
    else:
        form = PerfilUsuarioForm(instance=perfil)
    return render(request, 'core/perfil.html', {'form': form, 'perfil': perfil})


# ============================================
# DASHBOARDS
# ============================================

def dashboard_seguranca(request):
    return render(request, 'core/dashboard_seguranca.html')

@login_required
def dashboard_cliente(request):
    return render(request, 'core/cliente/dashboard_cliente.html')

@login_required
def dashboard_fornecedor(request):
    return render(request, 'core/fornecedor/dashboard_fornecedor.html')

@login_required
def dashboard_transacoes(request):
    """Dashboard de transações simplificado"""
    context = {
        'cliente_total': 0,
        'cliente_pendentes': 0,
        'cliente_pagos': 0,
        'cliente_enviados': 0,
        'cliente_confirmados': 0,
        'cliente_concluidos': 0,
        'cliente_cancelados': 0,
        'cliente_ultimas': [],
        'fornecedor_total': 0,
        'fornecedor_pendentes': 0,
        'fornecedor_pagos': 0,
        'fornecedor_enviados': 0,
        'fornecedor_confirmados': 0,
        'fornecedor_concluidos': 0,
        'fornecedor_cancelados': 0,
        'fornecedor_ultimas': [],
    }
    return render(request, 'core/transacoes/dashboard_transacoes.html', context)

def sucesso(request):
    return render(request, 'core/sucesso.html')

def recuperar_password(request):
    return render(request, 'core/recuperar.html')

def redefinir_password(request, uidb64, token):
    return render(request, 'core/redefinir.html')


# ============================================
# MOEDAS
# ============================================

@login_required
def moedas_list(request):
    moedas = Moeda.objects.filter(ativa=True)
    preferencia = PreferenciaMoeda.objects.filter(usuario=request.user).first()
    return render(request, 'core/moedas_list.html', {
        'moedas': moedas,
        'preferencia': preferencia,
    })

@login_required
def definir_moeda_preferida(request):
    if request.method == 'POST':
        moeda_id = request.POST.get('moeda_id')
        if moeda_id:
            try:
                moeda = Moeda.objects.get(id=moeda_id, ativa=True)
                preferencia, created = PreferenciaMoeda.objects.get_or_create(usuario=request.user)
                preferencia.moeda = moeda
                preferencia.save()
                messages.success(request, f'Moeda definida para {moeda.nome}')
            except Moeda.DoesNotExist:
                messages.error(request, 'Moeda não encontrada')
        else:
            PreferenciaMoeda.objects.filter(usuario=request.user).delete()
            messages.info(request, 'Moeda removida')
        return redirect('moedas_list')
    return redirect('moedas_list')

@login_required
def alternar_moeda(request):
    if request.method == 'POST':
        moeda_id = request.POST.get('moeda')
        if moeda_id:
            try:
                moeda = Moeda.objects.get(id=moeda_id)
                preferencia, created = PreferenciaMoeda.objects.get_or_create(usuario=request.user)
                preferencia.moeda = moeda
                preferencia.save()
                messages.success(request, f'Moeda alterada para {moeda.nome}')
            except Moeda.DoesNotExist:
                messages.error(request, 'Moeda não encontrada')
        else:
            PreferenciaMoeda.objects.filter(usuario=request.user).delete()
            messages.info(request, 'Moeda padrão restaurada')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# ============================================
# PEDIDOS E FORNECEDORES
# ============================================

@login_required
def criar_pedido(request):
    return render(request, 'core/cliente/criar_pedido.html')

@login_required
def meus_pedidos(request):
    return render(request, 'core/cliente/meus_pedidos.html')

@login_required
def registar_fornecedor(request):
    return render(request, 'core/fornecedor/registar_fornecedor.html')

@login_required
def pedidos_proximos(request):
    return render(request, 'core/fornecedor/pedidos_proximos.html')


# ============================================
# REQUISIÇÕES DE COMPRA
# ============================================

@login_required
def criar_requisicao(request):
    if request.method == 'POST':
        form = RequisicaoCompraForm(request.POST)
        if form.is_valid():
            requisicao = form.save(commit=False)
            requisicao.cliente = request.user
            
            try:
                perfil = request.user.perfilusuario
                requisicao.cidade = perfil.cidade or 'Maputo'
                requisicao.provincia = perfil.provincia or 'Maputo'
                requisicao.endereco_entrega = perfil.endereco_completo or perfil.endereco or 'Endereço não informado'
            except:
                requisicao.cidade = 'Maputo'
                requisicao.provincia = 'Maputo'
            
            requisicao.data_limite = timezone.now() + timedelta(days=7)
            requisicao.save()
            
            try:
                requisicao.notificar_fornecedores()
                messages.success(request, f'✅ Requisição "{requisicao.titulo}" criada! Fornecedores notificados.')
            except:
                messages.success(request, f'✅ Requisição "{requisicao.titulo}" criada!')
            
            return redirect('minhas_requisicoes')
    else:
        form = RequisicaoCompraForm()
    
    return render(request, 'core/requisicoes/criar_requisicao.html', {
        'form': form,
        'moedas': Moeda.objects.filter(ativa=True),
    })

@login_required
def minhas_requisicoes(request):
    requisicoes = RequisicaoCompra.objects.filter(cliente=request.user).order_by('-data_criacao')
    return render(request, 'core/requisicoes/minhas_requisicoes.html', {
        'requisicoes': requisicoes,
    })

@login_required
def detalhe_requisicao(request, requisicao_id):
    requisicao = get_object_or_404(RequisicaoCompra, id=requisicao_id, cliente=request.user)
    return render(request, 'core/requisicoes/detalhe_requisicao.html', {
        'requisicao': requisicao,
    })

@login_required
def cancelar_requisicao(request, requisicao_id):
    requisicao = get_object_or_404(RequisicaoCompra, id=requisicao_id, cliente=request.user)
    if requisicao.status in ['pendente', 'em_analise']:
        requisicao.status = 'cancelado'
        requisicao.save()
        messages.success(request, 'Requisição cancelada.')
    else:
        messages.error(request, 'Não é possível cancelar esta requisição.')
    return redirect('minhas_requisicoes')

@login_required
def requisicoes_fornecedor(request):
    try:
        perfil = request.user.perfilusuario
        if perfil.tipo != 'fornecedor':
            messages.warning(request, 'Apenas fornecedores podem ver esta página.')
            return redirect('home')
    except:
        messages.warning(request, 'Complete seu perfil.')
        return redirect('perfil')
    
    requisicoes = RequisicaoCompra.objects.filter(
        status__in=['pendente', 'em_analise']
    ).exclude(cliente=request.user).order_by('-data_criacao')
    
    if perfil.provincia:
        requisicoes = requisicoes.filter(provincia=perfil.provincia)
    
    return render(request, 'core/requisicoes/requisicoes_fornecedor.html', {
        'requisicoes': requisicoes,
        'perfil': perfil,
    })

@login_required
def interessar_requisicao(request, requisicao_id):
    try:
        perfil = request.user.perfilusuario
        if perfil.tipo != 'fornecedor':
            messages.error(request, 'Apenas fornecedores podem se interessar.')
            return redirect('home')
        
        requisicao = get_object_or_404(RequisicaoCompra, id=requisicao_id)
        
        if requisicao.status in ['pendente', 'em_analise']:
            requisicao.fornecedores_interessados.add(request.user)
            requisicao.status = 'em_analise'
            requisicao.save()
            messages.success(request, f'✅ Interesse registrado em "{requisicao.titulo}"')
        else:
            messages.error(request, 'Esta requisição não está disponível.')
    except:
        messages.error(request, 'Complete seu perfil primeiro.')
    
    return redirect('requisicoes_fornecedor')


# ============================================
# SEGURANÇA
# ============================================

@login_required
def alterar_password(request):
    if request.method == 'POST':
        password_atual = request.POST.get('password_atual')
        nova_password = request.POST.get('nova_password')
        confirmar_password = request.POST.get('confirmar_password')
        
        user = request.user
        
        if not user.check_password(password_atual):
            messages.error(request, 'Password atual incorreta.')
            return redirect('dashboard_seguranca')
        
        if nova_password != confirmar_password:
            messages.error(request, 'As novas passwords não coincidem.')
            return redirect('dashboard_seguranca')
        
        if len(nova_password) < 8:
            messages.error(request, 'A password deve ter pelo menos 8 caracteres.')
            return redirect('dashboard_seguranca')
        
        user.set_password(nova_password)
        user.save()
        
        logout(request)
        messages.success(request, 'Password alterada com sucesso! Faça login novamente.')
        return redirect('login')
    
    return redirect('dashboard_seguranca')

@login_required
def toggle_2fa(request):
    if request.method == 'POST':
        perfil = request.user.perfilusuario
        perfil.ativo_2fa = not perfil.ativo_2fa
        perfil.save()
        
        if perfil.ativo_2fa:
            messages.success(request, '2FA ativado com sucesso!')
        else:
            messages.success(request, '2FA desativado com sucesso!')
    
    return redirect('dashboard_seguranca')

@login_required
def logout_all(request):
    if request.method == 'POST':
        from django.contrib.sessions.models import Session
        sessions = Session.objects.filter(session_key=request.session.session_key)
        for session in sessions:
            session.delete()
        messages.success(request, 'Todas as sessões foram terminadas.')
    
    return redirect('dashboard_seguranca')


# ============================================
# MAPA
# ============================================

@login_required
def mapa_fornecedores(request):
    """Página com mapa de fornecedores próximos"""
    fornecedores = PerfilUsuario.objects.filter(
        tipo='fornecedor',
        status='ativo',
        latitude__isnull=False,
        longitude__isnull=False
    )
    
    try:
        cliente = request.user.perfilusuario
        cliente_lat = float(cliente.latitude) if cliente.latitude else None
        cliente_lng = float(cliente.longitude) if cliente.longitude else None
    except:
        cliente_lat = None
        cliente_lng = None
    
    fornecedores_data = []
    for f in fornecedores:
        fornecedores_data.append({
            'nome': f.nome_completo or f.usuario.username,
            'latitude': float(f.latitude),
            'longitude': float(f.longitude),
            'telefone': f.telefone or 'Não disponível',
            'cidade': f.cidade or 'Não informada',
        })
    
    context = {
        'fornecedores': fornecedores_data,
        'cliente_lat': cliente_lat,
        'cliente_lng': cliente_lng,
        'total_fornecedores': len(fornecedores_data),
    }
    return render(request, 'core/mapa_fornecedores.html', context)
# ============================================
# VIEWS M-PESA
# ============================================

from .services.mpesa import MpesaService
from .models import TransacaoMpesa, Transacao
from decimal import Decimal
import json

@login_required
def iniciar_pagamento(request, transacao_id):
    """Inicia um pagamento via M-Pesa"""
    transacao = get_object_or_404(Transacao, id=transacao_id, cliente=request.user)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        
        if not phone_number:
            messages.error(request, 'Número de telefone é obrigatório.')
            return redirect('iniciar_pagamento', transacao_id=transacao.id)
        
        # Validar número (84 ou 85 para M-Pesa)
        if not phone_number.startswith('84') and not phone_number.startswith('85'):
            messages.error(request, 'Número de telefone inválido para M-Pesa. Use 84 ou 85.')
            return redirect('iniciar_pagamento', transacao_id=transacao.id)
        
        # Iniciar pagamento
        mpesa = MpesaService()
        referencia = f"NHONGA-{transacao.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        result = mpesa.stk_push(
            phone_number=phone_number,
            amount=transacao.valor_total,
            reference=referencia,
            description=f"Pagamento Nhonga - {transacao.titulo}"
        )
        
        if result.get('success'):
            # Salvar transação M-Pesa
            transacao_mpesa = TransacaoMpesa.objects.create(
                usuario=request.user,
                transacao=transacao,
                checkout_request_id=result.get('checkout_request_id'),
                merchant_request_id=result.get('merchant_request_id'),
                phone_number=phone_number,
                amount=transacao.valor_total,
                status='pending'
            )
            
            messages.success(request, '✅ Pedido de pagamento enviado! Confirme no seu telemóvel M-Pesa.')
            return redirect('confirmar_pagamento', transacao_id=transacao.id)
        else:
            messages.error(request, f'❌ Erro: {result.get("message")}')
            return redirect('iniciar_pagamento', transacao_id=transacao.id)
    
    return render(request, 'core/pagamento/iniciar_pagamento.html', {
        'transacao': transacao,
    })

@login_required
def confirmar_pagamento(request, transacao_id):
    """Confirmação do pagamento"""
    transacao = get_object_or_404(Transacao, id=transacao_id, cliente=request.user)
    
    # Buscar transação M-Pesa
    try:
        transacao_mpesa = TransacaoMpesa.objects.filter(
            transacao=transacao,
            usuario=request.user
        ).order_by('-data_criacao').first()
    except:
        transacao_mpesa = None
    
    # Se ainda pendente, consultar status
    if transacao_mpesa and transacao_mpesa.status == 'pending':
        mpesa = MpesaService()
        result = mpesa.query_status(transacao_mpesa.checkout_request_id)
        
        if result.get('success'):
            if result.get('status') == 'success':
                transacao_mpesa.mark_success()
                transacao.status = 'pago'
                transacao.data_pagamento = timezone.now()
                transacao.save()
                messages.success(request, '✅ Pagamento confirmado com sucesso!')
            elif result.get('status') == 'failed':
                transacao_mpesa.mark_failed(result.get('result_description', 'Falha no pagamento'))
    
    return render(request, 'core/pagamento/confirmar_pagamento.html', {
        'transacao': transacao,
        'transacao_mpesa': transacao_mpesa,
    })

@csrf_exempt
def callback_mpesa(request):
    """Callback da M-Pesa para confirmação de pagamento"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Extrair dados do callback
            result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
            result_desc = data.get('Body', {}).get('stkCallback', {}).get('ResultDesc')
            checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
            
            # Buscar transação
            try:
                transacao_mpesa = TransacaoMpesa.objects.get(checkout_request_id=checkout_request_id)
                
                if result_code == '0':  # Sucesso
                    transacao_mpesa.mark_success()
                    
                    # Atualizar transação principal
                    if transacao_mpesa.transacao:
                        transacao_mpesa.transacao.status = 'pago'
                        transacao_mpesa.transacao.data_pagamento = timezone.now()
                        transacao_mpesa.transacao.save()
                else:
                    transacao_mpesa.mark_failed(result_desc)
                
                return JsonResponse({'status': 'ok'})
            except TransacaoMpesa.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Transação não encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)

def termos(request):
    """Página de Termos de Serviço"""
    return render(request, 'core/termos.html')