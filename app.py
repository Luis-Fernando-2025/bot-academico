from twilio.rest import Client
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Credenciales de tu cuenta Twilio (cargadas desde .env)
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

# Enviar mensaje
message = client.messages.create(
    from_="whatsapp:+14155238886",  # Número sandbox de Twilio
    body="¡Hola, Luis! Este es tu primer mensaje automático con Twilio y Python.",
    to="whatsapp:+51972552408"  # Tu número de WhatsApp personal
)

print("Mensaje enviado con SID:", message.sid)
