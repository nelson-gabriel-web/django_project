from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import ContatoForm
from .models import Contato

# Splash Screen
def splash(request):
    return render(request, 'core/splash.html')

# Home
def home(request):
    return render(request, 'core/home.html')

# Registo de utilizador
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

# Login
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
                username = username_or_email
        else:
            username = username_or_email
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo de volta, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Credenciais inválidas. Tente novamente.')
    
    form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

# Logout
def logout_view(request):
    logout(request)
    messages.info(request, 'Sessão terminada com sucesso.')
    return redirect('splash')

# Adicionar contacto
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

# Editar contacto
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

# Excluir contacto
@login_required
def excluir_contato(request, pk):
    contato = get_object_or_404(Contato, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        contato.delete()
        return redirect('listar')
    
    return render(request, 'core/excluir.html', {'contato': contato})

# Sucesso
@login_required
def sucesso(request):
    return render(request, 'core/sucesso.html')

# Listar contactos
@login_required
def listar_contatos(request):
    contatos = Contato.objects.filter(usuario=request.user).order_by('-criado_em')
    return render(request, 'core/listar.html', {'contatos': contatos})