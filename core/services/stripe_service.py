import stripe
from django.conf import settings
from decimal import Decimal

class StripeService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
    def criar_pagamento(self, transacao, email_cliente=None):
        """
        Cria um Payment Intent no Stripe para pagamento com cartão VISA
        """
        try:
            # Converter valor para centavos (Stripe trabalha com a menor unidade da moeda)
            valor_centavos = int(transacao.valor_total * 100)
            
            # Criar Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=valor_centavos,
                currency='usd',
                payment_method_types=['card'],
                metadata={
                    'transacao_id': transacao.id,
                    'usuario_id': transacao.cliente.id,
                    'titulo': transacao.titulo[:100]
                },
                receipt_email=email_cliente or transacao.cliente.email,
                description=f"Pagamento Nhonga - {transacao.titulo[:50]}",
                statement_descriptor="NHONGA PAYMENT",
            )
            
            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': intent.amount / 100,
                'status': intent.status
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Erro ao processar pagamento. Tente novamente.'
            }
    
    def confirmar_pagamento(self, payment_intent_id):
        """
        Confirma o status de um pagamento
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            status_map = {
                'succeeded': 'success',
                'requires_payment_method': 'pending',
                'requires_confirmation': 'pending',
                'canceled': 'failed',
                'processing': 'pending',
                'requires_action': 'pending'
            }
            
            return {
                'success': True,
                'status': status_map.get(intent.status, 'pending'),
                'payment_intent': intent,
                'metodo_pagamento': intent.payment_method_types[0] if intent.payment_method_types else 'card',
                'ultimos_4_digitos': intent.payment_method.last4 if hasattr(intent, 'payment_method') and intent.payment_method else None
            }
            
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancelar_pagamento(self, payment_intent_id):
        """
        Cancela um Payment Intent
        """
        try:
            intent = stripe.PaymentIntent.cancel(payment_intent_id)
            return {'success': True, 'status': 'canceled'}
        except stripe.error.StripeError as e:
            return {'success': False, 'error': str(e)}