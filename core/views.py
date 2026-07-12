from .models import Transacao, HistoricoTransacao, ComprovativoEnvio, ProvaRececao, Disputa, Mediacao
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

from .models import Contato, TentativaLogin, PerfilUsuario, Moeda, PreferenciaMoeda, RequisicaoCompra
from .forms import ContatoForm, PerfilUsuarioForm, RequisicaoCompraForm

# ============================================
# SPLASH E HOME
# ============================================

def splash(request):
    return render(request, 'core/splash.html')

def home(request):
    return render(request, 'core/home.html')

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
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Credenciais inválidas')
    return render(request, 'core/login.html')

def logout_view(request):
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

def dashboard_cliente(request):
    return render(request, 'core/cliente/dashboard_cliente.html')

def dashboard_fornecedor(request):
    return render(request, 'core/fornecedor/dashboard_fornecedor.html')

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
@login_required
def mapa_fornecedores(request):
    """Página com mapa de fornecedores próximos"""
    # Buscar fornecedores com localização
    fornecedores = PerfilUsuario.objects.filter(
        tipo='fornecedor',
        status='ativo',
        latitude__isnull=False,
        longitude__isnull=False
    )
    
    # Pegar localização do cliente
    try:
        cliente = request.user.perfilusuario
        cliente_lat = float(cliente.latitude) if cliente.latitude else None
        cliente_lng = float(cliente.longitude) if cliente.longitude else None
    except:
        cliente_lat = None
        cliente_lng = None
    
    # Preparar dados para o mapa
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
# VIEWS DO SISTEMA DE TRANSAÇÕES
# ============================================

from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from .models import Transacao, HistoricoTransacao, ComprovativoEnvio, ProvaRececao, Disputa, Mediacao

@login_required
def criar_transacao(request, requisicao_id):
    """Criar uma transação a partir de uma requisição"""
    requisicao = get_object_or_404(RequisicaoCompra, id=requisicao_id, cliente=request.user)
    
    if request.method == 'POST':
        fornecedor_id = request.POST.get('fornecedor_id')
        valor = request.POST.get('valor')
        
        fornecedor = get_object_or_404(User, id=fornecedor_id)
        
        transacao = Transacao.objects.create(
            cliente=request.user,
            fornecedor=fornecedor,
            requisicao=requisicao,
            titulo=requisicao.titulo,
            descricao=requisicao.descricao,
            valor_total=Decimal(valor),
            status='pendente'
        )
        
        # Registrar no histórico
        HistoricoTransacao.objects.create(
            transacao=transacao,
            status_anterior='pendente',
            status_novo='pendente',
            usuario=request.user,
            observacao='Transação criada'
        )
        
        messages.success(request, f'✅ Transação #{transacao.id} criada! Aguarde o pagamento.')
        return redirect('detalhe_transacao', transacao_id=transacao.id)
    
    # Buscar fornecedores interessados
    fornecedores = requisicao.fornecedores_interessados.all()
    return render(request, 'core/transacoes/criar_transacao.html', {
        'requisicao': requisicao,
        'fornecedores': fornecedores,
    })

@login_required
def minhas_transacoes(request):
    """Listar todas as transações do utilizador"""
    transacoes_cliente = Transacao.objects.filter(cliente=request.user).order_by('-data_criacao')
    transacoes_fornecedor = Transacao.objects.filter(fornecedor=request.user).order_by('-data_criacao')
    
    return render(request, 'core/transacoes/minhas_transacoes.html', {
        'transacoes_cliente': transacoes_cliente,
        'transacoes_fornecedor': transacoes_fornecedor,
    })

@login_required
def detalhe_transacao(request, transacao_id):
    """Detalhes de uma transação específica"""
    transacao = get_object_or_404(Transacao, id=transacao_id)
    
    # Verificar se o utilizador é parte envolvida
    if request.user != transacao.cliente and request.user != transacao.fornecedor:
        messages.error(request, 'Você não tem permissão para ver esta transação.')
        return redirect('minhas_transacoes')
    
    # Buscar histórico
    historico = transacao.historico.all().order_by('-data')
    
    # Buscar comprovativos
    comprovativos = transacao.comprovativos.all()
    
    # Buscar provas de receção
    provas = transacao.provas_rececao.all()
    
    # Buscar disputas
    disputas = transacao.disputas.all()
    
    return render(request, 'core/transacoes/detalhe_transacao.html', {
        'transacao': transacao,
        'historico': historico,
        'comprovativos': comprovativos,
        'provas': provas,
        'disputas': disputas,
        'is_cliente': request.user == transacao.cliente,
        'is_fornecedor': request.user == transacao.fornecedor,
    })

@login_required
def pagar_transacao(request, transacao_id):
    """Simular pagamento da transação (integração com M-Pesa)"""
    transacao = get_object_or_404(Transacao, id=transacao_id, cliente=request.user)
    
    if transacao.status != 'pendente':
        messages.error(request, 'Esta transação já foi paga ou está em processamento.')
        return redirect('detalhe_transacao', transacao_id=transacao.id)
    
    # Simular pagamento
    transacao.status = 'pago'
    transacao.data_pagamento = timezone.now()
    transacao.save()
    
    # Registrar no histórico
    HistoricoTransacao.objects.create(
        transacao=transacao,
        status_anterior='pendente',
        status_novo='pago',
        usuario=request.user,
        observacao='Pagamento confirmado'
    )
    
    messages.success(request, f'✅ Pagamento de {transacao.valor_total} MT confirmado!')
    return redirect('detalhe_transacao', transacao_id=transacao.id)

