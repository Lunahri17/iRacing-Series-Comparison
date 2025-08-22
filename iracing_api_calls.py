from base64 import b64encode
from hashlib import sha256
from os import getenv
from dotenv import load_dotenv
import requests

load_dotenv(dotenv_path=".env")

EMAIL = getenv("EMAIL")
PLAIN_PASSWORD = getenv("PASSWORD")

if not EMAIL or not PLAIN_PASSWORD:
    raise ValueError("Faltan variables de entorno EMAIL o PASSWORD")


def get_series(username: str = "", password: str = "") -> dict:
    return __fetch_iracing_data(username, password, "series/seasons?include_series=true")

def get_tracks(username: str = "", password: str = "") -> dict:
    return __fetch_iracing_data(username, password, "track/get")

def get_member_info(username: str = "", password: str = "") -> dict:
    return __fetch_iracing_data(username, password, "member/info")

def get_licence_info(username: str = "", password: str = "") -> dict:
    return __fetch_iracing_data(username, password, "lookup/licenses")

def get_cars(username: str = "", password: str = "") -> dict:
    return __fetch_iracing_data(username, password, "car/get")

def get_car_class(username: str = "", password: str = "") -> dict:
    return __fetch_iracing_data(username, password, "carclass/get")


def __fetch_iracing_data(username: str = "", password: str = "", endpoint: str = "") -> dict:
    """
    Obtiene datos de la API de iRacing a partir de un endpoint dado.
    
    Args:
        endpoint (str): Parte final de la URL después de https://members-ng.iracing.com/data/
    
    Returns:
        dict: Datos obtenidos de la API.
    """
    base_url = "https://members-ng.iracing.com/data/"

    if username == "local" and password == "local&":
        hashed_pw = __hash_password(EMAIL, PLAIN_PASSWORD)
        session = __authenticate(EMAIL, hashed_pw)
    else:
        hashed_pw = __hash_password(username, password)
        session = __authenticate(username, hashed_pw)

    url = f"{base_url}{endpoint}"
    raw_response = session.get(url)
    raw_response.raise_for_status()

    return __request_to_json_link(raw_response.json())


# Aux Functions
def __request_to_json_link(json_response: dict) -> dict:
    """Sigue el enlace 'link' del response para obtener el verdadero contenido JSON"""
    if "link" not in json_response:
        raise ValueError("No se encontró la clave 'link' en la respuesta JSON.")
    return requests.get(json_response["link"], timeout=120).json()

def __hash_password(email: str, password: str) -> str:
    """Genera el hash SHA256 en base64 como requiere iRacing"""
    email = email.lower()
    salted = password + email
    hashed = sha256(salted.encode("utf-8")).digest()
    return b64encode(hashed).decode("utf-8")

def __authenticate(email: str, hashed_password: str) -> requests.Session:
    """Realiza login y devuelve una sesión autenticada"""
    url = "https://members-ng.iracing.com/auth"
    payload = {"email": email, "password": hashed_password}
    session = requests.Session()
    response = session.post(url, json=payload)
    response.raise_for_status()
    return session
