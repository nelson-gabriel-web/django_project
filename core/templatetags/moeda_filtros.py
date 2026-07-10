from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiplicar(valor, taxa):
    try:
        return Decimal(str(valor)) * Decimal(str(taxa))
    except:
        return valor

@register.filter
def simbolo_moeda(moeda):
    simbolos = {
        'MZN': 'MT',
        'USD': '$',
        'EUR': '€',
        'ZAR': 'R',
    }
    return simbolos.get(moeda, moeda)

@register.filter
def formatar_moeda(valor, moeda_codigo='MZN'):
    try:
        v = Decimal(str(valor))
        simbolos = {
            'MZN': 'MT',
            'USD': '$',
            'EUR': '€',
            'ZAR': 'R',
        }
        simbolo = simbolos.get(moeda_codigo, moeda_codigo)
        return f"{simbolo} {v:,.2f}".replace(',', ' ')
    except:
        return f"{valor}"