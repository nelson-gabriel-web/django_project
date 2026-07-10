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

@login_required
def dashboard_cliente(request):
    requisicoes = RequisicaoCompra.objects.filter(cliente=request.user)
    context = {
        'total_requisicoes': requisicoes.count(),
        'requisicoes_pendentes': requisicoes.filter(status='pendente').count(),
        'requisicoes_em_analise': requisicoes.filter(status='em_analise').count(),
        'requisicoes_concluidas': requisicoes.filter(status='concluido').count(),
        'requisicoes_canceladas': requisicoes.filter(status='cancelado').count(),
        'ultimas_requisicoes': requisicoes.order_by('-data_criacao')[:5],
        'fornecedores_interessados': User.objects.filter(
            perfilusuario__tipo='fornecedor',
            requisicoes_interessadas__in=requisicoes
        ).distinct().count(),
    }
    return render(request, 'core/cliente/dashboard_cliente.html', context)

@login_required
def dashboard_fornecedor(request):
    try:
        perfil = request.user.perfilusuario
        if perfil.tipo != 'fornecedor':
            messages.warning(request, 'Apenas fornecedores podem ver este dashboard.')
            return redirect('home')
    except:
        messages.warning(request, 'Complete seu perfil.')
        return redirect('perfil')
    
    requisicoes_disponiveis = RequisicaoCompra.objects.filter(
        status__in=['pendente', 'em_analise']
    ).exclude(cliente=request.user)
    
    if perfil.provincia:
        requisicoes_disponiveis = requisicoes_disponiveis.filter(provincia=perfil.provincia)
    
    requisicoes_interessadas = RequisicaoCompra.objects.filter(
        fornecedores_interessados=request.user
    )
    
    context = {
        'total_disponiveis': requisicoes_disponiveis.count(),
        'total_interessadas': requisicoes_interessadas.count(),
        'requisicoes_em_negociacao': requisicoes_interessadas.filter(status='em_negociacao').count(),
        'requisicoes_concluidas': requisicoes_interessadas.filter(status='concluido').count(),
        'ultimas_disponiveis': requisicoes_disponiveis.order_by('-data_criacao')[:5],
        'ultimas_interessadas': requisicoes_interessadas.order_by('-data_criacao')[:5],
    }
    return render(request, 'core/fornecedor/dashboard_fornecedor.html', context)


# ============================================
# MOEDAS
# ============================================

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
# OUTRAS VIEWS
# ============================================

def sucesso(request):
    return render(request, 'core/sucesso.html')

def recuperar_password(request):
    return render(request, 'core/recuperar.html')

def redefinir_password(request, uidb64, token):
    return render(request, 'core/redefinir.html')

def comunidades_list(request):
    return render(request, 'core/comunidades_list.html')

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