from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ContatoForm
from .models import Contato

def home(request):
    return render(request, 'core/home.html')

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

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo de volta, {username}!')
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Sessão terminada com sucesso.')
    return redirect('home')

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

@login_required
def excluir_contato(request, pk):
    contato = get_object_or_404(Contato, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        contato.delete()
        return redirect('listar')
    
    return render(request, 'core/excluir.html', {'contato': contato})

@login_required
def sucesso(request):
    return render(request, 'core/sucesso.html')

@login_required
def listar_contatos(request):
    contatos = Contato.objects.filter(usuario=request.user).order_by('-criado_em')
    return render(request, 'core/listar.html', {'contatos': contatos})