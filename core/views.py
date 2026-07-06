from django.shortcuts import render, redirect
from .forms import ContatoForm
from .models import Contato

def home(request):
    return render(request, 'core/home.html')

def adicionar_contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sucesso')
    else:
        form = ContatoForm()
    
    return render(request, 'core/adicionar.html', {'form': form})

def sucesso(request):
    return render(request, 'core/sucesso.html')

def listar_contatos(request):
    contatos = Contato.objects.all().order_by('-criado_em')
    return render(request, 'core/listar.html', {'contatos': contatos})

from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContatoForm
from .models import Contato

def home(request):
    return render(request, 'core/home.html')

def adicionar_contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sucesso')
    else:
        form = ContatoForm()
    
    return render(request, 'core/adicionar.html', {'form': form})

def editar_contato(request, pk):
    contato = get_object_or_404(Contato, pk=pk)  # Busca o contato pelo ID
    
    if request.method == 'POST':
        form = ContatoForm(request.POST, instance=contato)  # Atualiza o contato existente
        if form.is_valid():
            form.save()
            return redirect('listar')  # Volta para a lista
    else:
        form = ContatoForm(instance=contato)  # Carrega os dados atuais
    
    return render(request, 'core/editar.html', {'form': form, 'contato': contato})

def sucesso(request):
    return render(request, 'core/sucesso.html')

def listar_contatos(request):
    contatos = Contato.objects.all().order_by('-criado_em')
    return render(request, 'core/listar.html', {'contatos': contatos})