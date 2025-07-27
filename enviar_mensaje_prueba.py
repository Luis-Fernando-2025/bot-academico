# enviar_mensaje_prueba.py
import os
import argparse
from dotenv import load_dotenv
from twilio.rest import Client

def enviar_mensaje(to, msg):
    load_dotenv()

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_=from_whatsapp,
        body=msg,
        to=f"whatsapp:{to}"
    )
    print(f"[OK] Mensaje enviado a {to} (SID: {message.sid})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enviar mensaje de prueba por Twilio WhatsApp.")
    parser.add_argument("--to", required=True, help="Número de destino en formato internacional (e.g., +51999999999)")
    parser.add_argument("--msg", default="Hola, este es un mensaje de prueba desde Twilio WhatsApp.", help="Mensaje a enviar.")
    args = parser.parse_args()

    enviar_mensaje(args.to, args.msg)
