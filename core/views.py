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