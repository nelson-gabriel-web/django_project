import requests
from django.conf import settings
from decimal import Decimal

class EmolaService:
    def __init__(self):
        # Credenciais do gateway e2payments
        self.base_url = settings.EMOLA_API_URL
        self.client_id = settings.EMOLA_CLIENT_ID
        self.client_secret = settings.EMOLA_CLIENT_SECRET
        self.wallet_id = settings.EMOLA_WALLET_ID
        
    def _get_token(self):
        """
        Obtém token OAuth2 do gateway
        """
        try:
            response = requests.post(
                f"{self.base_url}/oauth/token",
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'client_credentials'
                }
            )
            if response.status_code == 200:
                return response.json().get('access_token')
            return None
        except Exception as e:
            print(f"Erro ao obter token: {e}")
            return None
    
    def processar_pagamento(self, transacao, phone_number, referencia=None):
        """
        Processa pagamento via E-Mola
        """
        try:
            # Validar número
            if not phone_number.startswith(('86', '87')) or len(phone_number) != 9:
                return {
                    'success': False,
                    'error': 'Número E-Mola inválido. Deve começar com 86 ou 87.'
                }
            
            # Validar valor
            if transacao.valor_total < 1 or transacao.valor_total > 1250000:
                return {
                    'success': False,
                    'error': 'Valor deve ser entre 1 e 1.250.000 MZN'
                }
            
            # Gerar referência
            if not referencia:
                from datetime import datetime
                import random
                referencia = f"EMOLA{datetime.now().strftime('%Y%m%d%H%M')}{random.randint(100, 999)}"
            
            # Obter token
            token = self._get_token()
            if not token:
                return {
                    'success': False,
                    'error': 'Falha na autenticação com o gateway'
                }
            
            # Fazer pagamento
            response = requests.post(
                f"{self.base_url}/v1/c2b/emola-payment/{self.wallet_id}",
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                json={
                    'phone': phone_number,
                    'amount': str(transacao.valor_total),
                    'reference': referencia,
                    'description': f"Pagamento Nhonga - {transacao.titulo[:50]}"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return {
                        'success': True,
                        'reference': referencia,
                        'phone': phone_number,
                        'amount': transacao.valor_total,
                        'response': data
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('message', 'Falha no pagamento'),
                        'response': data
                    }
            else:
                return {
                    'success': False,
                    'error': f'Erro na API: {response.status_code}',
                    'response': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verificar_status(self, reference):
        """
        Verifica o status de um pagamento
        """
        try:
            token = self._get_token()
            if not token:
                return {'success': False, 'error': 'Falha na autenticação'}
            
            response = requests.get(
                f"{self.base_url}/v1/transaction/{reference}",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 200:
                data = response.json()
                status_map = {
                    'completed': 'success',
                    'pending': 'pending',
                    'failed': 'failed'
                }
                return {
                    'success': True,
                    'status': status_map.get(data.get('status'), 'pending'),
                    'data': data
                }
            else:
                return {'success': False, 'error': 'Transação não encontrada'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}