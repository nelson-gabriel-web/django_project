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
from .forms import ContatoForm
from .models import Contato, TentativaLogin
from .models import Contato, TentativaLogin, Camera, SensorMovimento, EventoSeguranca, ZonaRisco, Alerta

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
        
        # Identificar o utilizador
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                username = username_or_email
        else:
            username = username_or_email
        
        # Verificar se o utilizador existe
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Credenciais inválidas.')
            return render(request, 'core/login.html', {'form': AuthenticationForm()})
        
        # Verificar tentativas de login
        tentativa, created = TentativaLogin.objects.get_or_create(usuario=user)
        
        # Se estiver bloqueado, redirecionar para splash
        if tentativa.bloqueado:
            messages.error(request, 'Conta bloqueada por excesso de tentativas. Volte a tentar mais tarde.')
            return redirect('splash')
        
        # Autenticar
        user_authenticated = authenticate(request, username=username, password=password)
        
        if user_authenticated is not None:
            # Login bem-sucedido - resetar tentativas
            tentativa.tentativas = 0
            tentativa.bloqueado = False
            tentativa.save()
            login(request, user_authenticated)
            messages.success(request, f'Bem-vindo de volta, {username}!')
            return redirect('home')
        else:
            # Tentativa falhada
            tentativa.tentativas += 1
            
            # Se atingir 3 tentativas, bloquear
            if tentativa.tentativas >= 3:
                tentativa.bloqueado = True
                tentativa.save()
                messages.error(request, 'Demasiadas tentativas falhadas. A sua conta foi bloqueada temporariamente.')
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

# ============================================
# VIEWS PARA SISTEMA DE SEGURANÇA
# ============================================

@login_required
def dashboard_seguranca(request):
    """Dashboard principal de segurança"""
    eventos = EventoSeguranca.objects.filter(
        camera__usuario=request.user
    ).order_by('-criado_em')[:20]
    
    cameras = Camera.objects.filter(usuario=request.user, ativa=True)
    sensores = SensorMovimento.objects.filter(usuario=request.user, ativo=True)
    alertas = Alerta.objects.filter(evento__camera__usuario=request.user, lido=False)
    
    context = {
        'eventos': eventos,
        'cameras': cameras,
        'sensores': sensores,
        'alertas': alertas,
        'total_eventos': EventoSeguranca.objects.filter(camera__usuario=request.user).count(),
        'alertas_nao_lidos': alertas.count(),
    }
    return render(request, 'core/dashboard_seguranca.html', context)

@login_required
def cameras_list(request):
    """Lista de câmeras"""
    cameras = Camera.objects.filter(usuario=request.user)
    return render(request, 'core/cameras_list.html', {'cameras': cameras})

@login_required
def adicionar_camera(request):
    """Adicionar uma nova câmera"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        localizacao = request.POST.get('localizacao')
        url_rtsp = request.POST.get('url_rtsp')
        
        camera = Camera.objects.create(
            nome=nome,
            localizacao=localizacao,
            url_rtsp=url_rtsp,
            usuario=request.user
        )
        messages.success(request, 'Câmera adicionada com sucesso!')
        return redirect('cameras_list')
    
    return render(request, 'core/adicionar_camera.html')

@login_required
def eventos_seguranca(request):
    """Lista de eventos de segurança"""
    eventos = EventoSeguranca.objects.filter(
        camera__usuario=request.user
    ).order_by('-criado_em')
    return render(request, 'core/eventos_seguranca.html', {'eventos': eventos})

@login_required
def mapa_risco(request):
    """Mapa de zonas de risco"""
    zonas = ZonaRisco.objects.all().order_by('-nivel_risco')
    return render(request, 'core/mapa_risco.html', {'zonas': zonas})

# ============================================
# API PARA DISPOSITIVOS (ESP8266/Arduino)
# ============================================

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def api_evento(request):
    """API para receber eventos dos sensores"""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            tipo = dados.get('tipo')
            sensor_id = dados.get('sensor_id')
            descricao = dados.get('descricao', '')
            
            evento = EventoSeguranca.objects.create(
                tipo=tipo,
                sensor_id=sensor_id,
                descricao=descricao,
                processado=False
            )
            
            # Processar com IA (simples)
            processar_evento_ia(evento)
            
            return JsonResponse({'status': 'ok', 'evento_id': evento.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'mensagem': str(e)}, status=400)
    
    return JsonResponse({'status': 'error'}, status=405)

# ============================================
# VIEWS PARA ANÁLISE COMUNITÁRIA DE SEGURANÇA
# ============================================

@login_required
def comunidades_list(request):
    """Lista de comunidades"""
    comunidades = Comunidade.objects.filter(usuario=request.user)
    return render(request, 'core/comunidades_list.html', {'comunidades': comunidades})

@login_required
def adicionar_comunidade(request):
    """Adicionar uma nova comunidade"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        localizacao = request.POST.get('localizacao')
        populacao = request.POST.get('populacao')
        residencias = request.POST.get('residencias')
        
        comunidade = Comunidade.objects.create(
            nome=nome,
            localizacao=localizacao,
            populacao_estimada=populacao or 0,
            numero_residencias=residencias or 0,
            usuario=request.user
        )
        messages.success(request, f'Comunidade "{nome}" adicionada com sucesso!')
        return redirect('comunidades_list')
    
    return render(request, 'core/adicionar_comunidade.html')

