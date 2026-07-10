from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm  # <-- ESTA É IMPORTANTE
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Contato, TentativaLogin, PerfilUsuario, Moeda, PreferenciaMoeda, RequisicaoCompra
from .forms import ContatoForm, PerfilUsuarioForm, RequisicaoCompraForm


# ============================================
# VIEWS EXISTENTES
# ============================================
def splash(request):
    """Página inicial de carregamento (splash)"""
    return render(request, 'core/splash.html')

def home(request):
    return render(request, 'core/home.html')

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

def listar_contatos(request):
    contatos = Contato.objects.filter(usuario=request.user)
    return render(request, 'core/listar.html', {'contatos': contatos})

def buscar_contatos(request):
    query = request.GET.get('q', '')
    if query:
        contatos = Contato.objects.filter(
            models.Q(nome__icontains=query) | models.Q(telefone__icontains=query),
            usuario=request.user
        )
    else:
        contatos = Contato.objects.filter(usuario=request.user)
    return render(request, 'core/buscar.html', {'contatos': contatos, 'query': query})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Credenciais inválidas')
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def perfil(request):
    """Página de perfil do usuário"""
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
    else:
        form = PerfilUsuarioForm(instance=perfil)
    
    return render(request, 'core/perfil.html', {
        'form': form,
        'perfil': perfil,
    })

def dashboard_seguranca(request):
    return render(request, 'core/dashboard_seguranca.html')

def comunidades_list(request):
    return render(request, 'core/comunidades_list.html')

def dashboard_cliente(request):
    return render(request, 'core/dashboard_cliente.html')

def dashboard_fornecedor(request):
    return render(request, 'core/dashboard_fornecedor.html')


# ============================================
# VIEWS PARA ALTERNAR MOEDA
# ============================================

@login_required
def alternar_moeda(request):
    """Alterna a moeda preferida do usuário"""
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
# NOVAS VIEWS - REQUISIÇÕES DE COMPRA
# ============================================

@login_required
def criar_requisicao(request):
    """Criar uma nova requisição de compra"""
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
                messages.success(request, f'✅ Requisição "{requisicao.titulo}" criada! Fornecedores próximos foram notificados.')
            except:
                messages.success(request, f'✅ Requisição "{requisicao.titulo}" criada com sucesso!')
            
            return redirect('minhas_requisicoes')
    else:
        form = RequisicaoCompraForm()
    
    return render(request, 'core/requisicoes/criar_requisicao.html', {
        'form': form,
        'moedas': Moeda.objects.filter(ativa=True),
    })

@login_required
def minhas_requisicoes(request):
    """Listar todas as requisições do cliente"""
    requisicoes = RequisicaoCompra.objects.filter(cliente=request.user).order_by('-data_criacao')
    return render(request, 'core/requisicoes/minhas_requisicoes.html', {
        'requisicoes': requisicoes,
    })

@login_required
def detalhe_requisicao(request, requisicao_id):
    """Detalhes de uma requisição"""
    requisicao = get_object_or_404(RequisicaoCompra, id=requisicao_id, cliente=request.user)
    return render(request, 'core/requisicoes/detalhe_requisicao.html', {
        'requisicao': requisicao,
    })

@login_required
def cancelar_requisicao(request, requisicao_id):
    """Cancelar uma requisição"""
    requisicao = get_object_or_404(RequisicaoCompra, id=requisicao_id, cliente=request.user)
    
    if requisicao.status in ['pendente', 'em_analise']:
        requisicao.status = 'cancelado'
        requisicao.save()
        messages.success(request, 'Requisição cancelada com sucesso.')
    else:
        messages.error(request, 'Não é possível cancelar esta requisição.')
    
    return redirect('minhas_requisicoes')

@login_required
def requisicoes_fornecedor(request):
    """Lista requisições para fornecedores"""
    try:
        perfil = request.user.perfilusuario
        if perfil.tipo != 'fornecedor':
            messages.warning(request, 'Você precisa ser um fornecedor para ver esta página.')
            return redirect('home')
    except:
        messages.warning(request, 'Complete seu perfil para ser um fornecedor.')
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
    """Fornecedor se interessa por uma requisição"""
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
            messages.error(request, 'Esta requisição não está mais disponível.')
    except:
        messages.error(request, 'Complete seu perfil primeiro.')
    
    return redirect('requisicoes_fornecedor')
