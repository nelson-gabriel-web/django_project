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
    contato = get_object_or_404(Contato, pk=pk)
    
    if request.method == 'POST':
        form = ContatoForm(request.POST, instance=contato)
        if form.is_valid():
            form.save()
            return redirect('listar')
    else:
        form = ContatoForm(instance=contato)
    
    return render(request, 'core/editar.html', {'form': form, 'contato': contato})

def excluir_contato(request, pk):
    contato = get_object_or_404(Contato, pk=pk)
    
    if request.method == 'POST':
        contato.delete()
        return redirect('listar')
    
    return render(request, 'core/excluir.html', {'contato': contato})

def sucesso(request):
    return render(request, 'core/sucesso.html')

def listar_contatos(request):
    contatos = Contato.objects.all().order_by('-criado_em')
    return render(request, 'core/listar.html', {'contatos': contatos})