@login_required
def comunidade_detalhe(request, pk):
    """Detalhes de uma comunidade com análises"""
    comunidade = get_object_or_404(Comunidade, pk=pk, usuario=request.user)
    
    # Estatísticas de crimes
    crimes = Crime.objects.filter(comunidade=comunidade)
    total_crimes = crimes.count()
    crimes_por_tipo = crimes.values('tipo').annotate(total=Count('tipo'))
    
    # Estratégias de segurança
    estrategias = EstrategiaSeguranca.objects.filter(comunidade=comunidade)
    
    # Percepção de segurança
    percepcoes = PercepcaoSeguranca.objects.filter(comunidade=comunidade)
    media_seguranca = percepcoes.aggregate(avg=models.Avg('nivel_seguranca'))['avg'] or 0
    
    # Últimos crimes
    ultimos_crimes = crimes.order_by('-data_ocorrencia')[:10]
    
    # Análise de padrões
    analise = analisar_padroes_crime(comunidade)
    
    context = {
        'comunidade': comunidade,
        'total_crimes': total_crimes,
        'crimes_por_tipo': crimes_por_tipo,
        'estrategias': estrategias,
        'percepcoes': percepcoes,
        'media_seguranca': media_seguranca,
        'ultimos_crimes': ultimos_crimes,
        'analise': analise,
    }
    return render(request, 'core/comunidade_detalhe.html', context)

@login_required
def adicionar_crime(request, comunidade_pk):
    """Registar um crime na comunidade"""
    comunidade = get_object_or_404(Comunidade, pk=comunidade_pk, usuario=request.user)
    
    if request.method == 'POST':
        crime = Crime.objects.create(
            comunidade=comunidade,
            tipo=request.POST.get('tipo'),
            descricao=request.POST.get('descricao'),
            data_ocorrencia=request.POST.get('data_ocorrencia'),
            localizacao=request.POST.get('localizacao'),
            vitima=request.POST.get('vitima'),
            suspeito=request.POST.get('suspeito'),
            registado_por=request.user
        )
        messages.success(request, 'Crime registado com sucesso!')
        return redirect('comunidade_detalhe', pk=comunidade.pk)
    
    return render(request, 'core/adicionar_crime.html', {'comunidade': comunidade})

@login_required
def adicionar_estrategia(request, comunidade_pk):
    """Adicionar estratégia de segurança"""
    comunidade = get_object_or_404(Comunidade, pk=comunidade_pk, usuario=request.user)
    
    if request.method == 'POST':
        EstrategiaSeguranca.objects.create(
            comunidade=comunidade,
            tipo=request.POST.get('tipo'),
            descricao=request.POST.get('descricao'),
            data_implementacao=request.POST.get('data_implementacao'),
            usuario=request.user
        )
        messages.success(request, 'Estratégia adicionada com sucesso!')
        return redirect('comunidade_detalhe', pk=comunidade.pk)
    
    return render(request, 'core/adicionar_estrategia.html', {'comunidade': comunidade})