def registar(request):
    """Página de registo de utilizador"""
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
# ============================================
# VIEWS FALTANTES
# ============================================

@login_required
def editar_contato(request, pk):
    """Editar um contato existente"""
    contato = get_object_or_404(Contato, id=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = ContatoForm(request.POST, instance=contato)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contato atualizado com sucesso!')
            return redirect('listar')
    else:
        form = ContatoForm(instance=contato)
    
    return render(request, 'core/editar.html', {'form': form, 'contato': contato})

@login_required
def excluir_contato(request, pk):
    """Excluir um contato"""
    contato = get_object_or_404(Contato, id=pk, usuario=request.user)
    
    if request.method == 'POST':
        contato.delete()
        messages.success(request, 'Contato excluído com sucesso!')
        return redirect('listar')
    
    return render(request, 'core/excluir.html', {'contato': contato})

def dashboard(request):
    """Página de dashboard"""
    return render(request, 'core/dashboard.html')

def configuracoes(request):
    """Página de configurações"""
    return render(request, 'core/configuracoes.html')

def sobre(request):
    """Página sobre"""
    return render(request, 'core/sobre.html')
# ============================================
# VIEWS FALTANTES - ADICIONAR TODAS
# ============================================

def sucesso(request):
    """Página de sucesso após adicionar contato"""
    return render(request, 'core/sucesso.html')

@login_required
def recuperar_password(request):
    """Página de recuperação de password"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Aqui você pode enviar email com link de redefinição
            messages.success(request, 'Email de recuperação enviado!')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Email não encontrado.')
    return render(request, 'core/recuperar.html')

@login_required
def redefinir_password(request, uidb64, token):
    """Redefinir password com token"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password alterado com sucesso!')
                return redirect('login')
            else:
                messages.error(request, 'As passwords não coincidem.')
        return render(request, 'core/redefinir.html', {'uidb64': uidb64, 'token': token})
    else:
        messages.error(request, 'Link inválido ou expirado.')
        return redirect('recuperar')

@login_required
def moedas_list(request):
    """Lista de moedas disponíveis"""
    moedas = Moeda.objects.filter(ativa=True)
    preferencia = PreferenciaMoeda.objects.filter(usuario=request.user).first()
    return render(request, 'core/moedas_list.html', {
        'moedas': moedas,
        'preferencia': preferencia,
    })

@login_required
def definir_moeda_preferida(request):
    """Define a moeda preferida do usuário"""
    if request.method == 'POST':
        moeda_id = request.POST.get('moeda_id')
        if moeda_id:
            try:
                moeda = Moeda.objects.get(id=moeda_id, ativa=True)
                preferencia, created = PreferenciaMoeda.objects.get_or_create(usuario=request.user)
                preferencia.moeda = moeda
                preferencia.save()
                messages.success(request, f'Moeda preferida definida para {moeda.nome}')
            except Moeda.DoesNotExist:
                messages.error(request, 'Moeda não encontrada')
        else:
            PreferenciaMoeda.objects.filter(usuario=request.user).delete()
            messages.info(request, 'Moeda preferida removida')
        return redirect('moedas_list')
    return redirect('moedas_list')

@login_required
def criar_pedido(request):
    """Criar um novo pedido (cliente)"""
    # Esta é uma view simplificada para manter compatibilidade
    # Você pode expandir conforme necessário
    return render(request, 'core/cliente/criar_pedido.html')

@login_required
def meus_pedidos(request):
    """Listar pedidos do cliente"""
    # View simplificada
    return render(request, 'core/cliente/meus_pedidos.html')

@login_required
def registar_fornecedor(request):
    """Registar um novo fornecedor"""
    if request.method == 'POST':
        # Lógica para registar fornecedor
        messages.success(request, 'Fornecedor registado com sucesso!')
        return redirect('dashboard_fornecedor')
    return render(request, 'core/fornecedor/registar_fornecedor.html')

@login_required
def pedidos_proximos(request):
    """Lista pedidos próximos para fornecedores"""
    # View simplificada
    return render(request, 'core/fornecedor/pedidos_proximos.html')