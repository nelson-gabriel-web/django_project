from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.db.models import Count
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Contato, TentativaLogin, PerfilUsuario
from .forms import ContatoForm, PerfilForm

from .forms import ContatoForm
from .models import Contato, TentativaLogin

# ============ SPLASH ============
def splash(request):
    return render(request, 'core/splash.html')

# ============ HOME ============
def home(request):
    return render(request, 'core/home.html')

# ============ REGISTO ============
def registar(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registo efetuado com sucesso!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/registar.html', {'form': form})

# ============ LOGIN ============
def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        # Verificar se é email ou username
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, 'Credenciais inválidas.')
                return render(request, 'core/login.html', {'form': AuthenticationForm()})
            except User.MultipleObjectsReturned:
                # Se houver múltiplos utilizadores com o mesmo email, pedir username
                messages.error(request, 'Existem múltiplos utilizadores com este email. Por favor, use o seu username.')
                return render(request, 'core/login.html', {'form': AuthenticationForm()})
        else:
            username = username_or_email
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Credenciais inválidas.')
            return render(request, 'core/login.html', {'form': AuthenticationForm()})
        
        # Verificar tentativas de login
        tentativa, created = TentativaLogin.objects.get_or_create(usuario=user)
        
        if tentativa.bloqueado:
            messages.error(request, 'Conta bloqueada por excesso de tentativas.')
            return redirect('splash')
        
        user_authenticated = authenticate(request, username=username, password=password)
        
        if user_authenticated is not None:
            tentativa.tentativas = 0
            tentativa.bloqueado = False
            tentativa.save()
            login(request, user_authenticated)
            messages.success(request, f'Bem-vindo de volta, {username}!')
            return redirect('home')
        else:
            tentativa.tentativas += 1
            if tentativa.tentativas >= 3:
                tentativa.bloqueado = True
                tentativa.save()
                messages.error(request, 'Demasiadas tentativas falhadas. Conta bloqueada.')
                return redirect('splash')
            else:
                tentativa.save()
                tentativas_restantes = 3 - tentativa.tentativas
                messages.error(request, f'Credenciais inválidas. Tentativas restantes: {tentativas_restantes}')
    
    form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

# ============ ADICIONAR CONTACTO ============
@login_required
def adicionar_contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            contato = form.save(commit=False)
            contato.usuario = request.user
            contato.save()
            return redirect('sucesso')
    else:
        form = ContatoForm()
    
    return render(request, 'core/adicionar.html', {'form': form})

