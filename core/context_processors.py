from .models import Moeda

def moedas_context(request):
    return {
        'moedas': Moeda.objects.filter(ativa=True),
        'moeda_atual': Moeda.objects.filter(id=request.session.get('moeda_usuario')).first()
    }