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
        
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                username = username_or_email
        else:
            username = username_or_email
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Credenciais inválidas.')
            return render(request, 'core/login.html', {'form': AuthenticationForm()})
        
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

# ============ LOGOUT ============
def logout_view(request):
    logout(request)
    messages.info(request, 'Sessão terminada com sucesso.')
    return redirect('splash')

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