# ============ EDITAR CONTACTO ============
@login_required
def editar_contato(request, pk):
    contato = get_object_or_404(Contato, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = ContatoForm(request.POST, instance=contato)
        if form.is_valid():
            form.save()
            return redirect('listar')
    else:
        form = ContatoForm(instance=contato)
    
    return render(request, 'core/editar.html', {'form': form, 'contato': contato})

# ============ EXCLUIR CONTACTO ============
@login_required
def excluir_contato(request, pk):
    contato = get_object_or_404(Contato, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        contato.delete()
        return redirect('listar')
    
    return render(request, 'core/excluir.html', {'contato': contato})

# ============ SUCESSO ============
@login_required
def sucesso(request):
    return render(request, 'core/sucesso.html')

# ============ LISTAR CONTACTOS ============
@login_required
def listar_contatos(request):
    contatos = Contato.objects.filter(usuario=request.user).order_by('-criado_em')
    return render(request, 'core/listar.html', {'contatos': contatos})

# ============ BUSCAR CONTACTOS ============
@login_required
def buscar_contatos(request):
    query = request.GET.get('q', '')
    if query:
        contatos = Contato.objects.filter(
            usuario=request.user
        ).filter(
            models.Q(nome__icontains=query) | 
            models.Q(telefone__icontains=query)
        ).order_by('-criado_em')
    else:
        contatos = Contato.objects.filter(usuario=request.user).order_by('-criado_em')
    
    return render(request, 'core/buscar.html', {
        'contatos': contatos,
        'query': query
    })

# ============ RECUPERAR PASSWORD ============
def recuperar_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            current_site = get_current_site(request)
            protocol = 'https' if request.is_secure() else 'http'
            link = f"{protocol}://{current_site.domain}/redefinir/{uid}/{token}/"
            
            assunto = 'Recuperação de Password - LabSec'
            mensagem = f"""
            Olá {user.username},
            
            Recebemos um pedido para redefinir a sua password.
            
            Clique no link abaixo para redefinir a sua password:
            {link}
            
            Se não foi você, ignore este email.
            
            Atenciosamente,
            Equipa LabSec
            """
            send_mail(assunto, mensagem, 'noreply@labsec.com', [email])
            
            messages.success(request, 'Enviamos um email com instruções para redefinir a sua password.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Não existe nenhum utilizador com este email.')
    
    return render(request, 'core/recuperar.html')

# ============ REDEFINIR PASSWORD ============
def redefinir_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            nova_password = request.POST.get('nova_password')
            confirmar_password = request.POST.get('confirmar_password')
            
            if nova_password == confirmar_password and len(nova_password) >= 8:
                user.set_password(nova_password)
                user.save()
                messages.success(request, 'Password alterada com sucesso! Faça login com a nova password.')
                return redirect('login')
            else:
                messages.error(request, 'As passwords não coincidem ou têm menos de 8 caracteres.')
        
        return render(request, 'core/redefinir.html', {'user': user})
    else:
        messages.error(request, 'Link inválido ou expirado. Solicite uma nova recuperação.')
        return redirect('recuperar')

# ============ DASHBOARD SEGURANÇA ============
@login_required
def dashboard_seguranca(request):
    context = {
        'eventos': [],
        'cameras': [],
        'sensores': [],
        'alertas': [],
        'total_eventos': 0,
        'alertas_nao_lidos': 0,
    }
    return render(request, 'core/dashboard_seguranca.html', context)

# ============ LISTA DE COMUNIDADES ============
@login_required
def comunidades_list(request):
    return render(request, 'core/comunidades_list.html', {'comunidades': []})

# ============ ADICIONAR COMUNIDADE ============
@login_required
def adicionar_comunidade(request):
    if request.method == 'POST':
        messages.success(request, 'Comunidade adicionada com sucesso!')
        return redirect('comunidades_list')
    return render(request, 'core/adicionar_comunidade.html')

# ============ DETALHE COMUNIDADE ============
@login_required
def comunidade_detalhe(request, pk):
    return render(request, 'core/comunidade_detalhe.html', {'comunidade': {'nome': 'Comunidade Teste'}})

# ============ ADICIONAR CRIME ============
@login_required
def adicionar_crime(request, comunidade_pk):
    if request.method == 'POST':
        messages.success(request, 'Crime registado com sucesso!')
        return redirect('comunidade_detalhe', pk=comunidade_pk)
    return render(request, 'core/adicionar_crime.html')

# ============ ADICIONAR ESTRATÉGIA ============
@login_required
def adicionar_estrategia(request, comunidade_pk):
    if request.method == 'POST':
        messages.success(request, 'Estratégia adicionada com sucesso!')
        return redirect('comunidade_detalhe', pk=comunidade_pk)
    return render(request, 'core/adicionar_estrategia.html')

# ============ AVALIAR SEGURANÇA ============
@login_required
def avaliar_seguranca(request, comunidade_pk):
    if request.method == 'POST':
        messages.success(request, 'Avaliação registada com sucesso!')
        return redirect('comunidade_detalhe', pk=comunidade_pk)
    return render(request, 'core/avaliar_seguranca.html')

# ============ RELATÓRIO COMUNIDADE ============
@login_required
def relatorio_comunidade(request, pk):
    return render(request, 'core/relatorio_comunidade.html')

# ============ API EVENTO ============
@csrf_exempt
def api_evento(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)

# ============ LOGOUT ============
def logout_view(request):
    logout(request)
    return redirect('splash')

# ============ PERFIL DO UTILIZADOR ============
@login_required
def perfil(request):
    # Garantir que o perfil existe
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
        else:
            messages.error(request, 'Erro ao atualizar perfil. Verifique os dados.')
    else:
        form = PerfilForm(instance=perfil)
    
    return render(request, 'core/perfil.html', {
        'form': form,
        'perfil': perfil,
        'user': request.user
    })
# ============================================
# VIEWS PARA PLATAFORMA DE INTERMEDIAÇÃO NHONGA
# ============================================

from django.db.models import Q
from decimal import Decimal
import random
import string
from django.utils import timezone
from .models import Pedido, Fornecedor, Produto, Transacao, Avaliacao, Categoria, Notificacao
from .forms import PedidoForm, ProdutoForm, FornecedorForm

# ========== CLIENTE ==========

@login_required
def dashboard_cliente(request):
    """Dashboard do cliente"""
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-criado_em')[:10]
    transacoes = Transacao.objects.filter(cliente=request.user).order_by('-data_criacao')[:5]
    notificacoes = Notificacao.objects.filter(usuario=request.user, lida=False).order_by('-criado_em')
    
    context = {
        'pedidos': pedidos,
        'transacoes': transacoes,
        'notificacoes': notificacoes,
        'total_pedidos': Pedido.objects.filter(cliente=request.user).count(),
        'total_transacoes': Transacao.objects.filter(cliente=request.user).count(),
    }
    return render(request, 'core/cliente/dashboard_cliente.html', context)

@login_required
def criar_pedido(request):
    """Criar um novo pedido"""
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.cliente = request.user
            pedido.coordenadas = {'lat': -25.969, 'lng': 32.573}
            pedido.save()
            messages.success(request, 'Pedido criado com sucesso! A procurar fornecedores...')
            return redirect('meus_pedidos')
    else:
        form = PedidoForm()
    
    return render(request, 'core/cliente/criar_pedido.html', {'form': form})

@login_required
def meus_pedidos(request):
    """Lista de pedidos do cliente"""
    pedidos = Pedido.objects.filter(cliente=request.user).order_by('-criado_em')
    return render(request, 'core/cliente/meus_pedidos.html', {'pedidos': pedidos})

@login_required
def fornecedores_proximos(request, pedido_id):
    """Encontra fornecedores próximos para um pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    
    fornecedores = Fornecedor.objects.filter(
        categorias=pedido.categoria,
        disponivel=True,
        cidade__icontains=pedido.localizacao.split(',')[0] if pedido.localizacao else ''
    )[:10]
    
    if request.method == 'POST':
        fornecedor_id = request.POST.get('fornecedor_id')
        fornecedor = get_object_or_404(Fornecedor, id=fornecedor_id)
        
        pedido.fornecedor_escolhido = fornecedor
        pedido.status = 'em_negociacao'
        pedido.save()
        
        messages.success(request, f'Fornecedor {fornecedor.nome_empresa} selecionado!')
        return redirect('confirmar_compra', pedido_id=pedido.id)
    
    context = {
        'pedido': pedido,
        'fornecedores': fornecedores,
    }
    return render(request, 'core/cliente/fornecedores_proximos.html', context)

@login_required
def confirmar_compra(request, pedido_id):
    """Confirmar compra e realizar pagamento"""
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=request.user)
    fornecedor = pedido.fornecedor_escolhido
    
    if not fornecedor:
        messages.error(request, 'Nenhum fornecedor selecionado.')
        return redirect('meus_pedidos')
    
    valor = pedido.orcamento or Decimal('100.00')
    comissao = valor * Decimal('0.02')
    valor_fornecedor = valor - comissao
    
    if request.method == 'POST':
        codigo = ''.join(random.choices(string.digits, k=6))
        
        transacao = Transacao.objects.create(
            pedido=pedido,
            fornecedor=fornecedor,
            cliente=request.user,
            valor=valor,
            comissao=comissao,
            valor_fornecedor=valor_fornecedor,
            status='pago',
            codigo_confirmacao=codigo
        )
        
        pedido.status = 'pago'
        pedido.save()
        
        Notificacao.objects.create(
            usuario=fornecedor.usuario,
            mensagem=f'Novo pedido pago: {pedido.titulo}. Código: {codigo}',
            link='/fornecedor/transacoes/'
        )
        
        messages.success(request, f'Pagamento realizado com sucesso! Código: {codigo}')
        return redirect('meus_pedidos')
    
    context = {
        'pedido': pedido,
        'fornecedor': fornecedor,
        'valor': valor,
        'comissao': comissao,
        'valor_fornecedor': valor_fornecedor,
    }
    return render(request, 'core/cliente/confirmar_compra.html', context)

@login_required
def confirmar_rececao(request, transacao_id):
    """Confirmar receção do produto/serviço"""
    transacao = get_object_or_404(Transacao, id=transacao_id, cliente=request.user)
    
    if request.method == 'POST':
        transacao.status = 'confirmado'
        transacao.data_confirmacao = timezone.now()
        transacao.save()
        
        pedido = transacao.pedido
        pedido.status = 'concluido'
        pedido.save()
        
        Notificacao.objects.create(
            usuario=transacao.fornecedor.usuario,
            mensagem=f'Receção confirmada para o pedido {pedido.titulo}! Pagamento libertado.',
            link='/fornecedor/transacoes/'
        )
        
        messages.success(request, 'Receção confirmada! Pagamento libertado ao fornecedor.')
        return redirect('meus_pedidos')
    
    context = {
        'transacao': transacao,
        'pedido': transacao.pedido,
    }
    return render(request, 'core/cliente/confirmar_rececao.html', context)

# ========== FORNECEDOR ==========

@login_required
def dashboard_fornecedor(request):
    """Dashboard do fornecedor"""
    if not hasattr(request.user, 'fornecedor'):
        messages.warning(request, 'Registe-se como fornecedor primeiro.')
        return redirect('registar_fornecedor')
    
    fornecedor = request.user.fornecedor
    pedidos = Pedido.objects.filter(fornecedor_escolhido=fornecedor).order_by('-criado_em')[:10]
    transacoes = Transacao.objects.filter(fornecedor=fornecedor).order_by('-data_criacao')[:5]
    produtos = Produto.objects.filter(fornecedor=fornecedor)
    
    context = {
        'fornecedor': fornecedor,
        'pedidos': pedidos,
        'transacoes': transacoes,
        'produtos': produtos,
        'total_produtos': produtos.count(),
        'total_transacoes': Transacao.objects.filter(fornecedor=fornecedor).count(),
    }
    return render(request, 'core/fornecedor/dashboard_fornecedor.html', context)

@login_required
def registar_fornecedor(request):
    """Registar como fornecedor"""
    if hasattr(request.user, 'fornecedor'):
        messages.info(request, 'Já está registado como fornecedor.')
        return redirect('dashboard_fornecedor')
    
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            fornecedor = form.save(commit=False)
            fornecedor.usuario = request.user
            fornecedor.coordenadas = {'lat': -25.969, 'lng': 32.573}
            fornecedor.save()
            form.save_m2m()
            
            messages.success(request, 'Registo como fornecedor concluído!')
            return redirect('dashboard_fornecedor')
    else:
        form = FornecedorForm()
    
    return render(request, 'core/fornecedor/registar_fornecedor.html', {'form': form})

@login_required
def pedidos_proximos(request):
    """Ver pedidos próximos na região"""
    if not hasattr(request.user, 'fornecedor'):
        messages.warning(request, 'Registe-se como fornecedor primeiro.')
        return redirect('registar_fornecedor')
    
    fornecedor = request.user.fornecedor
    categorias = fornecedor.categorias.all()
    
    pedidos = Pedido.objects.filter(
        categoria__in=categorias,
        status='aberto'
    ).exclude(cliente=request.user).order_by('-criado_em')[:20]
    
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        pedido.fornecedor_escolhido = fornecedor
        pedido.status = 'em_negociacao'
        pedido.save()
        
        Notificacao.objects.create(
            usuario=pedido.cliente,
            mensagem=f'O fornecedor {fornecedor.nome_empresa} aceitou o seu pedido!',
            link='/cliente/pedidos/'
        )
        
        messages.success(request, 'Pedido aceite! Aguarde a confirmação do cliente.')
        return redirect('dashboard_fornecedor')
    
    context = {
        'pedidos': pedidos,
        'fornecedor': fornecedor,
    }
    return render(request, 'core/fornecedor/pedidos_proximos.html', context)

@login_required
def registar_produto(request):
    """Registar um produto ou serviço"""
    if not hasattr(request.user, 'fornecedor'):
        messages.warning(request, 'Registe-se como fornecedor primeiro.')
        return redirect('registar_fornecedor')
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.fornecedor = request.user.fornecedor
            produto.save()
            messages.success(request, 'Produto registado com sucesso!')
            return redirect('dashboard_fornecedor')
    else:
        form = ProdutoForm()
    
    return render(request, 'core/fornecedor/registar_produto.html', {'form': form})

@login_required
def transacoes_fornecedor(request):
    """Lista de transações do fornecedor"""
    if not hasattr(request.user, 'fornecedor'):
        return redirect('registar_fornecedor')
    
    transacoes = Transacao.objects.filter(fornecedor=request.user.fornecedor).order_by('-data_criacao')
    return render(request, 'core/fornecedor/transacoes_fornecedor.html', {'transacoes': transacoes})

# ========== FUNÇÃO PARA CRIAR CATEGORIAS ==========

def criar_categorias_iniciais():
    """Cria categorias iniciais se não existirem"""
    categorias = [
        ('eletricista', '⚡'),
        ('canalizador', '🔧'),
        ('mecanico', '🔩'),
        ('construcao', '🏗️'),
        ('informatica', '💻'),
        ('limpeza', '🧹'),
        ('jardinagem', '🌿'),
        ('entrega', '📦'),
        ('pintura', '🎨'),
        ('vidraceiro', '🪟'),
        ('serralheiro', '🔒'),
        ('lojas', '🏪'),      # NOVO
        ('outro', '📌'),
    ]
    for nome, icone in categorias:
        Categoria.objects.get_or_create(nome=nome, defaults={'icone': icone})