import os
import django
import requests
import json
from datetime import datetime
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from core.models import Moeda
from decimal import Decimal

print("🔧 Atualização Automática de Taxas de Câmbio")
print("=" * 50)

def obter_taxa_usd():
    """
    Obtém a taxa USD/MZN da API do Banco de Moçambique
    """
    try:
        # URL da API OData
        url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='07-13-2026'&$top=1&$format=json"
        
        # Usar a data atual
        hoje = datetime.now().strftime('%m-%d-%Y')
        url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{hoje}'&$top=1&$format=json"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            
            if dados.get('value') and len(dados['value']) > 0:
                cotacao = dados['value'][0]
                taxa_compra = Decimal(str(cotacao['cotacaoCompra']))
                taxa_venda = Decimal(str(cotacao['cotacaoVenda']))
                data = cotacao['dataHoraCotacao']
                
                print(f"📊 Cotação obtida com sucesso!")
                print(f"   📅 Data: {data}")
                print(f"   💰 Compra: {taxa_compra} MZN/USD")
                print(f"   💰 Venda: {taxa_venda} MZN/USD")
                
                return taxa_compra
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"   {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return None

def atualizar_moeda(codigo, taxa_mzn):
    try:
        moeda = Moeda.objects.get(codigo=codigo)
        moeda.taxa_cambio = taxa_mzn
        moeda.save()
        print(f"✅ {codigo} atualizado: 1 {codigo} = {taxa_mzn} MZN")
        return True
    except Moeda.DoesNotExist:
        print(f"❌ Moeda {codigo} não encontrada")
        return False

print("\n🔄 A obter taxa USD/MZN da API do Banco de Moçambique...")

taxa_usd = obter_taxa_usd()

if taxa_usd is None:
    print("\n❌ Não foi possível obter a taxa automaticamente.")
    print("⚠️  Verifica a ligação à internet e tenta novamente.")
    exit()

print("\n🔄 A atualizar moedas...")
atualizar_moeda('USD', taxa_usd)

# Taxas cruzadas (EUR/USD e ZAR/USD)
taxas_cruzadas = {
    'EUR': Decimal('1.09'),
    'ZAR': Decimal('18.50'),
}

for codigo, fator in taxas_cruzadas.items():
    taxa_mzn = taxa_usd * fator
    atualizar_moeda(codigo, taxa_mzn)

print("\n" + "=" * 50)
print("✅ Atualização concluída com sucesso!")
print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
print("\n📋 Taxas atuais:")
for m in Moeda.objects.filter(ativa=True):
    print(f"   - 1 {m.codigo} = {m.taxa_cambio} MZN")
print("=" * 50)