@login_required
def confirmar_envio(request, transacao_id):
    """Fornecedor confirma envio do produto"""
    transacao = get_object_or_404(Transacao, id=transacao_id, fornecedor=request.user)
    
    if transacao.status != 'pago':
        messages.error(request, 'A transação ainda não foi paga.')
        return redirect('detalhe_transacao', transacao_id=transacao.id)
    
    if request.method == 'POST':
        codigo_rastreamento = request.POST.get('codigo_rastreamento', '')
        transportadora = request.POST.get('transportadora', '')
        
        transacao.status = 'enviado'
        transacao.data_envio = timezone.now()
        transacao.codigo_rastreamento = codigo_rastreamento
        transacao.transportadora = transportadora
        transacao.save()
        
        # Registrar no histórico
        HistoricoTransacao.objects.create(
            transacao=transacao,
            status_anterior='pago',
            status_novo='enviado',
            usuario=request.user,
            observacao='Produto enviado'
        )
        
        messages.success(request, '✅ Produto enviado! Aguarde a confirmação do cliente.')
        return redirect('detalhe_transacao', transacao_id=transacao.id)
    
    return render(request, 'core/transacoes/confirmar_envio.html', {'transacao': transacao})

@login_required
def confirmar_rececao(request, transacao_id):
    """Cliente confirma receção do produto"""
    transacao = get_object_or_404(Transacao, id=transacao_id, cliente=request.user)
    
    if transacao.status != 'enviado':
        messages.error(request, 'O produto ainda não foi enviado.')
        return redirect('detalhe_transacao', transacao_id=transacao.id)
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo_confirmacao')
        
        if codigo == transacao.codigo_confirmacao:
            transacao.status = 'confirmado'
            transacao.data_confirmacao = timezone.now()
            transacao.save()
            
            # Registrar no histórico
            HistoricoTransacao.objects.create(
                transacao=transacao,
                status_anterior='enviado',
                status_novo='confirmado',
                usuario=request.user,
                observacao='Receção confirmada'
            )
            
            # Libertar pagamento (simulado)
            transacao.status = 'concluido'
            transacao.data_conclusao = timezone.now()
            transacao.save()
            
            HistoricoTransacao.objects.create(
                transacao=transacao,
                status_anterior='confirmado',
                status_novo='concluido',
                usuario=request.user,
                observacao='Pagamento libertado para o fornecedor'
            )
            
            messages.success(request, '✅ Receção confirmada! Pagamento libertado para o fornecedor.')
        else:
            messages.error(request, '❌ Código inválido. Verifique com o fornecedor.')
        
        return redirect('detalhe_transacao', transacao_id=transacao.id)
    
    return render(request, 'core/transacoes/confirmar_rececao.html', {'transacao': transacao})

@login_required
def abrir_disputa(request, transacao_id):
    """Cliente abre disputa"""
    transacao = get_object_or_404(Transacao, id=transacao_id, cliente=request.user)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        evidencia = request.FILES.get('evidencia')
        
        Disputa.objects.create(
            transacao=transacao,
            cliente=request.user,
            fornecedor=transacao.fornecedor,
            motivo=motivo,
            evidencia=evidencia,
            status='aberta'
        )
        
        messages.success(request, '✅ Disputa aberta com sucesso! A equipa Nhonga vai analisar.')
        return redirect('detalhe_transacao', transacao_id=transacao.id)
    
    return render(request, 'core/transacoes/abrir_disputa.html', {'transacao': transacao})

@login_required
def dashboard_transacoes(request):
    """Dashboard de transações para cliente e fornecedor"""
    # Transações do cliente
    cliente_transacoes = Transacao.objects.filter(cliente=request.user)
    
    # Transações do fornecedor
    fornecedor_transacoes = Transacao.objects.filter(fornecedor=request.user)
    
    context = {
        # Cliente
        'cliente_total': cliente_transacoes.count(),
        'cliente_pendentes': cliente_transacoes.filter(status='pendente').count(),
        'cliente_pagos': cliente_transacoes.filter(status='pago').count(),
        'cliente_enviados': cliente_transacoes.filter(status='enviado').count(),
        'cliente_confirmados': cliente_transacoes.filter(status='confirmado').count(),
        'cliente_concluidos': cliente_transacoes.filter(status='concluido').count(),
        'cliente_cancelados': cliente_transacoes.filter(status='cancelado').count(),
        'cliente_ultimas': cliente_transacoes.order_by('-data_criacao')[:5],
        
        # Fornecedor
        'fornecedor_total': fornecedor_transacoes.count(),
        'fornecedor_pendentes': fornecedor_transacoes.filter(status='pendente').count(),
        'fornecedor_pagos': fornecedor_transacoes.filter(status='pago').count(),
        'fornecedor_enviados': fornecedor_transacoes.filter(status='enviado').count(),
        'fornecedor_confirmados': fornecedor_transacoes.filter(status='confirmado').count(),
        'fornecedor_concluidos': fornecedor_transacoes.filter(status='concluido').count(),
        'fornecedor_cancelados': fornecedor_transacoes.filter(status='cancelado').count(),
        'fornecedor_ultimas': fornecedor_transacoes.order_by('-data_criacao')[:5],
    }
    
    return render(request, 'core/transacoes/dashboard_transacoes.html', context)