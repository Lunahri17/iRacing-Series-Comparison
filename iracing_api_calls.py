import requests


def get_series(token: str = "") -> dict:
    return __fetch_iracing_data(token, "series/seasons?include_series=true")

def get_tracks(token: str = "") -> dict:
    return __fetch_iracing_data(token, "track/get")

def get_member_info(token: str = "") -> dict:
    return __fetch_iracing_data(token, "member/info")

def get_licence_info(token: str = "") -> dict:
    return __fetch_iracing_data(token, "lookup/licenses")

def get_cars(token: str = "") -> dict:
    return __fetch_iracing_data(token, "car/get")

def get_car_class(token: str = "") -> dict:
    return __fetch_iracing_data(token, "carclass/get")


def __fetch_iracing_data(token: str = "", endpoint: str = "") -> dict:
    """
    Obtiene datos de la API de iRacing a partir de un endpoint dado.
    
    Args:
        endpoint (str): Parte final de la URL después de https://members-ng.iracing.com/data/
    
    Returns:
        dict: Datos obtenidos de la API.
    """
    base_url = "https://members-ng.iracing.com/data/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = f"{base_url}{endpoint}"

    raw_response = requests.get(url = url, headers = headers, timeout = 60)
    raw_response.raise_for_status()

    return __request_to_json_link(raw_response.json())


# Aux Functions
def __request_to_json_link(json_response: dict) -> dict:
    """Sigue el enlace 'link' del response para obtener el verdadero contenido JSON"""
    if "link" not in json_response:
        raise ValueError("No se encontró la clave 'link' en la respuesta JSON.")
    return requests.get(json_response["link"], timeout=120).json()
