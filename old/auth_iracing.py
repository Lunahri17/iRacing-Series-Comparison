
import os
import hashlib
import base64
from dotenv import load_dotenv

# === CARGA VARIABLES DE ENTORNO ===
load_dotenv(dotenv_path=".env")

EMAIL = os.getenv("EMAIL")
PLAIN_PASSWORD = os.getenv("PASSWORD")

def encode_pw(username, password):
    initialHash = hashlib.sha256((password + username.lower()).encode('utf-8')).digest()
    hashInBase64 = base64.b64encode(initialHash).decode('utf-8')

    return hashInBase64

pwValueToSubmit = encode_pw(EMAIL, PLAIN_PASSWORD)

print(f'{EMAIL}\n{pwValueToSubmit}')