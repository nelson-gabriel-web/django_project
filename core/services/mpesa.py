import json
import base64
import requests
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class MpesaService:
    """
    Serviço de integração com a API M-Pesa Moçambique
    """
    
    def __init__(self):
        self.consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', '')
        self.consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', '')
        self.passkey = getattr(settings, 'MPESA_PASSKEY', '')
        self.shortcode = getattr(settings, 'MPESA_SHORTCODE', '')
        self.callback_url = getattr(settings, 'MPESA_CALLBACK_URL', '')
        self.environment = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')
        
        # URLs da API
        if self.environment == 'production':
            self.base_url = 'https://api.vm.co.mz'
        else:
            self.base_url = 'https://sandbox.vm.co.mz'
        
        self.oauth_url = f"{self.base_url}/v1/token/generate"
        self.stk_push_url = f"{self.base_url}/v1/stkpush"
        self.query_url = f"{self.base_url}/v1/transaction/status"
    
    def get_access_token(self):
        """Obtém o token de acesso OAuth2"""
        try:
            auth = base64.b64encode(
                f"{self.consumer_key}:{self.consumer_secret}".encode()
            ).decode()
            
            headers = {
                'Authorization': f'Basic {auth}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(self.oauth_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('access_token')
            else:
                print(f"Erro ao obter token: {response.text}")
                return None
        except Exception as e:
            print(f"Erro: {e}")
            return None
    
    def stk_push(self, phone_number, amount, reference=None, description=None):
        """
        Inicia um pedido de pagamento STK Push
        
        Args:
            phone_number (str): Número de telefone (ex: 841234567)
            amount (Decimal): Valor a pagar
            reference (str): Referência da transação
            description (str): Descrição do pagamento
        
        Returns:
            dict: Resposta da API
        """
        token = self.get_access_token()
        if not token:
            return {'success': False, 'message': 'Erro ao obter token'}
        
        # Formatar número de telefone
        if phone_number.startswith('0'):
            phone_number = phone_number[1:]
        if not phone_number.startswith('84') and not phone_number.startswith('85'):
            return {'success': False, 'message': 'Número de telefone inválido para M-Pesa'}
        
        # Gerar referência única se não fornecida
        if not reference:
            reference = f"NHONGA-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Dados para STK Push
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{self.shortcode}{self.passkey}{timestamp}".encode()
        ).decode()
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': str(amount),
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': self.callback_url,
            'AccountReference': reference,
            'TransactionDesc': description or 'Pagamento Nhonga'
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(self.stk_push_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'checkout_request_id': data.get('CheckoutRequestID'),
                    'merchant_request_id': data.get('MerchantRequestID'),
                    'response_code': data.get('ResponseCode'),
                    'response_description': data.get('ResponseDescription'),
                    'raw': data
                }
            else:
                return {
                    'success': False,
                    'message': f"Erro: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def query_status(self, checkout_request_id):
        """
        Consulta o status de uma transação
        
        Args:
            checkout_request_id (str): ID da transação M-Pesa
        
        Returns:
            dict: Status da transação
        """
        token = self.get_access_token()
        if not token:
            return {'success': False, 'message': 'Erro ao obter token'}
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            f"{self.shortcode}{self.passkey}{timestamp}".encode()
        ).decode()
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(self.query_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'status': data.get('ResultCode') == '0' and 'success' or 'failed',
                    'result_code': data.get('ResultCode'),
                    'result_description': data.get('ResultDesc'),
                    'raw': data
                }
            else:
                return {
                    'success': False,
                    'message': f"Erro: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {'success': False, 'message': str(e)}