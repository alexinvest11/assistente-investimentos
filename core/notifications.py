import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_aviso(mensagem: str) -> bool:
    """
    Envia um aviso simples para o Telegram.
    Retorna True se enviou com sucesso, False se deu erro.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Token ou Chat ID não configurados.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return False


if __name__ == "__main__":
    sucesso = enviar_aviso("✅ Teste do Assistente de Investimentos\n\nSe você recebeu esta mensagem, o bot está funcionando!")
    if sucesso:
        print("Mensagem enviada com sucesso!")
    else:
        print("Falha ao enviar a mensagem.")
