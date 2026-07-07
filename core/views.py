from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ContatoForm
from .models import Contato

def login_view(request):
def splash(request):
    return render(request, 'core/splash.html')
def logout_view(request):
    logout(request)
    messages.info(request, 'Sessão terminada com sucesso.')
    return redirect('splash')

def home(request):
    return render(request, 'core/home.html')
# ... resto do código continua igual
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
            return redirect('home')
        else:
            messages.error(request, 'Credenciais inválidas. Tente novamente.')
    
    form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})