@login_required
def avaliar_seguranca(request, comunidade_pk):
    """Avaliar percepção de segurança"""
    comunidade = get_object_or_404(Comunidade, pk=comunidade_pk, usuario=request.user)
    
    if request.method == 'POST':
        PercepcaoSeguranca.objects.create(
            comunidade=comunidade,
            nivel_seguranca=request.POST.get('nivel_seguranca'),
            principais_medos=request.POST.get('principais_medos'),
            sugestoes=request.POST.get('sugestoes'),
            usuario=request.user
        )
        messages.success(request, 'Avaliação registada com sucesso!')
        return redirect('comunidade_detalhe', pk=comunidade.pk)
    
    return render(request, 'core/avaliar_seguranca.html', {'comunidade': comunidade})

@login_required
def relatorio_comunidade(request, pk):
    """Gerar relatório completo da comunidade"""
    comunidade = get_object_or_404(Comunidade, pk=pk, usuario=request.user)
    
    # Dados para o relatório
    crimes = Crime.objects.filter(comunidade=comunidade)
    estrategias = EstrategiaSeguranca.objects.filter(comunidade=comunidade)
    percepcoes = PercepcaoSeguranca.objects.filter(comunidade=comunidade)
    
    dados = {
        'comunidade': {
            'nome': comunidade.nome,
            'localizacao': comunidade.localizacao,
            'populacao': comunidade.populacao_estimada,
            'residencias': comunidade.numero_residencias,
        },
        'crimes': {
            'total': crimes.count(),
            'por_tipo': crimes.values('tipo').annotate(total=Count('tipo')),
            'ultimos_30_dias': crimes.filter(data_ocorrencia__gte=datetime.now() - timedelta(days=30)).count(),
        },
        'estrategias': {
            'ativas': estrategias.filter(ativa=True).count(),
            'lista': list(estrategias.values('tipo', 'descricao', 'data_implementacao')),
        },
        'percepcao': {
            'media': percepcoes.aggregate(avg=models.Avg('nivel_seguranca'))['avg'] or 0,
            'total_avaliacoes': percepcoes.count(),
        }
    }
    
    # Criar relatório
    relatorio = RelatorioComunidade.objects.create(
        comunidade=comunidade,
        titulo=f"Relatório de Segurança - {comunidade.nome}",
        descricao=f"Relatório gerado automaticamente para a comunidade {comunidade.nome}",
        dados=dados,
        usuario=request.user
    )
    
    return render(request, 'core/relatorio_comunidade.html', {'relatorio': relatorio, 'dados': dados})

# ============================================
# FUNÇÕES DE ANÁLISE
# ============================================

def analisar_padroes_crime(comunidade):
    """Analisa padrões de crimes na comunidade"""
    crimes = Crime.objects.filter(comunidade=comunidade)
    total = crimes.count()
    
    if total == 0:
        return {
            'mensagem': 'Sem dados suficientes para análise.',
            'padroes': []
        }
    
    # Padrão por hora
    padrao_hora = crimes.extra(
        select={'hora': "strftime('%H', data_ocorrencia)"}
    ).values('hora').annotate(total=Count('id')).order_by('-total')
    
    # Padrão por dia da semana
    padrao_semana = crimes.extra(
        select={'dia': "strftime('%w', data_ocorrencia)"}
    ).values('dia').annotate(total=Count('id')).order_by('-total')
    
    # Padrão por tipo
    padrao_tipo = crimes.values('tipo').annotate(total=Count('id')).order_by('-total')
    
    # Análise de tendência
    dias_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
    
    return {
        'total_crimes': total,
        'hora_mais_critica': padrao_hora[0] if padrao_hora else None,
        'dia_mais_critico': dias_semana[int(padrao_semana[0]['dia'])] if padrao_semana else None,
        'tipo_mais_comum': padrao_tipo[0] if padrao_tipo else None,
        'padrao_hora': list(padrao_hora),
        'padrao_semana': list(padrao_semana),
        'padrao_tipo': list(padrao_tipo),
        'nivel_risco': calcular_nivel_risco(total, comunidade.populacao_estimada)
    }

def calcular_nivel_risco(total_crimes, populacao):
    """Calcula o nível de risco baseado no número de crimes por habitante"""
    if populacao == 0:
        return 'Indeterminado'
    
    taxa = total_crimes / populacao * 1000  # Crimes por 1000 habitantes
    
    if taxa < 5:
        return 'Baixo'
    elif taxa < 15:
        return 'Médio'
    elif taxa < 30:
        return 'Alto'
    else:
        return 'Crítico'