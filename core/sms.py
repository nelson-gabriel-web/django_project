import requests

def enviar_sms(telefone, mensagem):
    """Envia SMS usando Africa's Talking"""
    url = "https://api.africastalking.com/version1/messaging"
    headers = {
        "apiKey": "API_KEY",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": "sandbox",
        "to": telefone,
        "message": mensagem
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()